from flask import redirect, url_for, Blueprint, session
from Services.auth_service import *

auth_bp = Blueprint('authenticate', __name__, url_prefix='/authenticate')

@auth_bp.route('/login/username', methods=['GET','POST'])
def login_username():
    return route_controller('login', ['Username', 'Password'], 'Sign in with email instead? Click here!')

@auth_bp.route('/login/email', methods=['GET','POST'])
def login_email():
    return route_controller('login', ['Email', 'Password'], 'Sign in with username instead? Click here!')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index.index'))

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    return route_controller('register', ['Name', 'Username', 'Email', 'Password'])

@auth_bp.route('/register/vender', methods=['GET','POST'])
def vender_register():
    return route_controller('register', ['Name', 'Username', 'Email', 'Password'], role=VENDER)