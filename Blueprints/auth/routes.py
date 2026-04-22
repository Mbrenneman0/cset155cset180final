from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

auth_bp = Blueprint('authenticate', __name__, url_prefix='/authenticate')

@auth_bp.route('/login/username', methods=['GET','POST'])
def login_username():
    if request.method == 'POST':
        return
    else:
        inputs = ['Username','Password']
        return render_template('base_auth.html', title='Login', inputs=inputs, log_type='Sign in with email instead? Click here!')
    
@auth_bp.route('/login/email', methods=['GET','POST'])
def login_email():
    if request.method == 'POST':
        return
    else:
        inputs = ['Email','Password']
        return render_template('base_auth.html', title='Login', inputs=inputs, log_type='Sign in with username instead? Click here!')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        return
    else:
        inputs = ['Name','Username','Email','Password']
        return render_template('base_auth.html', title='Register', inputs=inputs)

@auth_bp.route('/vender/register', methods=['GET','POST'])
def vender_register():
    if request.method == 'POST':
        return
    else:
        inputs = ['Name','Username','Email','Password']
        return render_template('base_auth.html', title='Register', inputs=inputs)