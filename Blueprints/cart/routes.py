from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

cart_bp = Blueprint('cart',__name__,url_prefix='/cart')

@cart_bp.route('/')
def view_cart():
    return

@cart_bp.route('/add')
def add_item():
    return

@cart_bp.route('/remove')
def remove_item():
    return