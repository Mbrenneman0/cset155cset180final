import os
import extensions
from flask import Flask, current_app, url_for, request
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

def update_product(
    form: ImmutableMultiDict[str, str],
    new_images: list[FileStorage] = None,
    delete_images: list[str] = None):

    sku = form.get('sku')
    product = extensions.client.product(sku)

    data = ProductUpdate(
        qty=int(form.get('qty')),
        title=form.get('title'),
        color=form.get('color'),
        size=form.get('size'),
        description=form.get('description'),
        unit_price=float(form.get('unit_price')),
        warranty_period=form.get('warranty_period'),
        is_removed=form.get('is_removed') == 'True'
    )

    product.update(data)

    delete_images = delete_images or []
    new_images = new_images or []

    current_images = product.get_images()

    if delete_images:
        delete_product_images(sku, delete_images, current_images)

    for image in new_images:
        if image and image.filename:
            save_product_image(sku, image)

def get_vendor_img_folder(sku: str) -> tuple[str, str]:
    product = extensions.client.product(sku)
    vendor_id = product.get_info()['vendor_id']
    vendor = extensions.client.vendor(vendor_id)
    vendor_name = vendor.get_info()['username']

    relative_folder = os.path.join("images", "prod-imgs", vendor_name)

    absolute_folder = os.path.join(
        current_app.root_path,
        "Static",
        relative_folder
    )

    os.makedirs(absolute_folder, exist_ok=True)

    return relative_folder, absolute_folder

def get_next_image_number(sku: str) -> int:
    images = extensions.client.product(sku).get_images()

    used_numbers = []

    for image in images:
        img_url = image['img_url']
        filename = os.path.basename(img_url)

        name_without_ext = os.path.splitext(filename)[0]

        try:
            number_part = name_without_ext.split('-')[-1]
            used_numbers.append(int(number_part))
        except ValueError:
            pass

    if not used_numbers:
        return 1

    return max(used_numbers) + 1

def save_product_image(sku: str, image: FileStorage):
    relative_folder, absolute_folder = get_vendor_img_folder(sku)

    image_number = get_next_image_number(sku)
    filename = f"{sku}-{image_number}.png"

    save_path = os.path.join(absolute_folder, filename)
    image.save(save_path)

    img_url = os.path.join(relative_folder, filename).replace("\\", "/")

    extensions.client.conn.create_row(
        TableNames.PROD_IMGS,
        {
            "sku": sku,
            "img_url": img_url
        }
    )

def delete_product_images(sku: str, delete_images: list[str], current_images: list[ProductImageRow]):
    current_urls = [image['img_url'] for image in current_images]

    # Only allow deleting images that actually belong to this product
    delete_images = [img for img in delete_images if img in current_urls]

    if len(current_urls) - len(delete_images) < 1:
        raise ValueError("A product must have at least one image.")

    for img_url in delete_images:
        delete_product_image_row(img_url)
        delete_product_image_file(img_url)

def delete_product_image_row(img_url: str):
    rslt = extensions.client.conn.get_rows(TableNames.PROD_IMGS,
                                        condition = 'img_url=:img_url',
                                        params={'img_url': img_url})
    img_index = rslt[0].get('img_index')
    extensions.client.conn.delete_row(TableNames.PROD_IMGS, img_index)

def delete_product_image_file(img_url: str):
    file_path = os.path.join(
        current_app.root_path,
        "Static",
        img_url
    )

    if os.path.exists(file_path):
        os.remove(file_path)

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