import os
import extensions
from flask import Flask, current_app, url_for, request
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from Modules.Types import *
import re
from difflib import SequenceMatcher

def _clean_search_text(value) -> str:
    value = str(value or "").lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def _product_search_score(product, search: str) -> float:
    query = _clean_search_text(search)

    if not query:
        return 1.0

    title = _clean_search_text(product.get("title", ""))
    description = _clean_search_text(product.get("description", ""))
    searchable_text = f"{title} {description}".strip()

    if not searchable_text:
        return 0.0

    if query in title:
        return 1.0

    if query in description:
        return 0.9
    title_score = SequenceMatcher(None, query, title).ratio()
    desc_score = SequenceMatcher(None, query, description).ratio()
    query_words = query.split()
    product_words = searchable_text.split()

    word_scores = []
    for query_word in query_words:
        best_word_score = max(
            SequenceMatcher(None, query_word, product_word).ratio()
            for product_word in product_words
        )
        word_scores.append(best_word_score)

    token_score = sum(word_scores) / len(word_scores) if word_scores else 0
    return max(title_score, desc_score, token_score)

def _fuzzy_filter_products(products, search: str, threshold: float = 0.55):
    if not search:
        return products

    scored_products = []
    for product in products:
        score = _product_search_score(product, search)
        if score >= threshold:
            scored_products.append((score, product))

    scored_products.sort(key=lambda item: item[0], reverse=True)
    return [product for score, product in scored_products]

def get_products(with_imgs = False,
                 with_reviews = False,
                 with_rating = False,
                 category:ProdCategories = None,
                 search:str = None):
    products = extensions.client.get_all_products()
    if category:
        products = [product for product in products
                    if product.get('category') == category.value]
        
    products = _fuzzy_filter_products(products, search)
    
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
        for review in product['reviews']:
            username = extensions.client.user(review.get('user_id')).get_info().get('name')
            review.update(username=username)
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
        category=form.get('category'),
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


def add_new_product(
    form: ImmutableMultiDict[str, str],
    image: FileStorage = None):

    sku = form.get('sku')
    vendor_id = int(form.get('vendor_id'))

    data = NewProduct(
        sku=sku,
        qty=int(form.get('qty')),
        title=form.get('title'),
        category=form.get('category'),
        color=form.get('color'),
        size=form.get('size'),
        description=form.get('description'),
        unit_price=float(form.get('unit_price')),
        warranty_period=form.get('warranty_period'),
        is_removed=form.get('is_removed') == 'True'
    )

    extensions.client.vendor(vendor_id).create_product(data)
    if image and image.filename:
        save_product_image(sku, image)

def new_sku() -> str:
    skus = [item['sku'] for item in extensions.client.get_all_products()]
    sku_nums = []

    for sku_str in skus:
        match = re.search(r"\d+", sku_str)
        if match:
            sku_nums.append(int(match.group(0)))

    new_num = max(sku_nums, default=0) + 1
    return f'SKU{new_num:03d}'

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

def filter_reviews(reviews:list[ReviewRow], filter):
    if filter == 'one':
        reviews = [review for review in reviews if review['rating'] == 1]
    elif filter == 'two':
        reviews = [review for review in reviews if review['rating'] == 2]
    elif filter == 'three':
        reviews = [review for review in reviews if review['rating'] == 3]
    elif filter == 'four':
        reviews = [review for review in reviews if review['rating'] == 4]
    elif filter == 'five':
        reviews = [review for review in reviews if review['rating'] == 5]
    return reviews

def sort_reviews(reviews, sort):
    if sort == 'old':
        reviews.sort(key=lambda review: review['rvw_time'])
    elif sort == 'high':
        reviews.sort(key=lambda review: review['rating'], reverse=True)
    elif sort == 'low':
        reviews.sort(key=lambda review: review['rating'])
    else:
        sort = 'new'
        reviews.sort(key=lambda review: review['rvw_time'], reverse=True)

    return reviews