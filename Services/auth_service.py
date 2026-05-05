from flask import flash, session, request, render_template, redirect, url_for
import extensions
from Modules.Types import TableNames, Role
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def _does_input_exist(col: str, value) -> bool:
    rslt = extensions.client.conn.get_rows(TableNames.USERS, condition=f"{col} = :value", params={'value': value})
    return len(rslt) != 0

def _parse_login_inputs(form_inputs) -> dict:
    inputs = {key: value.strip() if isinstance(value, str) else value for key, value in form_inputs.items()}
    if not inputs.get('username') and not inputs.get('email'):
        flash('Please provide a username or email.')
        inputs['username'] = inputs.get('username')
        inputs['email'] = inputs.get('email')
    if not inputs.get('password'):
        flash('Password is required.')
        inputs['password'] = None
    return inputs

def _parse_register_inputs(form_inputs) -> dict:
    inputs = {key: value.strip() if isinstance(value, str) else value for key, value in form_inputs.items()}
    for key in ['name', 'username', 'email', 'password']:
        if not inputs.get(key):
            flash(f'Invalid {key} input. Please try again.')
            inputs[key] = None

    if inputs.get('username') and _does_input_exist('username', inputs['username']):
        flash('Username is already in use. Please choose another.')
        inputs['username'] = None
    if inputs.get('email') and _does_input_exist('email', inputs['email']):
        flash('Email is already in use. Please choose another.')
        inputs['email'] = None
    return inputs

def _create_user(form_inputs):
    form_inputs['password'] = ph.hash(form_inputs['password'])
    extensions.client.conn.create_row(TableNames.USERS, form_inputs)
    user = _find_user_for_login(form_inputs)
    if user:
        create_session(user['user_id'], user['role'])

def _find_user_for_login(inputs: dict) -> dict | None:
    if inputs.get('username'):
        rows = extensions.client.conn.get_rows(TableNames.USERS, condition='username = :value', params={'value': inputs['username']})
    elif inputs.get('email'):
        rows = extensions.client.conn.get_rows(TableNames.USERS, condition='email = :value', params={'value': inputs['email']})
    else:
        return None
    return rows[0] if rows else None


def route_controller(action: str, input_types: list, log_type: str = None, role: Role = Role.CUSTOMER):
    if request.method == 'POST':
        if action == 'login':
            inputs = _parse_login_inputs(request.form)
        elif action == 'register':
            inputs = _parse_register_inputs(request.form)
            inputs['role'] = role.value if isinstance(role, Role) else role
        else:
            raise ValueError("Invalid action. Must be 'login' or 'register'.")
        if any(value is None for value in inputs.values()):
            return render_template('base_auth.html', title=action.capitalize(), inputs=input_types, saved_inputs=inputs, log_type=log_type)
        if action == 'login':
            user = _find_user_for_login(inputs)
            if not user:
                flash('Invalid credentials. Please try again.')
                return render_template('base_auth.html', title='Login', inputs=input_types, saved_inputs=inputs, log_type=log_type)

            try:
                if ph.verify(user['password'], inputs['password']):
                    create_session(user['user_id'], user['role'])
                    if role != Role.CUSTOMER:
                        return # TODO: redirect to vender/admin page when made
                    return redirect(url_for('index.index'))
            except VerifyMismatchError:
                pass

            flash('Invalid credentials. Please try again.')
            return render_template('base_auth.html', title='Login', inputs=input_types, saved_inputs=inputs, log_type=log_type)

        if action == 'register':
            _create_user(inputs)
            if role != Role.CUSTOMER:
                return # TODO: redirect to vender/admin page when made
            return redirect(url_for('index.index'))

    return render_template('base_auth.html', title=action.capitalize(), inputs=input_types, log_type=log_type)
            
def check_credentials(role_type:Role, user_id:int=None) -> bool:
    check = True
    if user_id is None:
        user_id = session['user_id']
    if not _does_input_exist('user_id', user_id):
        check = False
        print(KeyError(f'User ID not found at: {session['user_id']}'))
    if session['role'] != role_type:
        check = False
        print(KeyError(f'User {session['user_id']} does not have {role_type.value} access'))
    return check

def create_session(user_id:str=None, role:str=None):
    session['user_id'] = user_id
    session['role'] = role