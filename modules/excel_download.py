# modules/excel_download/download_excel.py

import logging
import requests
from urllib.parse import urljoin
from datetime import datetime
from config.settings import BASE_URL, USERNAME, FACILITY_ID, CASH_REGISTER_ID
from .authentication import get_cookies, get_token


def download_excel(output_path):
    # """
    # Download the Excel file with the products from the Alioo system.
    # """
    # Get the authentication token and session cookies
    token = get_token()
    cookies = get_cookies()

    # Add the cookies obtained in the login
    session_cookies = {
        'token': token,
        'user': USERNAME,
        'facility': FACILITY_ID,
        'cashRegister': CASH_REGISTER_ID
    }
    # Update the session cookies with the cookies from the login
    session_cookies.update(cookies)

    logging.info("Descargando archivo Excel...")

    # Endpoint to download the Excel file
    download_endpoint = "InventoryJSON/DownloadProductsExcel.rails"
    download_url = urljoin(BASE_URL, download_endpoint)
    params = {
        "categoryId": 0,
        "brandId": 0,
        "until": datetime.now().strftime('%Y-%m-%d')  # Current date
    }

    # Send the request to download the Excel
    response = requests.get(download_url, params=params, cookies=session_cookies)
    response.raise_for_status()

    logging.info("Archivo Excel descargado correctamente.")

    # Save the Excel file
    with open(output_path, 'wb') as f:
        f.write(response.content)


    logging.info(f"Archivo Excel guardado en '{output_path}'.")
