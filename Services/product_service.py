import extensions
from flask import Flask, url_for, request
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from Modules.Types import *

def get_products(with_imgs = False, with_reviews = False, with_rating = False):
    products = extensions.client.get_all_products()
    if with_imgs:
        for product in products:
            try:
                images = extensions.client.product(product['sku']).get_images()
                product['images'] = images
            except Exception as e:
                product['images'] = []
    if with_reviews:
        for product in products:
            product['reviews'] = extensions.client.product(product['sku']).get_reviews()
    if with_rating:
        for product in products:
            product['rating'] = get_rating(product['sku'])
    return products

def get_product(sku, with_imgs = False, with_reviews = False, with_rating = False):
    product = extensions.client.product(sku).get_info()
    if with_imgs:
        try:
            images = extensions.client.product(sku).get_images()
            product['images'] = images
        except Exception as e:
            product['images'] = []
    if with_reviews:
        product['reviews'] = extensions.client.product(sku).get_reviews()
    if with_rating:
        product['rating'] = get_rating(sku)
    return product

def update_product(form:ImmutableMultiDict[str, str], image:FileStorage=None):
    sku = form.get('sku')
    product = extensions.client.product(sku)
    data = ProductUpdate(qty = int(form.get('qty')),
                        title = form.get('title'),
                        color = form.get('color'),
                        size = form.get('size'),
                        description = form.get('description'),
                        unit_price = float(form.get('unit_price')),
                        warranty_period = form.get('warranty_period'),
                        is_removed = form.get('is_removed')=='True'
                        )
    product.update(data)
    

def get_rating(sku):
    reviews = extensions.client.product(sku).get_reviews()
    if not reviews:
        return None
    total_rating = sum(review['rating'] for review in reviews)
    return round(total_rating / len(reviews), 1)

def save_review(user_id, sku, rating, comment):
    try:
        extensions.client.customer(user_id).create_review(sku, int(rating), comment)
    except Exception as e:
        if "duplicate entry" in str(e).lower():
            raise Exception("You have already submitted a review for this product")
        else:
            raise