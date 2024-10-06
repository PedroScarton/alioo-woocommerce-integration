import logging
import pandas as pd

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
        logging.info("Fetched all products from WooCommerce.")
        return df_wc
    except Exception as e:
        logging.error(f"Error fetching products from WooCommerce: {e}")
        raise

def create_simple_products(wcapi, products):
    for product in products:
        try:
            response = wcapi.post("products", product).json()
            logging.info(f"Created simple product '{product['name']}' with SKU '{product['sku']}'")
        except Exception as e:
            logging.error(f"Error creating simple product '{product['name']}': {e}")


def create_variable_products(wcapi, products):
    for item in products:
        parent_product = item['parent']
        variations = item['variations']
        try:
            # Create parent product
            response = wcapi.post("products", parent_product).json()
            parent_id = response['id']
            logging.info(f"Created variable product '{parent_product['name']}' with SKU '{parent_product['sku']}'")

            # Create variations
            for variation in variations:
                variation_response = wcapi.post(f"products/{parent_id}/variations", variation).json()
                logging.info(f"Created variation with SKU '{variation['sku']}' for product ID {parent_id}")
        except Exception as e:
            logging.error(f"Error creating variable product '{parent_product['name']}': {e}")


def update_products(wcapi, products):
    for product in products:
        try:
            product_id = product.pop('id')
            response = wcapi.put(f"products/{product_id}", product).json()
            logging.info(f"Updated product ID {product_id} with SKU '{product.get('sku', '')}'")
        except Exception as e:
            logging.error(f"Error updating product ID {product_id}: {e}")

def delete_products(wcapi, df_delete):
    for index, row in df_delete.iterrows():
        product_id = row['id']
        try:
            response = wcapi.delete(f"products/{product_id}", params={"force": True}).json()
            logging.info(f"Deleted product ID {product_id} with SKU '{row['sku']}'")
        except Exception as e:
            logging.error(f"Error deleting product ID {product_id}: {e}")

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
