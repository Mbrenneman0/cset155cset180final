from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

auth_bp = Blueprint('authenticate', __name__, url_prefix='/authenticate')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    return

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    return

@auth_bp.route('/vender/register', methods=['GET','POST'])
def vender_register():
    return