from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

index_bp = Blueprint('index',__name__, url_prefix='/')

@index_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

