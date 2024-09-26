# modules/authentication/login.py

import requests
from urllib.parse import urljoin
from config.settings import BASE_URL, USERNAME, PASSWORD, FACILITY_ID, CASH_REGISTER_ID

def login():
    """
    Realiza el login y retorna el token de autenticación y las cookies de sesión.
    """
    login_endpoint = "InventoryJSON/Login.rails"
    login_url = urljoin(BASE_URL, login_endpoint)
    params = {
        "username": USERNAME,
        "pass": PASSWORD,
        "facilityId": FACILITY_ID,
        "cashRegisterId": CASH_REGISTER_ID
    }

    # Crear una sesión para mantener las cookies
    session = requests.Session()
    response = session.get(login_url, params=params)
    response.raise_for_status()  # Lanza una excepción si ocurre un error HTTP

    data = response.json()
    token = data['ailooContext']['token']

    # Obtener las cookies de la sesión
    cookies = session.cookies.get_dict()

    return token, cookies

def get_token():
    """
    Retorna el token de autenticación.
    """
    token, _ = login()
    return token

def get_cookies():
    """
    Retorna las cookies de sesión necesarias para futuras peticiones.
    """
    _, cookies = login()
    return cookies
