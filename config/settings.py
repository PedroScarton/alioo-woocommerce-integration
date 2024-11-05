# config/settings.py

import os
from dotenv import load_dotenv
from pathlib import Path

from woocommerce import API

# Ruta al archivo .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Función auxiliar para obtener variables de entorno con validación
def get_env_variable(var_name, default_value=None, required=True):
    value = os.getenv(var_name, default_value)
    if required and value is None:
        raise EnvironmentError(f"La variable de entorno {var_name} no está definida y es requerida.")
    return value

# Configuración de la aplicación
BASE_URL = get_env_variable('BASE_URL')

# Credenciales para el login
USERNAME = get_env_variable('ALIOO_USERNAME')
PASSWORD = get_env_variable('ALIOO_PASSWORD')
FACILITY_ID = get_env_variable('FACILITY_ID')
CASH_REGISTER_ID = get_env_variable('CASH_REGISTER_ID')
ALIOO_API_KEY = get_env_variable('ALIOO_API_KEY')

# Configuración de WooCommerce
WOOCOMMERCE_URL = get_env_variable('WOOCOMMERCE_URL')
WC_CONSUMER_KEY = get_env_variable('WC_CONSUMER_KEY')
WC_CONSUMER_SECRET = get_env_variable('WC_CONSUMER_SECRET')

# URL base de las imágenes
BASE_IMAGE_URL='http://mundobikes.ailoo.cl'

# Configuración de la API de WooCommerce

wcapi = API(
    url=WOOCOMMERCE_URL,
    consumer_key=WC_CONSUMER_KEY,
    consumer_secret=WC_CONSUMER_SECRET,
    version="wc/v3",
    timeout=60
)