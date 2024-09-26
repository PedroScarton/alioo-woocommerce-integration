# modules/woocommerce_integration/woocommerce_sync.py

from woocommerce import API
import pandas as pd
from config.settings import WOOCOMMERCE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET

def sync_products(processed_data_path):
    """
    Sincroniza los productos con WooCommerce.
    """
    wcapi = API(
        url=WOOCOMMERCE_URL,
        consumer_key=WC_CONSUMER_KEY,
        consumer_secret=WC_CONSUMER_SECRET,
        version="wc/v3",
        timeout=30
    )

    # Leer los datos procesados
    df = pd.read_csv(processed_data_path)

    # Convertir el DataFrame en una lista de diccionarios
    products_data = df.to_dict(orient='records')

    # Obtener todos los productos actuales en WooCommerce
    existing_products = wcapi.get("products", params={"per_page": 100}).json()
    existing_product_ids = {product['id']: product for product in existing_products}

    # IDs de productos en el archivo procesado
    processed_product_ids = set()

    for product in products_data:
        product_id = product['id']
        processed_product_ids.add(product_id)

        if str(product_id) in existing_product_ids:
            # Actualizar producto existente
            wcapi.put(f"products/{product_id}", product)
        else:
            # Crear nuevo producto
            wcapi.post("products", product)

    # Identificar y eliminar productos que ya no están en el archivo procesado
    products_to_delete = set(existing_product_ids.keys()) - processed_product_ids

    for product_id in products_to_delete:
        wcapi.delete(f"products/{product_id}", params={"force": True})

    print("Sincronización con WooCommerce completada.")
