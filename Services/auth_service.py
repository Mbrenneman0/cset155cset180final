from flask import flash, session
import extensions
from Modules.Types import *

def _does_input_exist(col:str, value:str) -> bool:
    rslt = extensions.client.conn.get_rows(TableNames.USERS, condition=f'{col}=\"{value}\"')
    return True if len(rslt) != 0 else False

def check_credentials(role_type:str, user_id:str=session['user_id']) -> bool:
    check = True
    if not _does_input_exist('user_id', user_id):
        check = False
        raise KeyError(f'User ID not found at: {session['user_id']}')
    if session['role'] != role_type:
        check = False
        raise KeyError(f'User at user_id :{session['user_id']}, does not have {role_type} access')
    return check

def parse_login_inputs(form_inputs) -> dict:
    inputs = dict(form_inputs)
    for key, value in inputs.items():
        if value.isspace():
            flash(f'Invalid {key} input. Please try again.')
            inputs[key] = None
        if _does_input_exist(key, value):
            flash(f'{key.capitalize()} value already in use. Please try again.')
            inputs[key] = None
    return inputs

def parse_register_inputs(form_inputs) -> dict:
    inputs = dict(form_inputs)
    for key, value in inputs.items():
        if value.isspace():
            flash(f'Invalid {key} input. Please try again.')
            inputs[key] = None
        if not _does_input_exist(key, value):
            flash(f'{key.capitalize()} value not in use. Please try again.')
            inputs[key] = None
    return inputs

def create_user(form_inputs):
    rslt = extensions.client.conn.create_row(TableNames.USERS, form_inputs)
    create_session(rslt['user_id'], rslt['role'])

def create_session(user_id:str=None, role:str=None):
    session['user_id'] = user_id
    session['role'] = role