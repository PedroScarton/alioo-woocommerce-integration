# modules/authentication/login.py

import requests
from urllib.parse import urljoin
from config.settings import BASE_URL, USERNAME, PASSWORD, FACILITY_ID, CASH_REGISTER_ID

def login():
    """
    English version
    Perform the login and return the authentication token and session cookies.
    """
    login_endpoint = "InventoryJSON/Login.rails"
    login_url = urljoin(BASE_URL, login_endpoint)
    params = {
        "username": USERNAME,
        "pass": PASSWORD,
        "facilityId": FACILITY_ID,
        "cashRegisterId": CASH_REGISTER_ID
    }

    # Create a session to persist the cookies
    session = requests.Session()
    response = session.get(login_url, params=params)
    response.raise_for_status()  #  Raise an exception for 4xx and 5xx status codes

    data = response.json()
    token = data['ailooContext']['token']

    # Get the cookies from the session
    cookies = session.cookies.get_dict()

    return token, cookies

def get_token():
    """
    Return the authentication token for future requests.
    """
    token, _ = login()
    return token

def get_cookies():
    """
    Return the session cookies for future requests.
    """
    _, cookies = login()
    return cookies
