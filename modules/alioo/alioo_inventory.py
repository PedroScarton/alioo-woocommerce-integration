import requests
from config.settings import ALIOO_API_KEY

def get_product_item_id(sku):
    print(f"Buscando product item id para sku: {sku}")
    url = f"https://api.ailoo.cl/v1/inventory/all/sku/{sku}"
    headers = {
        "X-Ailoo-Access-Token": ALIOO_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        error_code = data.get("error", {}).get("code")
        if error_code != 0:
            return None


        inventory_items = data.get("inventoryItems")
        if inventory_items and len(inventory_items) > 0:
            product_item_id = inventory_items[0].get("productItemId")
            return product_item_id if product_item_id is not None else None
        else:
             return None

    except requests.exceptions.RequestException as e:
        print(f"Error en la llamada a la API de Alioo: {e}")
        raise