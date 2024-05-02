import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px

def calcular_tiempo_a_madurez(df):
    """
    Calcula el tiempo hasta la madurez desde la fecha actual hasta las fechas en la columna 'Fecha' del DataFrame dado.
    La función retorna una columna con los tiempos calculados.

    Args:
        df (pd.DataFrame): DataFrame que contiene una columna 'Fecha' con las fechas de expiración.

    Returns:
        pd.Series: Serie con los tiempos hasta la madurez en años.
    """
    df_temp = df.copy()  # Trabajar con una copia para evitar efectos secundarios en el DataFrame original
    df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha'])
    fecha_base = pd.Timestamp(datetime.now().date())
    return (df_temp['Fecha'] - fecha_base).dt.days / 365.25

def preparar_datos(df, precio_subyacente, tipo_opcion):
    """
    Prepara los datos para la interpolación necesaria para crear una superficie de volatilidad.

    Args:
        df (pd.DataFrame): DataFrame con las columnas 'Fecha', 'Strike', 'Vol_call', y 'Vol_put'.
        precio_subyacente (float): Precio actual del activo subyacente para calcular el Moneyness.
        tipo_opcion (str): Tipo de opción, 'call' o 'put'.

    Returns:
        tuple: Contiene tres arrays numpy que representan la malla de Tiempo a Madurez (T),
               Moneyness (M) y los valores interpolados de Volatilidad Implícita (IV).
    """
    # Calcula la madurez y asigna a la columna 'Maturity'
    df['Maturity'] = calcular_tiempo_a_madurez(df)
    
    # Calcula el Moneyness
    df['Moneyness'] = df['Strike'] / precio_subyacente
    
    # Selecciona la volatilidad según el tipo de opción y asegura no trabajar en copias
    if tipo_opcion == 'call':
        df = df.dropna(subset=['Vol_call']).copy()
        df.loc[:, 'VolatilidadImplicita'] = df['Vol_call']
    elif tipo_opcion == 'put':
        df = df.dropna(subset=['Vol_put']).copy()
        df.loc[:, 'VolatilidadImplicita'] = df['Vol_put']
    
    # Agrupa por 'Maturity' y 'Moneyness' y calcula la media de la volatilidad implícita
    df_agrupado = df.groupby(['Maturity', 'Moneyness'], as_index=False)['VolatilidadImplicita'].mean()

    # Prepara los datos para la interpolación
    Maturity = np.linspace(df_agrupado['Maturity'].min(), df_agrupado['Maturity'].max(), 100)
    Moneyness = np.linspace(df_agrupado['Moneyness'].min(), df_agrupado['Moneyness'].max(), 100)
    T_grid, M_grid = np.meshgrid(Maturity, Moneyness)

    # Interpolación para crear la superficie de volatilidad
    IV_grid = griddata(
        (df_agrupado['Maturity'].values, df_agrupado['Moneyness'].values),
        df_agrupado['VolatilidadImplicita'].values,
        (T_grid, M_grid),
        method='cubic'
    )

    return T_grid, M_grid, IV_grid

def plot_surface(X, Y, Z, title='Superficie de Volatilidad'):
    """
    Crea y muestra un gráfico de superficie usando Plotly.

    Args:
    X (array-like): Coordenadas X de la malla de la superficie, 
    representando el tiempo de madurez.
    Y (array-like): Coordenadas Y de la malla de la superficie, 
    representando la moneidad.
    Z (array-like): Valores de la superficie (elevación) para 
    cada par (X, Y), representando la volatilidad implícita.
    title (str): Título del gráfico.

    Returns:
    None - Muestra un gráfico interactivo.
    """
    # Crear el objeto figura y añadir la superficie
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='RdBu', cmin=Z.min(), cmax=Z.max())])
    
    # Personalizar la apariencia del gráfico
    fig.update_layout(
        title=title,
        autosize=False,
        width=600,
        height=600,
        scene=dict(
            xaxis=dict(title='Maturity Time', 
                       backgroundcolor="rgb(200, 200, 230)", 
                       gridcolor="white", 
                       showbackground=True, 
                       zerolinecolor="white", 
                       tickfont=dict(size=12)),
            
            yaxis=dict(title='Moneyness', 
                       backgroundcolor="rgb(230, 200,230)", 
                       gridcolor="white", 
                       showbackground=True, 
                       zerolinecolor="white", 
                       tickfont=dict(size=12)),
            
            zaxis=dict(title='Volatilidad Implícita', 
                       backgroundcolor="rgb(230, 230,200)", 
                       gridcolor="white", 
                       showbackground=True, 
                       zerolinecolor="white", 
                       tickfont=dict(size=12)),
            camera_eye=dict(x=1.5, y=1.5, z=0.5)
        ),
        margin=dict(l=65, r=50, b=65, t=90),
        
        paper_bgcolor='rgb(243, 243, 243)',
        
        font=dict(family="Arial, sans-serif", 
                  size=12, 
                  color="darkblue")
    )

    # Ajustes de iluminación para mejorar el aspecto tridimensional
    fig.update_traces(lighting=dict(ambient=0.3, diffuse=0.7, fresnel=0.1, specular=0.5, roughness=0.5))
    
    fig.show()


# Ejemplo de uso:
df = pd.read_csv('volatilidades.csv')
precio_subyacente = 11123.70  # Este valor debe ser el precio actual del subyacente


T_call, M_call, IV_call = preparar_datos(df, precio_subyacente, 'call')


call_surface = plot_surface(T_call, M_call, IV_call)
