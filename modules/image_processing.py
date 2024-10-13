import logging
import os

import pandas as pd
import requests
import imghdr

from config.settings import BASE_IMAGE_URL

def process_image_urls(image_paths, product_id):
    if pd.isna(image_paths) or image_paths.strip() == '':
        logging.info(f"Producto ID {product_id} no tiene imágenes.")
        return ''
    image_paths_list = [path.strip() for path in image_paths.split(',') if path.strip()]
    processed_image_urls = []
    for image_path in image_paths_list:
        image_url = process_single_image_url(image_path, product_id)
        if image_url:
            processed_image_urls.append(image_url)
    return ', '.join(processed_image_urls)

def process_single_image_url(image_path, product_id):
    image_path = image_path.lstrip('/')
    parts = image_path.split('/')
    if len(parts) != 2:
        logging.warning(f"Formato inesperado de imagen para el producto ID {product_id}: '{image_path}'")
        return ''
    domain_id, image_filename = parts
    image_name, ext = os.path.splitext(image_filename)
    if len(image_name) < 3:
        logging.warning(f"Nombre de imagen inválido para el producto ID {product_id}: '{image_filename}'")
        return ''
    first_three_chars = image_name[:3]
    first_char = first_three_chars[0]
    next_two_chars = first_three_chars[1:]

    sizes = ['_900', '_150', '_100', '_75']
    for size_suffix in sizes:
        new_image_name = f"{image_name}{size_suffix}{ext}"
        image_url = f"{BASE_IMAGE_URL}/Content/products/{domain_id}/{first_char}/{next_two_chars}/{new_image_name}"
        try:
            headers = {'Range': 'bytes=0-1023'}  # Descargar solo los primeros bytes
            response = requests.get(image_url, headers=headers, timeout=5)
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type.lower() or imghdr.what(None, h=response.content):
                return image_url
        except requests.RequestException as e:
            logging.debug(f"Error al verificar la imagen para el producto ID {product_id}: {e}")
            continue
    logging.warning(f"No se encontró imagen disponible para el producto ID {product_id} con la ruta '{image_path}'.")
    return ''
