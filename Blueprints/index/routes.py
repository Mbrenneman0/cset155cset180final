from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from Services.product_service import get_products

index_bp = Blueprint('index',__name__, url_prefix='/')

@index_bp.route('/', methods=['GET'])
def index():
    products = get_products(with_imgs=True, with_rating=True)
    return render_template('index.html', products=products)

