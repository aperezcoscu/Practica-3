import requests
import pandas as pd
from decimal import Decimal
import numpy as np  # Usado en la máscara de valores NaN


def datos_dynamodb(url):
    """Obtiene datos desde una API REST y retorna un DataFrame."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Asegura que la respuesta es exitosa
        data = response.json()       # Parsea la respuesta JSON a un diccionario
        df = pd.DataFrame(data)      # Convierte el diccionario a DataFrame

        # Convertir todas las columnas que contienen decimales a flotantes
        for column in ['Vol_call', 'Strike', 'Vol_put']:
            df[column] = df[column].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

        # Filtrar y ordenar el DataFrame
        df = df.loc[:, ['Fecha_scrap', 'Fecha', 'Strike', 'Vol_call', 'Vol_put']]
        df = df.sort_values(by=['Fecha', 'Strike'])
        df = df.reset_index(drop=True)

        # Reemplazar valores menores que 0.001 en 'Vol_call' y 'Vol_put' por NaN
        df['Vol_call'] = df['Vol_call'].mask(df['Vol_call'] < 0.001, np.nan)
        df['Vol_put'] = df['Vol_put'].mask(df['Vol_put'] < 0.001, np.nan)

        return df

    except requests.RequestException as e:
        print(f"Error al hacer la solicitud HTTP: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
    

def datos_s3(url):
    """Función para obtener datos JSON desde la API y retornarlos como un DataFrame."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanzará un error si la respuesta de la API no es exitosa
        data = response.json()
        return pd.DataFrame(data)
    except requests.RequestException as e:
        print(f"Error al hacer la solicitud a la API: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

# URL de la API
api_url = "http://localhost:8000/volatilities/"
api_futuros = "http://localhost:8000/datos-futuros"


# Obtener los datos de la API 
df = datos_dynamodb(api_url)
df_futuro = datos_s3(api_futuros)

print(df)
