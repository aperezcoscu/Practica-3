import json
import boto3
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime
import numpy as np
from io import StringIO
from decimal import Decimal


# Inicializar el cliente de S3
s3_client = boto3.client('s3')

### Calculamos volatilidades

# Función para calcular el precio de una opción call europea usando Black-Scholes
def black_scholes_call(S, K, T, r, sigma):
    if T <= 0:  # No se puede calcular precio de una opción con tiempo hasta vencimiento negativo o cero
        return 0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def black_scholes_put(S, K, T, r, sigma):
    if T <= 0:  # No se puede calcular precio de una opción con tiempo hasta vencimiento negativo o cero
        return 0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Función para extraer la volatilidad implícita
def implied_volatility(option_price, S, K, T, r, option_type):
    """Calcula la volatilidad implícita de una opción dada su precio de mercado.
    option_price : Precio de mercado de la opción
    S : Precio del activo subyacente
    K : Precio de ejercicio
    T : Tiempo hasta el vencimiento
    r : Tasa de interés libre de riesgo
    option_type : Tipo de opción ('call' o 'put')
    """
    if option_price <= 0 or T <= 0:
        return 0
    # Función objetivo para encontrar la volatilidad implícita
    def objective(sigma):
        if option_type == 'call':
            return black_scholes_call(S, K, T, r, sigma) - option_price
        else:
            return black_scholes_put(S, K, T, r, sigma) - option_price
    # Resolver usando Brent's method
    try:
        result = brentq(objective, 1e-6, 4)
        return result
    except ValueError:
        return np.nan  


def subir_a_s3(data, bucket_name, object_name):
    """
    Sube los datos al bucket de S3 especificado.

    Args:
    - data (str): Datos en formato JSON.
    - bucket_name (str): Nombre del bucket de S3.
    - object_name (str): Nombre del objeto en S3.
    """
    try:
        s3_client.put_object(Body=data, Bucket=bucket_name, Key=object_name)
        print(f'Datos subidos correctamente {bucket_name}/{object_name}')
    except Exception as e:
        print(f'Se ha producido un error: {e}')

def subir_a_dynamodb(df):
    """
    Sube los datos al DynamoDB especificado.
    Args:
    - df (DataFrame): DataFrame de Pandas que contiene los datos a subir.
    """
    try:
        for index, row in df.iterrows():
            item = {
                'id': row['Fecha'] + '_' + str(row['Strike']),  # Asegúrate de que este campo es único
                'Fecha': row['Fecha'],
                'Strike': int(row['Strike']),
                'Vol_call': None if pd.isna(row['Vol_call']) else Decimal(str(row['Vol_call'])),
                'Vol_put': None if pd.isna(row['Vol_put']) else Decimal(str(row['Vol_put']))
            }
            table.put_item(Item=item)
        print('Datos almacenados correctamente y deploy correcto')
    except Exception as e:
        print(f'Se ha producido un error: {e}')


# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Volatilidades')  # Nombre de tu tabla de DynamoDB

def lambda_handler(event, context):
    bucket = 'miax-12-scrap-meff'
    opciones_key = 'datos_opciones.json'
    futuros_key = 'datos_futuros.json'

    # Leer datos de opciones
    s3_client = boto3.client('s3')
    response_opciones = s3_client.get_object(Bucket=bucket, Key=opciones_key)
    opciones_str = response_opciones['Body'].read().decode('utf-8')
    opciones_io = StringIO(opciones_str)
    df_opciones = pd.read_json(opciones_io)

    # Leer datos de futuros (para obtener el precio subyacente)
    response_futuros = s3_client.get_object(Bucket=bucket, Key=futuros_key)
    futuros_str = response_futuros['Body'].read().decode('utf-8')
    futuros_io = StringIO(futuros_str)
    df_futuros = pd.read_json(futuros_io)

    price_sub = df_futuros['Ant'].iloc[0] if not df_futuros.empty else 0
    rfr = 0.01  # Tasa de interés libre de riesgo

    # Calcular la volatilidad implícita para cada opción en df_opciones
    df_opciones['Vol_call'] = df_opciones.apply(
        lambda row: implied_volatility(row['Precio_call'], price_sub, row['Strike'], row['T'], rfr, 'call'), axis=1)
    df_opciones['Vol_put'] = df_opciones.apply(
        lambda row: implied_volatility(row['Precio_put'], price_sub, row['Strike'], row['T'], rfr, 'put'), axis=1)

    df_volatilidades = df_opciones.loc[:, ['Fecha', 'Strike', 'Vol_call', 'Vol_put']]

    # Subir a DynamoDB
    subir_a_dynamodb(df_volatilidades)

    return {
        'statusCode': 200,
        'body': json.dumps('Volatilidades subidas correctamente a DynamoDB y deployment realizado')
    }


if __name__ == "__main__":
    print(lambda_handler({}, {}))