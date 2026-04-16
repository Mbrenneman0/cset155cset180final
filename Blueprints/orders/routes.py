from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
# from Services."folder" import 'funcs_needed'

orders_bp = Blueprint('orders',__name__, url_prefix='/orders')

@orders_bp.route('/checkout')
def checkout():
    return

@orders_bp.route('/<int:id>')
def view_order(id):
    return