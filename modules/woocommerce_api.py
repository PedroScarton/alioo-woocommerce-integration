import logging
import pandas as pd
import requests

def get_all_woocommerce_products(wcapi):
    try:
        products = []
        page = 1
        while True:
            response = wcapi.get("products", params={"per_page": 100, "page": page})
            data = response.json()
            if not data:
                break
            products.extend(data)
            page += 1
        df_wc = pd.DataFrame(products)

        # Skip persistent product in woocommerce
        persistent_product_name = ['Booknetic']

        df_wc = df_wc[~df_wc['name'].isin(persistent_product_name)]

        logging.info("Fetched all products from WooCommerce.")
        return df_wc
    except Exception as e:
        logging.error(f"Error fetching products from WooCommerce: {e}")
        raise

def create_simple_products(wcapi, products):
    for product in products:
        try:
            response = wcapi.post("products", product)
            response_data = response.json()
            if response.status_code in [200, 201]:
                logging.info(f"Created simple product '{product['name']}' with SKU '{product['sku']}'")
            else:
                error_message = response_data.get('message', 'Unknown error')
                logging.error(f"Failed to create simple product '{product['name']}' with SKU '{product['sku']}': {error_message}")
                logging.info(f"Product JSON: {product}")
        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while creating simple product '{product['name']}' with SKU '{product['sku']}'")
        except Exception as e:
            logging.error(f"Error creating simple product '{product['name']}': {e}")
            logging.info(f"Product JSON: {product}")


def create_variable_products(wcapi, products):
    for item in products:
        parent_product = item['parent']
        variations = item['variations']
        try:
            # Create parent product
            response = wcapi.post("products", parent_product)
            response_data = response.json()
            if response.status_code == 201:
                parent_id = response_data['id']
                logging.info(f"Created variable product '{parent_product['name']}' with SKU '{parent_product['sku']}'")
            else:
                error_message = response_data.get('message', 'Unknown error')
                logging.error(f"Failed to create variable product '{parent_product['name']}': {error_message}")
                logging.info(f"Product JSON: {parent_product}")
                continue  # No continuar con las variaciones si falla la creación del padre

            # Create variations
            for variation in variations:
                variation_response = wcapi.post(f"products/{parent_id}/variations", variation)
                variation_data = variation_response.json()
                if variation_response.status_code == 201:
                    logging.info(f"Created variation with SKU '{variation['sku']}' for product ID {parent_id}")
                else:
                    error_message = variation_data.get('message', 'Unknown error')
                    logging.error(f"Failed to create variation with SKU '{variation['sku']}' for product ID {parent_id}: {error_message}")
                    logging.info(f"Variation JSON: {variation}")
        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while creating variable product '{parent_product['name']}'")
        except Exception as e:
            logging.error(f"Error creating variable product '{parent_product['name']}': {e}")
            logging.info(f"Variation JSON: {variations}")


def update_products(wcapi, products):
    for product in products:
        try:
            product_id = product.pop('id')
            response = wcapi.put(f"products/{product_id}", product)
            response_data = response.json()
            if response.status_code in [200, 201]:
                logging.info(f"Updated product '{product.get('name', '')}' with SKU '{product.get('sku', '')}'")
            else:
                error_message = response_data.get('message', 'Unknown error')
                logging.error(f"Failed to update product ID '{product_id}': {error_message}")
                logging.info(f"Product JSON: {product}")
        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while updating product ID '{product_id}'")
        except Exception as e:
            logging.error(f"Error updating product ID '{product_id}': {e}")
            logging.info(f"Product JSON: {product}")

def delete_products_batch(wcapi, product_ids, batch_size=20):
    for i in range(0, len(product_ids), batch_size):
        batch_ids = product_ids[i:i + batch_size]
        data = {
            "delete": batch_ids
        }
        try:
            response = wcapi.post("products/batch", data)
            response_data = response.json()
            if response.status_code in [200, 201]:
                deleted_products = response_data.get('delete', [])
                for product in deleted_products:
                    logging.info(f"Deleted product ID '{product['id']}'")
                errors = response_data.get('errors', [])
                for error in errors:
                    logging.error(f"Error deleting product: {error}")
            else:
                error_message = response_data.get('message', 'Unknown error')
                logging.error(f"Failed to delete product batch: {error_message}")
        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while deleting product batch starting at index {i}")
        except Exception as e:
            logging.error(f"Error deleting product batch starting at index {i}: {e}")

def get_variations_for_product(wcapi, parent_id):
    try:
        variations = []
        page = 1
        while True:
            response = wcapi.get(f"products/{parent_id}/variations", params={"per_page": 100, "page": page})
            data = response.json()
            if not data:
                break
            variations.extend(data)
            page += 1
        return variations
    except Exception as e:
        logging.error(f"Error fetching variations for product ID {parent_id}: {e}")
        return []


def update_variable_products(wcapi, variable_products):
    for item in variable_products:
        parent_product = item['parent']
        parent_id = item['parent_id']
        variations_to_update = item['variations_to_update']
        variations_to_create = item['variations_to_create']
        variations_to_delete = item['variations_to_delete']

        try:
            # Update parent product
            response = wcapi.put(f"products/{parent_id}", parent_product).json()
            logging.info(f"Updated variable product '{parent_product['name']}' with ID {parent_id}")

            # Update existing variations
            for variation in variations_to_update:
                variation_id = variation.pop('id')
                response = wcapi.put(f"products/{parent_id}/variations/{variation_id}", variation).json()
                logging.info(f"Updated variation with SKU '{variation['sku']}' and ID {variation_id}")

            # Create new variations
            for variation in variations_to_create:
                response = wcapi.post(f"products/{parent_id}/variations", variation).json()
                logging.info(f"Created new variation with SKU '{variation['sku']}' for product ID {parent_id}")

            # Delete variations not in Excel
            for variation_id in variations_to_delete:
                response = wcapi.delete(f"products/{parent_id}/variations/{variation_id}", params={"force": True}).json()
                logging.info(f"Deleted variation ID {variation_id} from product ID {parent_id}")

        except Exception as e:
            logging.error(f"Error updating variable product ID {parent_id}: {e}")


def get_all_woocommerce_categories(wcapi):
    try:
        categories = []
        page = 1
        while True:
            response = wcapi.get("products/categories", params={"per_page": 100, "page": page})
            data = response.json()
            if not data:
                break
            categories.extend(data)
            page += 1
        # Build a mapping from category name to ID
        category_name_to_id = {cat['name']: cat['id'] for cat in categories}
        logging.info("Fetched all categories from WooCommerce.")
        return category_name_to_id
    except Exception as e:
        logging.error(f"Error fetching categories from WooCommerce: {e}")
        raise


def create_missing_categories(wcapi, category_names, existing_categories):

    # Get existing categories from existing_categories dict (keys)
    existing_categorie_names = existing_categories.keys()

    # Get missing categories in category_names list
    missing_categories = list(set(category_names) - set(existing_categorie_names))

    # Create missing categories
    for category_name in missing_categories:
        try:
            data = {"name": category_name}
            response = wcapi.post("products/categories", data).json()
            category_id = response.get('id')
            if category_id:
                existing_categories[category_name] = category_id
                logging.info(f"Created new category '{category_name}' with ID {category_id}")
            else:
                logging.error(f"Failed to create category '{category_name}': {response}")
        except Exception as e:
            logging.error(f"Error creating category '{category_name}': {e}")


    return existing_categories