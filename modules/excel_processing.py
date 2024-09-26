# modules/excel_processing.py

import pandas as pd
import os

def process_excel(input_path, output_path):
    """
    Procesa el archivo Excel descargado y lo convierte al formato necesario para WooCommerce.
    """
    # Leer el Excel
    df = pd.read_excel(input_path, engine='openpyxl')

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
    df = df[selected_columns]

    # Procesar la ruta de categorías
    def process_categories(row):
        categories = row['Ruta Categorías'].split('/')
        categories = [cat.strip() for cat in categories if cat.strip()]
        return categories

    df['Categorías'] = df.apply(process_categories, axis=1)

    # Crear columnas para los atributos
    df['pa_marca'] = df['Marca']
    df['pa_modelo'] = df['Modelo']
    df['pa_tamano'] = df['Tamaños']
    df['pa_color'] = df['Colores']

    # Procesar las URLs de las imágenes
    BASE_IMAGE_URL = 'http://mundobikes.ailoo.cl'

    def process_image_url(image_path):
        if pd.isna(image_path) or image_path.strip() == '':
            return ''
        # Eliminar el '/' inicial si existe
        image_path = image_path.lstrip('/')
        # Dividir la ruta en partes
        parts = image_path.split('/')
        if len(parts) != 2:
            # Formato inesperado
            return ''
        domain_id = parts[0]
        image_filename = parts[1]
        # Extraer el nombre del archivo y la extensión
        image_name, ext = os.path.splitext(image_filename)
        if len(image_name) < 3:
            # Formato inesperado
            return ''
        # Obtener los primeros tres caracteres
        first_three_chars = image_name[:3]
        first_char = first_three_chars[0]
        next_two_chars = first_three_chars[1:]
        # Construir la nueva ruta de la imagen
        new_image_name = f"{image_name}_900{ext}"
        image_url = f"{BASE_IMAGE_URL}/Content/products/{domain_id}/{first_char}/{next_two_chars}/{new_image_name}"
        return image_url

    df['Images'] = df['Imagenes Ailoo'].apply(process_image_url)

    # Renombrar y asegurar que el stock es un entero
    df['stock'] = df['Stock:Mundo Bikes'].fillna(0).astype(int)

    # Crear un DataFrame para WooCommerce
    wc_df = pd.DataFrame()

    # Mapear las columnas
    wc_df['ID'] = df['Id']
    wc_df['Type'] = 'simple'
    wc_df['SKU'] = df['SKU']
    wc_df['Name'] = df['Producto']
    wc_df['Published'] = 1
    wc_df['Is featured?'] = 0
    wc_df['Visibility in catalog'] = 'visible'
    wc_df['Short description'] = ''
    wc_df['Description'] = ''
    wc_df['Tax status'] = 'taxable'
    wc_df['Tax class'] = ''
    wc_df['In stock?'] = df['stock'].apply(lambda x: 1 if x > 0 else 0)
    wc_df['Stock'] = df['stock']
    wc_df['Backorders allowed?'] = 0
    wc_df['Sold individually?'] = 0
    wc_df['Regular price'] = df['Precio']
    wc_df['Sale price'] = ''
    wc_df['Categories'] = df['Categorías'].apply(lambda x: ', '.join(x))
    wc_df['Tags'] = df['Etiquetas']
    wc_df['Images'] = df['Images']
    wc_df['Attribute 1 name'] = 'Marca'
    wc_df['Attribute 1 value(s)'] = df['pa_marca']
    wc_df['Attribute 1 visible'] = 1
    wc_df['Attribute 1 global'] = 1
    wc_df['Attribute 2 name'] = 'Modelo'
    wc_df['Attribute 2 value(s)'] = df['pa_modelo']
    wc_df['Attribute 2 visible'] = 1
    wc_df['Attribute 2 global'] = 1
    wc_df['Attribute 3 name'] = 'Tamaño'
    wc_df['Attribute 3 value(s)'] = df['pa_tamano']
    wc_df['Attribute 3 visible'] = 1
    wc_df['Attribute 3 global'] = 1
    wc_df['Attribute 4 name'] = 'Color'
    wc_df['Attribute 4 value(s)'] = df['pa_color']
    wc_df['Attribute 4 visible'] = 1
    wc_df['Attribute 4 global'] = 1

    # Guardar el DataFrame en un archivo CSV
    wc_df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"Archivo procesado y guardado en {output_path}")
