# modules/excel_download/download_excel.py

import requests
from urllib.parse import urljoin
from datetime import datetime
from config.settings import BASE_URL, USERNAME, FACILITY_ID, CASH_REGISTER_ID
from .authentication import get_cookies, get_token

def download_excel(output_path):
    # """
    # Descarga el archivo Excel y lo guarda en la ruta especificada.
    # """
    # Obtener token y cookies
    token = get_token()
    cookies = get_cookies()

    # Construir las cookies necesarias para la petición
    session_cookies = {
        'token': token,
        'user': USERNAME,
        'facility': FACILITY_ID,
        'cashRegister': CASH_REGISTER_ID
    }
    # Añadir las cookies obtenidas en el login
    session_cookies.update(cookies)

    # Construir la URL de descarga
    download_endpoint = "InventoryJSON/DownloadProductsExcel.rails"
    download_url = urljoin(BASE_URL, download_endpoint)
    params = {
        "categoryId": 0,
        "brandId": 0,
        "until": datetime.now().strftime('%Y-%m-%d')  # Fecha actual
    }

    # Realizar la petición GET para descargar el Excel
    response = requests.get(download_url, params=params, cookies=session_cookies)
    response.raise_for_status()

    # Guardar el contenido en un archivo
    with open(output_path, 'wb') as f:
        f.write(response.content)
