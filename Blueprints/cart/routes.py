from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

cart_bp = Blueprint('cart',__name__,url_prefix='/cart')

@cart_bp.route('/', methods=['GET'])
def view_cart():
    return

@cart_bp.route('/add', methods=['POST'])
def add_item():
    return

@cart_bp.route('/remove', methods=['POST'])
def remove_item():
    return