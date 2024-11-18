# main.py

import logging

from config.settings import wcapi

from modules.alioo.excel_download import download_excel
from modules.read_excel import read_excel
from modules.woocommerce_api import get_all_woocommerce_products
from modules.product import pre_process_df, identify_products, separate_simple_and_variable, format_simple_products, format_updated_simple_products, map_sku_to_id
from modules.woocommerce_api import create_simple_products, update_products, delete_products_batch, get_all_woocommerce_categories, create_missing_categories
from modules.dataframe_operations import get_unique_categories

# Configuración del logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def main():
    try:
        # Clear log file
        open('logs/app.log', 'w').close()

        logging.info("Starting process...")

        # File paths
        excel_path = 'data/raw_excel.xlsx'

        # Download the Excel file
        download_excel(excel_path)

        # Read the Excel file
        df_excel = read_excel(excel_path)

        # Get all WooCommerce products
        df_wc = get_all_woocommerce_products(wcapi)

        # Read WooCommerce products
        df_excel = pre_process_df(df_excel)

        # # Identify new, updated, and deleted products
        df_new, df_updated, df_delete = identify_products(df_excel, df_wc)

        # Extract unique categories from Excel
        category_names = get_unique_categories(df_excel)

        # Get existing categories from WooCommerce
        category_name_to_id = get_all_woocommerce_categories(wcapi)

        # Create missing categories
        category_name_to_id = create_missing_categories(wcapi, category_names, category_name_to_id)

        if not df_new.empty:
            logging.info(f"Found {len(df_new)} new products.")
            # # Separate simple and variable products
            df_new_simple, df_new_variable = separate_simple_and_variable(df_new)

            # Export df_new_simple to a new Excel file
            df_new_simple.to_excel('data/new_simple_products.xlsx', index=False)

            # Format and create new products
            new_simple_products = format_simple_products(df_new_simple, category_name_to_id)

            # Create new products in WooCommerce
            create_simple_products(wcapi, new_simple_products)
        else:
            logging.info("No products to create.")

        # If there are products to update in WooCommerce (df_updated is not empty)
        if not df_updated.empty:
            logging.info(f"Found {len(df_updated)} products to update.")
            # Map SKU to WooCommerce ID
            sku_to_id = map_sku_to_id(df_wc)

            # Process updated products
            df_updated_simple, df_updated_variable = separate_simple_and_variable(df_updated)

            # Format products
            updated_simple_products = format_updated_simple_products(df_updated_simple, sku_to_id, category_name_to_id)

            # Update products in WooCommerce
            update_products(wcapi, updated_simple_products)

            logging.info("Products updated.")
        else:
            logging.info("No products to update.")

        if not df_delete.empty:
            logging.info(f"Found {len(df_delete)} products to delete.")

            # Delete products in WooCommerce that are not in the Excel file
            product_ids_to_delete = df_delete['id'].tolist()

            delete_products_batch(wcapi, product_ids_to_delete)

            logging.info("Products deleted.")
        else:
            logging.info("No products to delete.")

        logging.info("Process finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the process: {e}")
        raise

if __name__ == "__main__":
    main()
