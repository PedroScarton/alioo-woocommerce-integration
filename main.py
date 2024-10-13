# main.py

import logging
import pandas as pd

import json

from config.settings import wcapi

from modules.excel_download import download_excel
from modules.read_excel import read_excel
from modules.woocommerce_api import get_all_woocommerce_products
from modules.product import prepare_dataframes, identify_products, separate_simple_and_variable, format_simple_products, format_variable_products, format_updated_simple_products, map_sku_to_id, format_updated_variable_products
from modules.woocommerce_api import create_simple_products, create_variable_products, update_products, delete_products_batch, update_variable_products, get_all_woocommerce_categories, create_missing_categories
from modules.dataframe_operations import get_unique_categories

# Configuración del logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def main():
    try:
        logging.info("Starting process...")

        # # File paths
        # excel_path = 'data/raw_excel.xlsx'

        # # Step 1: Download the Excel file
        # download_excel(excel_path)

        # # Step 2: Read the Excel file
        # df_excel = read_excel(excel_path)

        # # Step 3: Get all WooCommerce products
        # df_wc = get_all_woocommerce_products(wcapi)

        # # Step 4: Read WooCommerce products
        # df_excel, df_wc = prepare_dataframes(df_excel, df_wc)

        # # Step 5: Identify new, updated, and deleted products
        # df_new, df_updated, df_delete = identify_products(df_excel, df_wc)

        # # Extract unique categories from Excel
        # category_names = get_unique_categories(df_excel)

        # # Get existing categories from WooCommerce
        # category_name_to_id = get_all_woocommerce_categories(wcapi)

        # # Create missing categories
        # category_name_to_id = create_missing_categories(wcapi, category_names, category_name_to_id)

        # # Proceed with identifying new, updated, and deleted products
        # df_new, df_updated, df_delete = identify_products(df_excel, df_wc)

        # if not df_new.empty:
        #     logging.info(f"Found {len(df_new)} new products.")
        #     # Step 6: Separate simple and variable products
        #     df_new_simple, df_new_variable = separate_simple_and_variable(df_new)

        #     df_new_simple.to_csv('data/new_simple.csv', index=False)

        # #     # Step 7: Format and create new products
        #     products = format_simple_products(df_new_simple, category_name_to_id)
        #     format_variable_products(df_new_variable, category_name_to_id)

            # Create new products in WooCommerce
        products = {
                "name": "Abrillantador GS27",
                "type": "simple",
                "regular_price": "15000",
                "sku": "VE110251",
                "description": "",
                "categories": [{ "id": 103 }, { "id": 61 }],
                "manage_stock": True,
                "stock_quantity": 0,
                "images": [
      {
        "src": "http://mundobikes.ailoo.cl/Content/products/2387/e/d8/ed8e5e1c3dce49b09e8ded788f5aca3e_900.jpg"
      }
    ],
    "attributes": [
      {
        "name": "Marca",
        "options": ["GS27"],
        "visible": True,
        "variation": False
      },
      {
        "name": "Tama\u00f1o",
        "options": ["300ML"],
        "visible": True,
        "variation": False
      },
      {
        "name": "Color",
        "options": ["Blanco/Verde"],
        "visible": True,
        "variation": False
      }
    ]
  }
        
        
        response = wcapi.post("products", products)
        response_data = response.json()
        
        print(json.dumps(response_data, indent=4))
        
        # create_simple_products(wcapi, products)
        # else:
        #     logging.info("No new products found.")

        # # If there are products to update in WooCommerce (df_updated is not empty)
        # if not df_updated.empty:
        #     logging.info(f"Found {len(df_updated)} products to update.")
        #     # Step 9: Map SKU to WooCommerce ID
        #     sku_to_id = map_sku_to_id(df_wc)

        #     # Step 10: Process updated products
        #     df_updated_simple, df_updated_variable = separate_simple_and_variable(df_updated)

        #     # Step 11: Format products
        #     updated_simple_products = format_updated_simple_products(df_updated_simple, sku_to_id, category_name_to_id)
        #     updated_variable_products = format_updated_variable_products(df_updated_variable, sku_to_id, category_name_to_id, wcapi)


        #     # Step 12: Update products in WooCommerce
        #     update_products(wcapi, updated_simple_products)
        #     update_variable_products(wcapi, updated_variable_products)
        #     logging.info("Products updated.")
        # else:
        #     logging.info("No products to update.")

        # if not df_delete.empty:
        #     logging.info(f"Found {len(df_delete)} products to delete.")
        #     # Step 13: Delete products in WooCommerce that are not in the Excel file
        #     product_ids_to_delete = df_delete['id'].tolist()
        #     delete_products_batch(wcapi, product_ids_to_delete)
        #     logging.info("Products deleted.")
        # else:
        #     logging.info("No products to delete.")

        logging.info("Process finished successfully.")

    except Exception as e:
        logging.error(f"An error occurred during the process: {e}")
        raise

if __name__ == "__main__":
    main()
