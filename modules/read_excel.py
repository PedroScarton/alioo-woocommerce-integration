import pandas as pd
import logging

def read_excel(excel_path):
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        logging.info(f"File '{excel_path}' read successfully.")
        return df
    except Exception as e:
        logging.error(f" Error reading file '{excel_path}': {e}")
        return