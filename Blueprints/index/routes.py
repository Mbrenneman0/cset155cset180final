from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from Services.product_service import get_products
from Modules.Types import *

index_bp = Blueprint('index',__name__, url_prefix='/')

@index_bp.route('/', methods=['GET'])
def index():
    category_value = request.args.get('category','').strip()
    selected_category = None

    if category_value:
        try:
            selected_category = ProdCategories(category_value)
        except:
            flash("Invalid category selected.", "error")
            return redirect(url_for(index.index))
        
        
    products = get_products(with_imgs=True, with_rating=True, category=selected_category)

    return render_template('index.html',
                           products=products,
                           categories=ProdCategories,
                           selected_category=category_value)

