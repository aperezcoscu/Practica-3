import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import boto3


# URL de la página a hacer scraping
url = 'https://www.meff.es/esp/Derivados-Financieros/Ficha/FIEM_MiniIbex_35'

# Realizar la petición HTTP GET a la página
response = requests.get(url)

def obtener_dataframe(response, tipo_tabla):
    """
    Realiza el web scraping y devuelve un dataframe con los datos obtenidos,
    dependiendo si el tipo de tabla es 'opciones' o 'futuros'.    
    Args:
    - response: La respuesta HTTP obtenida.
    - tipo_tabla: Tipo de la tabla a buscar ('opciones' o 'futuros').
    Returns:
    - Un dataframe con los datos de la tabla.
    """
    # Determinar el ID de la tabla y si se necesita manejar el atributo data-tipo
    if tipo_tabla == 'opciones':
        id_tabla = 'tblOpciones'
        es_opcion = True
    elif tipo_tabla == 'futuros':
        id_tabla = 'Contenido_Contenido_tblFuturos'
        es_opcion = False
    else:
        print("Tipo de tabla no soportado.")
        return pd.DataFrame()
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', id=id_tabla)
        all_rows_data = []
        
        if table:
            rows = table.find_all('tr', class_='text-right')
            
            for row in rows:
                cells = row.find_all('td')
                row_data = [cell.text.strip() for cell in cells]
                
                if es_opcion:
                    data_tipo = row.get('data-tipo', 'No especificado')
                    row_data.insert(0, data_tipo)
                    
                all_rows_data.append(row_data)
                
            return pd.DataFrame(all_rows_data)
        else:
            print('No se encontró la tabla con el id especificado.')
            return pd.DataFrame()
    else:
        print('Error al realizar la petición HTTP:', response.status_code)
        return pd.DataFrame()
    
    
def tratar_dataframe(df, tipo_tabla):
    """
    Transforma el dataframe según si es de opciones o de futuros.
    
    Args:
    - df: Dataframe a transformar.
    - tipo_tabla: Tipo de la tabla ('opciones' o 'futuros').
    
    Returns:
    - Un dataframe transformado.
    """
    if tipo_tabla == 'opciones':
        # Especificar los nombres de columna para opciones
        df.columns = ['Class', 'Strike', 'Buy_ord', 'Buy_vol', 'Buy_price', 'Sell_price', 'Sell_vol', 'Sell_ord', 'Ult', 'Vol', 'Aper', 'Max.', 'Min.', 'Ant']
        df['Tipo'] = df['Class'].str[:3]
        df['Fecha'] = pd.to_datetime(df['Class'].str[3:], format='%Y%m%d').dt.strftime('%Y-%m-%d')
        df.drop(['Class'], axis=1, inplace=True)
        
        # Transformaciones adicionales para opciones
        df['Strike'] = df['Strike'].apply(lambda x: float(x.replace('.', '').replace(',', '.')))
        df['Ant'] = df['Ant'].apply(lambda x: pd.to_numeric(x.replace('.', '').replace(',', '.'), errors='coerce'))
        df['Buy_price'] = df['Buy_price'].apply(lambda x: pd.to_numeric(x.replace('.', '').replace(',', '.'), errors='coerce'))
        df['Sell_price'] = df['Sell_price'].apply(lambda x: pd.to_numeric(x.replace('.', '').replace(',', '.'), errors='coerce'))

        # Seleccionando solo las columnas deseadas para opciones
        df = df[['Tipo', 'Fecha', 'Strike', 'Buy_price', 'Sell_price', 'Ant']]
        
    elif tipo_tabla == 'futuros':
        # Especificar los nombres de columna para futuros
        df.columns = ['Vencimiento', 'Tipo', 'Buy_ord', 'Buy_vol', 'Buy_price', 'Sell_price', 'Sell_vol', 'Sell_ord', 'Ult', 'Vol', 'Aper', 'Max.', 'Min.','Ant']
        
        # Clean up the date string if necessary
        df['Vencimiento'] = df['Vencimiento'].str.replace('.', '')  # Remove periods if present
        df['Vencimiento'] = pd.to_datetime(df['Vencimiento'], format='%d %b %Y', errors='coerce')
        df['Ant'] = pd.to_numeric(df['Ant'].str.replace('.', '').str.replace(',', '.'), errors='coerce')
        
        # Seleccionando solo las columnas deseadas para futuros
        df = df.loc[:, ['Vencimiento', 'Ant']]
        
    else:
        print("Tipo de tabla no soportado.")
        return pd.DataFrame()
    
    return df


def calcular_precio_opcion(row, tipo):
    """
    Calcula el precio de la opción, ya sea 'call' o 'put'.
    
    Args:
    - row: La fila del DataFrame.
    - tipo: Tipo de opción ('call' o 'put').
    
    Returns:
    - Precio calculado de la opción.
    """
    if tipo == 'call':
        buy_col = 'Buy_price_call'
        sell_col = 'Sell_price_call'
        ant_col = 'Ant_call'
    elif tipo == 'put':
        buy_col = 'Buy_price_put'
        sell_col = 'Sell_price_put'
        ant_col = 'Ant_put'
    else:
        raise ValueError("Tipo de opción no soportado. Use 'call' o 'put'.")

    # Usar 'Ant_call' o 'Ant_put' si ambas columnas de precios son NA
    if pd.isna(row[buy_col]) and pd.isna(row[sell_col]):
        return row[ant_col]
    elif pd.notna(row[buy_col]) and pd.notna(row[sell_col]):
        return (row[buy_col] + row[sell_col]) / 2
    elif pd.notna(row[buy_col]):
        return row[buy_col]
    elif pd.notna(row[sell_col]):
        return row[sell_col]
    else:
        return None

    
def datos_opciones(tipo_tabla, response):
    df = obtener_dataframe(response, tipo_tabla)
    df = tratar_dataframe(df, tipo_tabla)
    
    df_c = df[df['Tipo'] == 'OCE'].copy()
    df_p = df[df['Tipo'] == 'OPE'].copy()

    df_c.rename(columns={'Buy_price': 'Buy_price_call', 'Sell_price': 'Sell_price_call', 'Ant': 'Ant_call'}, inplace=True)
    df_p.rename(columns={'Buy_price': 'Buy_price_put', 'Sell_price': 'Sell_price_put', 'Ant': 'Ant_put'}, inplace=True)
    
    # Unir los dataframes por 'Fecha' y 'Strike'
    df_final = pd.merge(df_c, df_p, on=['Fecha', 'Strike'], how='outer')

    # Ordenar por 'Fecha' y 'Strike'
    df_final.sort_values(by=['Fecha', 'Strike'], ascending=[True, True], inplace=True)
    
    # Calcular la columna 'T' en el DataFrame
    df_final['T'] = (pd.to_datetime(df_final['Fecha']) - pd.Timestamp(datetime.now().date())).dt.days / 365.25

    # Aplicar la función para calcular las columnas 'Precio_call' y 'Precio_put'
    df_final['Precio_call'] = df_final.apply(lambda row: calcular_precio_opcion(row, 'call'), axis=1)
    df_final['Precio_put'] = df_final.apply(lambda row: calcular_precio_opcion(row, 'put'), axis=1)

    return df_final


def datos_futuros(tipo_tabla, response):
    df = obtener_dataframe(response, 'futuros')
    df = tratar_dataframe(df, 'futuros')
    return df


# Cliente de S3
s3_client = boto3.client('s3')

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
        print(f'Datos almacenados correctamente en {bucket_name}/{object_name} y deployment realizado')
    except Exception as e:
        print(f'Se ha producido un error: {e}')


def lambda_handler(event, context):
    url = 'https://www.meff.es/esp/Derivados-Financieros/Ficha/FIEM_MiniIbex_35'
    response = requests.get(url)
    
    if response.status_code == 200:
        # Opciones
        df_opciones = datos_opciones('opciones', response)
        
        # Futuros
        df_futuros = datos_futuros('futuros', response)
        
        # Convertir DataFrames a JSON
        opciones_json = df_opciones.to_json(orient='records')
        futuros_json = df_futuros.to_json(orient='records')
        
        # Nombre del bucket y los objetos en S3
        bucket_name = 'miax-12-scrap-meff'
        opciones_object_name = 'datos_opciones.json'
        futuros_object_name = 'datos_futuros.json'
        
        # Subir a S3
        subir_a_s3(opciones_json, bucket_name, opciones_object_name)
        subir_a_s3(futuros_json, bucket_name, futuros_object_name)
        return {
            'statusCode': 200,
            'body': json.dumps('Datos subidos a S3 correctamente y deployment realizado')
        }
    else:
        return {
            'statusCode': response.status_code,
            'body': json.dumps('Error al realizar el web scraping')
        }


if __name__ == "__main__":
    print(lambda_handler({}, {}))