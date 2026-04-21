from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

main_bp = Blueprint('main',__name__)

@main_bp.route('/')
def index():
    return redirect(url_for('authenticate.login'))