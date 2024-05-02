import boto3
import pandas as pd
from decimal import Decimal
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt

# Inicializar un cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')

# Seleccionar la tabla
table = dynamodb.Table('Volatilidades')

response = table.scan()
data = response['Items']

# Convertir la lista de diccionarios a DataFrame
df = pd.DataFrame(data)

# Convertir todas las columnas que contienen decimales a flotantes
for column in ['Vol_call', 'Strike', 'Vol_put']:
    df[column] = df[column].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
    
df = df.loc[:, ['Fecha', 'Strike', 'Vol_call', 'Vol_put']]

df['Fecha'] = pd.to_datetime(df['Fecha'])

# Ordenar los datos primero por 'Fecha' y luego por 'Strike'
df = df.sort_values(by=['Fecha', 'Strike'])

# Resetear el índice del DataFrame
df = df.reset_index(drop=True)

# Reemplazar valores menores que 0.001 en 'Vol_call' y 'Vol_put' por NaN
df['Vol_call'] = df['Vol_call'].mask(df['Vol_call'] < 0.001, np.nan)
df['Vol_put'] = df['Vol_put'].mask(df['Vol_put'] < 0.001, np.nan)




# Crear un cliente S3
s3 = boto3.client('s3')

# Definir el nombre del bucket y la clave del archivo
bucket_name = 'miax-12-scrap-meff'
file_key = 'datos_futuros.json'

# Obtener el objeto S3
response = s3.get_object(Bucket=bucket_name, Key=file_key)

# Leer el contenido del objeto
file_content = response['Body'].read()

# Convertir bytes a un objeto similar a un archivo usando BytesIO
json_bytes = BytesIO(file_content)

# Cargar el contenido del objeto BytesIO en un DataFrame
df_futuro = pd.read_json(json_bytes)

precio_subyacente = df_futuro.loc[0, 'Ant']


print(f'Dataframe de volatilidades: {df}')

print(f'Precio subyacente {precio_subyacente}')