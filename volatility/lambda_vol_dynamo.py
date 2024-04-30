import json
import boto3
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime
import numpy as np
from io import StringIO

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

#def lambda_handler(event, context):
#    bucket = 'miax-12-scrap-meff'
#    opciones_key = 'datos_opciones.json'
#    futuros_key = 'datos_futuros.json'
#    
#    # Obtener datos de opciones de S3
#    response_opciones = s3_client.get_object(Bucket=bucket, Key=opciones_key)
#    opciones_str = response_opciones['Body'].read().decode('utf-8')
#    df_opciones = pd.read_json(opciones_str)
#    
#    # Obtener datos de futuros de S3
#    response_futuros = s3_client.get_object(Bucket=bucket, Key=futuros_key)
#    futuros_str = response_futuros['Body'].read().decode('utf-8')
#    df_futuros = pd.read_json(futuros_str)
#    
#    # Suponemos que los datos de futuros incluyen un precio actual "Ant"
#    if not df_futuros.empty:
#        price_sub = df_futuros.loc[0, 'Ant']
#    else:
#        price_sub = 0  # O manejar de otra forma si no hay datos disponibles
#    
#    rfr = 0.01  # Tasa de interés libre de riesgo, ajustar según sea necesario
#    
#    # Calcular la volatilidad implícita para cada opción en df_opciones
#    df_opciones['Vol_call'] = df_opciones.apply(
#        lambda row: implied_volatility(row['Precio_call'], price_sub, row['Strike'], row['T'], rfr, 'call'), axis=1)
#    df_opciones['Vol_put'] = df_opciones.apply(
#        lambda row: implied_volatility(row['Precio_put'], price_sub, row['Strike'], row['T'], rfr, 'put'), axis=1)
#    
#    # Preparar el DataFrame de volatilidades para la salida
#    volatilidades = df_opciones[['Strike', 'Vol_call', 'Vol_put']]
#    
#    # Convertir el DataFrame de volatilidades a JSON para la salida
#    result = volatilidades.to_dict('records')
#    
#    # Preparar los datos para almacenamiento en DynamoDB, o ajustar según necesidad
#    # DynamoDB table
#    dynamodb = boto3.resource('dynamodb')
#    table = dynamodb.Table('VolatilidadesTable')
#    
#    now = datetime.now()
#    timestamp = now.isoformat()
#    
#    # Subir los datos a DynamoDB
#    for record in result:
#        record_id = str(uuid.uuid4())  # Genera un UUID único para cada registro
#        record['timestamp'] = timestamp  # Añade un timestamp al registro
#        record['id'] = record_id  # Añade el UUID al registro
#        
#        # Escribe el registro en la tabla DynamoDB
#        try:
#            table.put_item(Item=record)
#        except Exception as e:
#            print(e)
#            continue  # O maneja la excepción como mejor te parezca
#
#    return {
#        'statusCode': 200,
#        'body': json.dumps(result)
#    }


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


def lambda_handler(event, context):
    bucket = 'miax-12-scrap-meff'
    opciones_key = 'datos_opciones.json'
    futuros_key = 'datos_futuros.json'

    # Leer datos de opciones
    response_opciones = s3_client.get_object(Bucket=bucket, Key=opciones_key)
    opciones_str = response_opciones['Body'].read().decode('utf-8')
    opciones_io = StringIO(opciones_str)  # Utilizar StringIO aquí
    df_opciones = pd.read_json(opciones_io)

    # Leer datos de futuros (para obtener el precio subyacente)
    response_futuros = s3_client.get_object(Bucket=bucket, Key=futuros_key)
    futuros_str = response_futuros['Body'].read().decode('utf-8')
    futuros_io = StringIO(futuros_str)  # Utilizar StringIO aquí
    df_futuros = pd.read_json(futuros_io)

    price_sub = df_futuros['Ant'].iloc[0] if not df_futuros.empty else 0
    rfr = 0.01  # Ejemplo de tasa de interés libre de riesgo

    # Calcular la volatilidad implícita para cada opción en df_opciones
    df_opciones['Vol_call'] = df_opciones.apply(
        lambda row: implied_volatility(row['Precio_call'], price_sub, row['Strike'], row['T'], rfr, 'call'), axis=1)
    df_opciones['Vol_put'] = df_opciones.apply(
        lambda row: implied_volatility(row['Precio_put'], price_sub, row['Strike'], row['T'], rfr, 'put'), axis=1)

    # Preparar el DataFrame de volatilidades para la salida
    volatilidades = df_opciones[['Strike', 'Vol_call', 'Vol_put']]

    vol_impli = volatilidades.to_json(orient='records')

    opciones_object_name = 'volatilidades_implicitas.json'

    # Subir a S3
    subir_a_s3(vol_impli, bucket, opciones_object_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Volatilidades calculadas correctamente')
    }



if __name__ == "__main__":
    # Suponiendo que no necesitas pasar un evento o contexto específico,
    # puedes llamar a lambda_handler con valores ficticios o nulos.
    print(lambda_handler({}, {}))