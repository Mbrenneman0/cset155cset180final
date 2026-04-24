from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from Services.auth_service import parse_login_inputs, parse_register_inputs, create_user, create_session

auth_bp = Blueprint('authenticate', __name__, url_prefix='/authenticate')

@auth_bp.route('/login/username', methods=['GET','POST'])
def login_username():
    input_types = ['Username','Password']
    if request.method == 'POST':
        inputs = parse_login_inputs(request.form)
        if len(inputs) != len(input_types):
            return render_template('base_auth.html', title='Login', inputs=input_types, saved_inputs=inputs, log_type='Sign in with email instead? Click here!')
        return redirect(url_for('index.index'))
    else:
        return render_template('base_auth.html', title='Login', inputs=input_types, log_type='Sign in with email instead? Click here!')
    
@auth_bp.route('/login/email', methods=['GET','POST'])
def login_email():
    input_types = ['Email','Password']
    if request.method == 'POST':
        inputs = parse_login_inputs(request.form)
        if len(inputs) != len(input_types):
            return render_template('base_auth.html', title='Login', inputs=input_types, saved_inputs=inputs, log_type='Sign in with username instead? Click here!')
        return redirect(url_for('index.index'))
    else:
        return render_template('base_auth.html', title='Login', inputs=input_types, log_type='Sign in with username instead? Click here!')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    input_types = ['Name','Username','Email','Password']
    if request.method == 'POST':
        inputs = parse_register_inputs(request.form)
        if len(inputs) != len(input_types):
            return render_template('base_auth.html', title='Register', inputs=input_types, saved_inputs=inputs)
        # create_user(inputs)
        return redirect(url_for('index.index'))
    else:
        
        return render_template('base_auth.html', title='Register', inputs=input_types)

@auth_bp.route('/register/vender', methods=['GET','POST'])
def vender_register():
    input_types = ['Name','Username','Email','Password']
    if request.method == 'POST':
        inputs = parse_register_inputs(request.form)
        if len(inputs) != 0:
            return render_template('base_auth.html', title='Register', inputs=input_types, saved_inputs=inputs)
        # create_user(inputs)
        return redirect(url_for('index.index'))
    else:
        
        return render_template('base_auth.html', title='Register', inputs=input_types)