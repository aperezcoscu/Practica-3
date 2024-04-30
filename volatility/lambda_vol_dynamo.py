import json
import boto3
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime
from uuid import uuid4

# AWS SDK (boto3) inicialización
dynamodb = boto3.resource('dynamodb')
# Asegúrate de que el nombre de la tabla es correcto
table = dynamodb.Table('volatility_table')


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


def lambda_handler(event, context):
    # Asumiendo que 'event' es un diccionario que ya contiene el payload esperado
    body = json.loads(event['responsePayload']['body'])
    
    # Convierte los datos a DataFrames de pandas
    df_opciones = pd.DataFrame(body['opciones'])
    df_futuros = pd.DataFrame(body['futuros'])

    # Aquí asumimos que tienes una columna 'Ant' en tu dataframe de futuros.
    price_sub = df_futuros.loc[0, 'Ant'] if not df_futuros.empty else 0
    rfr = 0  # Tasa de interés libre de riesgo

    # Calcular la volatilidad implícita para cada opción en df_opciones
    df_opciones['Vol_call'] = df_opciones.apply(
        lambda row: implied_volatility(row['Precio_call'], price_sub, row['Strike'], row['T'], rfr, 'call'), axis=1)
    df_opciones['Vol_put'] = df_opciones.apply(
        lambda row: implied_volatility(row['Precio_put'], price_sub, row['Strike'], row['T'], rfr, 'put'), axis=1)

    # Preparar el DataFrame de volatilidades para la salida
    volatilidades = df_opciones.loc[:, ['Strike', 'Vol_call', 'Vol_put']]
    
    # Convierte el DataFrame de volatilidades a un diccionario para la salida JSON
    result = volatilidades.to_dict('records')

    # Obtiene la fecha y hora actual para el timestamp
    now = datetime.now()
    timestamp = now.isoformat()

    # Preparar los datos para importar a DynamoDB
    for record in result:
        record_id = str(uuid4())  # Genera un UUID único para cada registro
        record['timestamp'] = timestamp  # Añade un timestamp al registro
        record['id'] = record_id  # Añade el UUID al registro

        # Escribe el registro en la tabla DynamoDB
        try:
            table.put_item(Item=record)
        except Exception as e:
            print(e)
            continue  # O maneja la excepción como mejor te parezca

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }