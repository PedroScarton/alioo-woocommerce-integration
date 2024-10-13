# modules/excel_processing.py

import pandas as pd
import os
import requests
import logging
import imghdr

def process_excel(input_path, output_path):
    """
    Procesa el archivo Excel descargado y lo convierte al formato necesario para WooCommerce,
    manejando productos variables y sus variaciones.
    """
    try:
        # Leer el Excel
        df = pd.read_excel(input_path, engine='openpyxl')
        logging.info(f"Archivo Excel '{input_path}' leído correctamente.")
    except Exception as e:
        logging.error(f"Error al leer el archivo Excel '{input_path}': {e}")
        return

    # Seleccionar las columnas necesarias
    selected_columns = [
        'Id',
        'Producto',
        'Precio',
        'SKU',
        'Ruta Categorías',
        'Marca',
        'Modelo',
        'Tamaños',
        'Colores',
        'Etiquetas',
        'Imagenes Ailoo',
        'Stock:Mundo Bikes'
    ]

    # Verificar si todas las columnas necesarias están presentes
    missing_columns = set(selected_columns) - set(df.columns)
    if missing_columns:
        logging.error(f"Columnas faltantes en el Excel: {missing_columns}")
        return

    df = df[selected_columns]

    # Procesar la ruta de categorías
    def process_categories(row):
        try:
            categories = row['Ruta Categorías'].split('/')
            categories = [cat.strip() for cat in categories if cat.strip()]
            return categories
        except Exception as e:
            logging.warning(f"Error al procesar categorías para el producto ID {row['Id']}: {e}")
            return []

    df['Categorías'] = df.apply(process_categories, axis=1)

    # Crear columnas para los atributos
    df['pa_marca'] = df['Marca']
    df['pa_modelo'] = df['Modelo']
    df['pa_tamano'] = df['Tamaños']
    df['pa_color'] = df['Colores']

    # Procesar las URLs de las imágenes
    BASE_IMAGE_URL = 'http://mundobikes.ailoo.cl'

    def process_image_urls(image_paths, product_id):
        if pd.isna(image_paths) or image_paths.strip() == '':
            logging.info(f"Producto ID {product_id} no tiene imagenes.")
            return ''
        # Dividir las rutas de imágenes por coma
        image_paths_list = [path.strip() for path in image_paths.split(',') if path.strip()]
        processed_image_urls = []
        for image_path in image_paths_list:
            # Procesar cada ruta de imagen individualmente
            image_url = process_single_image_url(image_path, product_id)
            if image_url:
                processed_image_urls.append(image_url)
        # Combinar las URLs de imágenes procesadas en una cadena separada por comas
        return ', '.join(processed_image_urls)

    def process_single_image_url(image_path, product_id):
        # Eliminar el '/' inicial si existe
        image_path = image_path.lstrip('/')
        # Dividir la ruta en partes
        parts = image_path.split('/')
        if len(parts) != 2:
            logging.warning(f"Formato inesperado de imagen para el producto ID {product_id}: '{image_path}'")
            return ''
        domain_id = parts[0]
        image_filename = parts[1]
        # Extraer el nombre del archivo y la extensión
        image_name, ext = os.path.splitext(image_filename)
        if len(image_name) < 3:
            logging.warning(f"Nombre de imagen inválido para el producto ID {product_id}: '{image_filename}'")
            return ''
        # Obtener los primeros tres caracteres
        first_three_chars = image_name[:3]
        first_char = first_three_chars[0]
        next_two_chars = first_three_chars[1:]

        # Lista de tamaños a probar
        sizes = ['_900', '_150', '_75', '']  # El último intento sin sufijo de tamaño
        for size_suffix in sizes:
            new_image_name = f"{image_name}{size_suffix}{ext}"
            image_url = f"{BASE_IMAGE_URL}/Content/products/{domain_id}/{first_char}/{next_two_chars}/{new_image_name}"
            try:
                headers = {
                    'Range': 'bytes=0-1023'  # Descargar solo los primeros 1024 bytes
                }
                response = requests.get(image_url, headers=headers, timeout=5)
                content_type = response.headers.get('Content-Type', '')
                if 'image' in content_type.lower():
                    return image_url
                else:
                    # Verificar los primeros bytes del contenido
                    image_type = imghdr.what(None, h=response.content)
                    if image_type:
                        return image_url
                    else:
                        logging.debug(f"Contenido no es una imagen para el producto ID {product_id}, URL: {image_url}")
            except requests.RequestException as e:
                logging.debug(f"Error al verificar la imagen para el producto ID {product_id}: {e}")
                continue  # Intentar con el siguiente tamaño
        # Si ninguna imagen está disponible, registrar advertencia
        logging.warning(f"No se encontró imagen disponible para el producto ID {product_id} con la ruta '{image_path}'.")
        return ''  # O retornar la URL de una imagen predeterminada

    df['Images'] = df.apply(lambda row: process_image_urls(row['Imagenes Ailoo'], row['Id']), axis=1)

    # Renombrar y asegurar que el stock es un entero
    df['stock'] = df['Stock:Mundo Bikes'].fillna(0).astype(int)
    df['In stock?'] = df['stock'].apply(lambda x: 1 if x > 0 else 0)

    # Agrupar productos por ID
    grouped = df.groupby('Id')

    # Lista para almacenar las filas finales
    final_rows = []

    for product_id, group in grouped:
        try:
            if len(group) == 1:
                # Producto simple
                row = create_simple_product_row(group.iloc[0])
                final_rows.append(row)
            else:
                # Producto variable
                # Crear fila del producto principal
                parent_row = create_variable_product_row(group)
                final_rows.append(parent_row)
                # Crear filas para cada variación
                variation_rows = create_variation_rows(group, parent_row['ID'])
                final_rows.extend(variation_rows)
        except Exception as e:
            logging.error(f"Error al procesar el producto ID {product_id}: {e}")
            continue  # Omitir este producto y continuar con el siguiente

    # Crear DataFrame final
    wc_df = pd.DataFrame(final_rows)

    # Guardar el DataFrame en un archivo CSV
    try:
        wc_df.to_csv(output_path, index=False, encoding='utf-8')
        logging.info(f"Archivo procesado y guardado en '{output_path}'.")
    except Exception as e:
        logging.error(f"Error al guardar el archivo '{output_path}': {e}")

def create_simple_product_row(row):
    # Crear una fila para un producto simple
    wc_row = {
        'ID': row['Id'],
        'Type': 'simple',
        'SKU': row['SKU'],
        'Name': row['Producto'],
        'Published': 1,
        'Is featured?': 0,
        'Visibility in catalog': 'visible',  # Valor válido
        'Short description': '',
        'Description': '',
        'Tax status': 'taxable',
        'Tax class': '',
        'In stock?': row['In stock?'],
        'Stock': row['Stock:Mundo Bikes'],
        'Backorders allowed?': 0,
        'Sold individually?': 0,
        'Regular price': row['Precio'],
        'Sale price': '',
        'Categories': format_category(row['Categoría Padre'], row['Categoria Primaria']),
        'Tags': row['Etiquetas'],
        'Images': row['Images'],
        'Attribute 1 name': 'Marca',
        'Attribute 1 value(s)': row['pa_marca'],
        'Attribute 1 visible': 1,
        'Attribute 1 global': 1,
        'Attribute 2 name': 'Modelo',
        'Attribute 2 value(s)': row['pa_modelo'],
        'Attribute 2 visible': 1,
        'Attribute 2 global': 1,
        'Attribute 3 name': 'Tamaño',
        'Attribute 3 value(s)': row['pa_tamano'],
        'Attribute 3 visible': 1,
        'Attribute 3 global': 1,
        'Attribute 4 name': 'Color',
        'Attribute 4 value(s)': row['pa_color'],
        'Attribute 4 visible': 1,
        'Attribute 4 global': 1,
    }
    return wc_row

def create_variable_product_row(group):
    # Crear una fila para el producto variable
    row = group.iloc[0]
    wc_row = {
        'ID': row['Id'],
        'Type': 'variable',
        'SKU': row['SKU'],
        'Name': row['Producto'],
        'Published': 1,
        'Is featured?': 0,
        'Visibility in catalog': 'visible',  # Valor válido
        'Short description': '',
        'Description': '',
        'Tax status': 'taxable',
        'Tax class': '',
        # Las siguientes columnas no se usan en el producto variable
        'In stock?': '',
        'Stock': '',
        'Backorders allowed?': '',
        'Sold individually?': 0,
        'Regular price': '',
        'Sale price': '',
        'Categories': format_category(row['Categoría Padre'], row['Categoria Primaria']),
        'Tags': row['Etiquetas'],
        'Images': row['Images'],
    }

    # Definir los atributos y sus valores posibles
    attributes = ['pa_marca', 'pa_modelo', 'pa_tamano', 'pa_color']
    attribute_index = 1
    for attr in attributes:
        values = group[attr].dropna().astype(str).unique()
        values = [v for v in values if v != '']
        if len(values) > 0:
            wc_row[f'Attribute {attribute_index} name'] = attr.replace('pa_', '').capitalize()
            wc_row[f'Attribute {attribute_index} value(s)'] = ', '.join(values)
            wc_row[f'Attribute {attribute_index} visible'] = 1
            wc_row[f'Attribute {attribute_index} global'] = 1
            attribute_index += 1
    return wc_row

def create_variation_rows(group, parent_id):
    # Crear filas para cada variación
    variation_rows = []
    for _, row in group.iterrows():
        try:
            wc_row = {
                'ID': '',
                'Type': 'variation',
                'SKU': row['SKU'],
                'Name': '',
                'Published': 1,
                'Is featured?': '',
                'Visibility in catalog': 'visible',
                'Short description': '',
                'Description': '',
                'Tax status': '',
                'Tax class': '',
                'In stock?': row['In stock?'],
                'Stock': row['Stock:Mundo Bikes'],
                'Backorders allowed?': 0,
                'Sold individually?': '',
                'Regular price': row['Precio'],
                'Sale price': '',
                'Categories': '',
                'Tags': '',
                'Images': row['Images'],
                'Parent': parent_id,
            }
            # Añadir los atributos con sus valores específicos
            attributes = ['pa_marca', 'pa_modelo', 'pa_tamano', 'pa_color']
            attribute_index = 1
            for attr in attributes:
                value = row[attr]
                if pd.notna(value) and value != '':
                    wc_row[f'Attribute {attribute_index} name'] = attr.replace('pa_', '').capitalize()
                    wc_row[f'Attribute {attribute_index} value(s)'] = value
                    attribute_index += 1
            variation_rows.append(wc_row)
        except Exception as e:
            logging.error(f"Error al crear la variación para el producto ID {parent_id}: {e}")
            continue  # Omitir esta variación y continuar con las siguientes
    return variation_rows


def format_category(categoria_padre, categoria_primaria):
    # Verificar si existe la categoría padre
    if categoria_padre:
        formatted_category = categoria_padre.strip()
    else:
        formatted_category = ""

    # Verificar si existe la categoría primaria
    if categoria_primaria:
        categorias_primarias = [cat.strip() for cat in categoria_primaria.split(',')]  # Separar por coma y quitar espacios
        if formatted_category:
            # Si hay categoría padre, agregar '>' y luego las categorías primarias unidas
            formatted_category += " > " + " > ".join(categorias_primarias)
        else:
            # Si no hay categoría padre, solo las categorías primarias
            formatted_category = " > ".join(categorias_primarias)

    return formatted_category