import extensions
from flask import url_for
from Modules.Types import *

def get_products(with_imgs = False, with_reviews = False):
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
            product['reviews'] = extensions.client.get_product_reviews(product['sku'])
    return products

