# main.py

import logging
from modules.excel_download import download_excel
from modules.excel_processing import process_excel
from modules.woocommerce_sync import sync_products

# Configuración del logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def main():
    try:
        logging.info("Inicio del proceso automatizado.")

        # Rutas de los archivos
        excel_path = 'data/input/raw_excel.xlsx'
        processed_data_path = 'data/output/processed_data.csv'

        # Paso 1: Descargar el Excel
        download_excel(excel_path)

        # # Paso 2: Procesar el Excel
        # process_excel(excel_path, processed_data_path)

        # # Paso 3: Integrar con WooCommerce
        # sync_products(processed_data_path)

        # logging.info("Proceso completado exitosamente.")

    except Exception as e:
        logging.error(f"Ocurrió un error: {e}")
        raise

if __name__ == "__main__":
    main()
