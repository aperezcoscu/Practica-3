import requests
import pandas as pd

def datos_dynamodb(url):
    """Función para obtener datos desde la API y retornarlos como un DataFrame."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanzará un error si la respuesta de la API no es exitosa
        data = response.json()
        return pd.DataFrame(data)
    except requests.RequestException as e:
        print(f"Error al hacer la solicitud a la API: {e}")
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




def main():
    # URL de la API - Cambia esto por la URL real de tu API
    api_url = "http://localhost:8000/volatilities/"
    
    # Obtener los datos de la API
    df = datos_dynamodb(api_url)
    
    # Imprimir los datos recibidos
    if not df.empty:
        print("Datos recibidos desde la API:")
        print(df)
    else:
        print("No se recibieron datos desde la API o hubo un error.")
        
        
    api_futuros = "http://localhost:8000/datos-futuros"
        # Obtener los datos de la API de futuros
    df_futuros = datos_s3(api_futuros)
    
    # Imprimir los datos recibidos
    if not df_futuros.empty:
        print("Datos recibidos desde la API de futuros:")
        print(df_futuros)
    else:
        print("No se recibieron datos desde la API de futuros o hubo un error.")

if __name__ == "__main__":
    main()
