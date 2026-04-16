from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

auth_bp = Blueprint('authenticate', __name__, url_prefix='/authenticate')

@auth_bp.route('/login')
def login():
    return

@auth_bp.route('/logout')
def logout():
    return

@auth_bp.route('/register')
def register():
    return

@auth_bp.route('/vender/register')
def vender_register():
    return