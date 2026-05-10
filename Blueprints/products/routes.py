from flask import Flask, render_template, request, redirect, session, url_for, flash, Blueprint
from Services.product_service import get_product, save_review, sort_reviews, filter_reviews

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/', methods=['GET'])
def list_products():
    return "Products page"

@products_bp.route('/view_product/<string:sku>', methods=['GET'])
def view_product(sku):
    review_sort = request.args.get('review_sort', 'new')
    review_filter = request.args.get('review_filter', 'all')
    product = get_product(sku, with_imgs=True, with_reviews=True)
    product['reviews'] = filter_reviews(product.get('reviews'), review_filter)
    product['reviews'] = sort_reviews(product.get('reviews', []), review_sort)

    if not product:
        flash('Product not found')
        return redirect(url_for('index.index'))
    return render_template('prod_page.html', product=product, review_sort=review_sort, review_filter=review_filter)

@products_bp.route('/add_review/<string:sku>', methods=['GET'])
def add_review(sku):
    return render_template('review_form.html', sku=sku)

@products_bp.route('/add_review/<string:sku>', methods=['POST'])
def submit_review(sku):
    # IMPORTANT: add check to make sure customer purchased and recieved the product before allowing review submission
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to submit a review')
        return redirect(url_for('authenticate.login_username'))
    try:
        save_review(user_id, sku, rating, comment)
    except Exception as e:
        flash('Error submitting review: ' + str(e), 'error')
        return redirect(url_for('products.view_product', sku=sku))
    flash('Review submitted successfully')
    return redirect(url_for('products.view_product', sku=sku))