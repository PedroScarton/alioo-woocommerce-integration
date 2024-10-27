import pandas as pd
import logging

from .image_processing import process_image_urls
from .woocommerce_api import get_variations_for_product

def pre_process_df(df_excel):
    # Remove products without SKU from df_excel
    df_excel = df_excel.dropna(subset=['SKU'])
    df_excel = df_excel[df_excel['SKU'].astype(str).str.strip() != '']

    # Add categories column to df_excel
    df_excel['categories'] = None

    # Return the updated dataframe
    return df_excel


def map_sku_to_id(df_wc):
    sku_to_id = df_wc.set_index('sku')['id'].to_dict()
    return sku_to_id

def identify_products(df_excel, df_wc):

    # SKUs in Excel
    excel_skus = set(df_excel['SKU'])

    # SKUs in WooCommerce
    if not df_wc.empty and 'sku' in df_wc.columns:
        wc_skus = set(df_wc['sku'])
    else:
        wc_skus = set()

    # New products: SKUs in Excel but not in WooCommerce
    new_skus = excel_skus - wc_skus
    df_new = df_excel[df_excel['SKU'].isin(new_skus)]

    # Updated products: SKUs in both Excel and WooCommerce
    updated_skus = excel_skus & wc_skus
    df_updated = df_excel[df_excel['SKU'].isin(updated_skus)]

    # Products to delete: SKUs in WooCommerce but not in Excel
    delete_skus = wc_skus - excel_skus
    if not df_wc.empty:
        df_delete = df_wc[df_wc['sku'].isin(delete_skus)]
    else:
        df_delete = pd.DataFrame(columns=df_wc.columns)

    return df_new, df_updated, df_delete

def map_variation_sku_to_id(variations):
    sku_to_id = {}
    for variation in variations:
        sku = variation.get('sku')
        if sku:
            sku_to_id[sku] = variation['id']
    return sku_to_id


def separate_simple_and_variable(df):
    # Count how many times each Id appears
    id_counts = df['Id'].value_counts()

    # Variable products have Ids that appear more than once
    variable_ids = id_counts[id_counts > 1].index
    df_variable = df[df['Id'].isin(variable_ids)]

    # Simple products have Ids that appear only once
    simple_ids = id_counts[id_counts == 1].index
    df_simple = df[df['Id'].isin(simple_ids)]

    return df_simple, df_variable


def format_simple_products(df_simple, category_name_to_id):
    products = []
    for index, row in df_simple.iterrows():

        # Get category IDs
        categories = []
        primary_category = str(row['Categoria Primaria']).strip()
        parent_category = str(row['Categoría Padre']).strip()
        if primary_category and primary_category in category_name_to_id:
            categories.append({"id": category_name_to_id[primary_category]})
        if parent_category and parent_category in category_name_to_id:
            categories.append({"id": category_name_to_id[parent_category]})

        product = {
            "name": row['Producto'],
            "type": "simple",
            "regular_price": str(row['Precio']),
            "sku": row['SKU'],
            "description": row['Descripción'] if 'Descripción' in row and not pd.isna(row['Descripción']) else '',
            "categories": categories,
            # "tags": [{"name": tag.strip()} for tag in str(row['Etiquetas']).split(',') if tag.strip()],
            "manage_stock": True,
            "stock_quantity": int(row['Stock:Mundo Bikes']) if 'Stock:Mundo Bikes' in row and not pd.isna(row['Stock:Mundo Bikes']) else 0,
        }

        # Process images using the process_image_urls function
        image_urls = process_image_urls(row['Imagenes Ailoo'], row['Id'])
        if image_urls:
            product["images"] = [{"src": url.strip()} for url in image_urls.split(',') if url.strip()]

        # Update custom fields as attributes
        attributes = []

        # Brand
        if 'Marca' in row and not pd.isna(row['Marca']) and row['Marca'].strip():
            attributes.append({
                "name": "Marca",
                "options": [row['Marca']],
                "visible": True,
                "variation": False
            })

        # Model
        if 'Modelo' in row and not pd.isna(row['Modelo']) and row['Modelo'].strip():
            attributes.append({
                "name": "Modelo",
                "options": [row['Modelo']],
                "visible": True,
                "variation": False
            })

        # Sizes
        if 'Tamaños' in row and not pd.isna(row['Tamaños']) and row['Tamaños'].strip():
            tamanos = [size.strip() for size in str(row['Tamaños']).split(',') if size.strip()]
            attributes.append({
                "name": "Tamaño",
                "options": tamanos,
                "visible": True,
                "variation": False
            })

        # Colors
        if 'Colores' in row and not pd.isna(row['Colores']) and row['Colores'].strip():
            colores = [color.strip() for color in str(row['Colores']).split(',') if color.strip()]
            attributes.append({
                "name": "Color",
                "options": colores,
                "visible": True,
                "variation": False
            })

        # Proveedor
        attributes.append({ "name": "Proveedor", "options": "Alioo", "visible": False, "variation": False })

        # Proveedor
        attributes.append({ "name": "Alioo ID", "options": row['Id'], "visible": False, "variation": False })

        if attributes:
            product['attributes'] = attributes

        products.append(product)
    return products


def format_variable_products(df_variable):
    products = []
    # Group by Id
    grouped = df_variable.groupby('Id')
    for product_id, group in grouped:
        # Get the first row of the group
        first_row = group.iloc[0]

        # Get category IDs
        categories = []
        # primary_category = str(first_row['Categoria Primaria']).strip()
        # parent_category = str(first_row['Categoría Padre']).strip()
        # if primary_category and primary_category in category_name_to_id:
        #     categories.append({"id": category_name_to_id[primary_category]})
        # if parent_category and parent_category in category_name_to_id:
        #     categories.append({"id": category_name_to_id[parent_category]})

        # Generate the parent SKU based on the name of the product
        parent_sku = first_row['Producto'].lower().replace(' ', '-')


        # Parent product
        parent_product = {
            "name": first_row['Producto'],
            "type": "variable",
            "sku": parent_sku,
            "description": first_row['Descripción'] if 'Descripción' in first_row and not pd.isna(first_row['Descripción']) else '',
            "categories": categories,
            # "tags": [{"name": tag.strip()} for tag in str(first_row['Etiquetas']).split(',') if tag.strip()],
            "images": []
        }

        # Update custom fields as attributes
        attributes = []

        # Brand
        if 'Marca' in first_row and not pd.isna(first_row['Marca']) and first_row['Marca'].strip():
            attributes.append({
                "name": "Marca",
                "options": [first_row['Marca']],
                "visible": True,
                "variation": False # Assuming "Marca" is not a variation attribute
            })

        # Model
        if 'Modelo' in first_row and not pd.isna(first_row['Modelo']) and first_row['Modelo'].strip():
            attributes.append({
                "name": "Modelo",
                "options": [first_row['Modelo']],
                "visible": True,
                "variation": False # Assuming "Modelo" is not a variation attribute
            })

        plural_to_singular = {
            'Tamaños': 'Tamaño',
            'Colores': 'Color'
        }

        # Variable attributes
        variable_attributes = {}
        for attr_name in ['Tamaños', 'Colores']:
            if attr_name in group.columns:
                values = group[attr_name].dropna().unique().tolist()
                if values:
                    # Clean values and remove empty strings
                    cleaned_values = [str(value).strip() for value in values if str(value).strip()]
                    if cleaned_values:
                        singular_name = plural_to_singular.get(attr_name, attr_name)
                        variable_attributes[attr_name] = {
                            "name": singular_name,
                            "options": list(set(cleaned_values)),
                            "visible": True,
                            "variation": True
                        }

        # Add variable attributes to the parent product
        attributes.extend(variable_attributes.values())

        # Add variable attributes to the variations
        parent_product['attributes'] = attributes

        # Variations
        variations = []
        for index, row in group.iterrows():
            variation = {
                "regular_price": str(row['Precio']),
                "sku": row['SKU'],
                "attributes": [],
                "manage_stock": True,
                "stock_quantity": int(row['Stock:Mundo Bikes']) if 'Stock:Mundo Bikes' in row and not pd.isna(row['Stock:Mundo Bikes']) else 0,
                "images": []
            }

            # Process images using the process_image_urls function
            # variation_image_urls = process_image_urls(row['Imagenes Ailoo'], row['Id'])
            # if variation_image_urls:
            #     # Use the first image as the variation image
            #     variation_image_url = variation_image_urls.split(',')[0]
            #     variation["image"] = {"src": variation_image_url.strip()}

            # Add variation attributes
            for attr_name in ['Tamaños', 'Colores']:
                if attr_name in row and pd.notna(row[attr_name]) and str(row[attr_name]).strip():
                    singular_name = plural_to_singular.get(attr_name, attr_name)
                    variation['attributes'].append({
                        "name": singular_name,
                        "option": str(row[attr_name]).strip()
                    })

            variations.append(variation)

        products.append({
            "parent": parent_product,
            "variations": variations
        })
    return products


def format_updated_simple_products(df_simple, sku_to_id, category_name_to_id):
    products = []
    for index, row in df_simple.iterrows():

        product_id = sku_to_id.get(row['SKU'])

        if not product_id:
            continue # Cannot update a product that doesn't exist

        # Get category IDs
        categories = []
        primary_category = str(row['Categoria Primaria']).strip()
        parent_category = str(row['Categoría Padre']).strip()
        if primary_category and primary_category in category_name_to_id:
            categories.append({"id": category_name_to_id[primary_category]})
        if parent_category and parent_category in category_name_to_id:
            categories.append({"id": category_name_to_id[parent_category]})

        product = {
            "id": product_id,
            "name": row['Producto'],
            "regular_price": str(row['Precio']),
            "sku": row['SKU'],
            "categories": categories,
            # "tags": [{"name": tag.strip()} for tag in str(row['Etiquetas']).split(',') if tag.strip()],
            "manage_stock": True,
            "stock_quantity": int(row['Stock:Mundo Bikes']) if 'Stock:Mundo Bikes' in row and not pd.isna(row['Stock:Mundo Bikes']) else 0,
            "backorders": "no",
        }

        # Process images using the process_image_urls function
        image_urls = process_image_urls(row['Imagenes Ailoo'], row['Id'])
        if image_urls:
            product["images"] = [{"src": url.strip()} for url in image_urls.split(',') if url.strip()]

        # Update custom fields as attributes
        attributes = []

        # Brand
        if 'Marca' in row and not pd.isna(row['Marca']) and row['Marca'].strip():
            attributes.append({
                "name": "Marca",
                "options": [row['Marca']],
                "visible": True,
                "variation": False
            })

        # Model
        if 'Modelo' in row and not pd.isna(row['Modelo']) and row['Modelo'].strip():
            attributes.append({
                "name": "Modelo",
                "options": [row['Modelo']],
                "visible": True,
                "variation": False
            })

        # Sizes
        if 'Tamaños' in row and not pd.isna(row['Tamaños']) and row['Tamaños'].strip():
            tamanos = [size.strip() for size in str(row['Tamaños']).split(',') if size.strip()]
            attributes.append({
                "name": "Tamaño",
                "options": tamanos,
                "visible": True,
                "variation": False
            })

        # Colors
        if 'Colores' in row and not pd.isna(row['Colores']) and row['Colores'].strip():
            colores = [color.strip() for color in str(row['Colores']).split(',') if color.strip()]
            attributes.append({
                "name": "Color",
                "options": colores,
                "visible": True,
                "variation": False
            })

        # Proveedor
        attributes.append({ "name": "Proveedor", "options": "Alioo", "visible": False, "variation": False })

        # Proveedor
        attributes.append({ "name": "Alioo ID", "options": row['Id'], "visible": False, "variation": False })

        if attributes:
            product['attributes'] = attributes


        products.append(product)
    return products



def format_updated_variable_products(df_variable, sku_to_id, category_name_to_id, wcapi):
    products = []
    # Group by 'Id' to process each variable product
    grouped = df_variable.groupby('Id')
    for product_id, group in grouped:
        first_row = group.iloc[0]
        parent_sku = first_row['SKU']
        parent_id = sku_to_id.get(parent_sku)
        if not parent_id:
            logging.warning(f"Parent product with SKU '{parent_sku}' not found in WooCommerce.")
            continue

        # Get category IDs
        categories = []
        primary_category = str(first_row['Categoria Primaria']).strip()
        parent_category = str(first_row['Categoría Padre']).strip()
        if primary_category and primary_category in category_name_to_id:
            categories.append({"id": category_name_to_id[primary_category]})
        if parent_category and parent_category in category_name_to_id:
            categories.append({"id": category_name_to_id[parent_category]})

        # Prepare parent product data for update
        parent_product = {
            "id": parent_id,
            "name": first_row['Producto'],
            "type": "variable",
            "description": first_row['Descripción'] if 'Descripción' in first_row and not pd.isna(first_row['Descripción']) else '',
            "categories": categories,
            # "tags": [{"name": tag.strip()} for tag in str(first_row['Etiquetas']).split(',') if tag.strip()],
        }

        # Process images using the process_image_urls function
        image_urls = process_image_urls(first_row['Imagenes Ailoo'], first_row['Id'])
        if image_urls:
            parent_product["images"] = [{"src": url.strip()} for url in image_urls.split(',') if url.strip()]

        # Update attributes
        attributes = []

        # Brand
        if 'Marca' in first_row and not pd.isna(first_row['Marca']) and first_row['Marca'].strip():
            attributes.append({
                "name": "Marca",
                "options": [first_row['Marca']],
                "visible": True,
                "variation": False
            })

        # Model
        if 'Modelo' in first_row and not pd.isna(first_row['Modelo']) and first_row['Modelo'].strip():
            attributes.append({
                "name": "Modelo",
                "options": [first_row['Modelo']],
                "visible": True,
                "variation": False
            })

        plural_to_singular = {
            'Tamaños': 'Tamaño',
            'Colores': 'Color'
        }

        # Variable attributes
        variable_attributes = {}
        for attr_name in ['Tamaños', 'Colores']:
            if attr_name in group.columns:
                values = group[attr_name].dropna().unique().tolist()
                if values:
                    cleaned_values = [str(value).strip() for value in values if str(value).strip()]
                    if cleaned_values:
                        singular_name = plural_to_singular.get(attr_name, attr_name)
                        variable_attributes[attr_name] = {
                            "name": singular_name,
                            "options": list(set(cleaned_values)),
                            "visible": True,
                            "variation": True
                        }

        attributes.extend(variable_attributes.values())
        parent_product['attributes'] = attributes

        # Fetch existing variations from WooCommerce
        existing_variations = get_variations_for_product(wcapi, parent_id)
        variation_sku_to_id = map_variation_sku_to_id(existing_variations)

        # Variations to update or create
        variations_to_update = []
        variations_to_create = []

        # SKUs of variations in Excel
        excel_variation_skus = set()

        for index, row in group.iterrows():
            variation_sku = row['SKU']
            excel_variation_skus.add(variation_sku)
            variation_data = {
                "sku": variation_sku,
                "regular_price": str(row['Precio']),
                "manage_stock": True,
                "stock_quantity": int(row['Stock:Mundo Bikes']) if 'Stock:Mundo Bikes' in row and not pd.isna(row['Stock:Mundo Bikes']) else 0,
                "attributes": []
            }

            # Process images
            variation_image_urls = process_image_urls(row['Imagenes Ailoo'], row['Id'])
            if variation_image_urls:
                variation_image_url = variation_image_urls.split(',')[0]
                variation_data["image"] = {"src": variation_image_url.strip()}

            # Add variation attributes
            for attr_name in ['Tamaños', 'Colores']:
                if attr_name in row and pd.notna(row[attr_name]) and str(row[attr_name]).strip():
                    singular_name = plural_to_singular.get(attr_name, attr_name)
                    variation_data['attributes'].append({
                        "name": singular_name,
                        "option": str(row[attr_name]).strip()
                    })

            # Check if variation exists
            variation_id = variation_sku_to_id.get(variation_sku)
            if variation_id:
                variation_data['id'] = variation_id
                variations_to_update.append(variation_data)
            else:
                variations_to_create.append(variation_data)

        # Variations to delete (existing variations not in Excel)
        existing_variation_skus = set(variation_sku_to_id.keys())
        skus_to_delete = existing_variation_skus - excel_variation_skus
        variations_to_delete = [variation_sku_to_id[sku] for sku in skus_to_delete]

        products.append({
            "parent": parent_product,
            "variations_to_update": variations_to_update,
            "variations_to_create": variations_to_create,
            "variations_to_delete": variations_to_delete,
            "parent_id": parent_id
        })

    return products


