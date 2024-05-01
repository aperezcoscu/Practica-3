import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go
from datetime import datetime

def calcular_tiempo_a_madurez(fechas, fecha_base):
    """
    Calcula el tiempo hasta la madurez desde una fecha base hasta las fechas dadas.

    Args:
        fechas (pd.Series): Serie de fechas de expiración.
        fecha_base (datetime): Fecha desde la cual calcular el tiempo a madurez.

    Returns:
        np.array: Array de tiempos a madurez en años.
    """
    fechas = pd.to_datetime(fechas)
    # Calcula la diferencia en días y convierte a años
    return ((fechas - fecha_base) / np.timedelta64(1, 'D') / 365.25).values


def preparar_datos(df, precio_subyacente, fecha_base=datetime.today()):
    """
    Prepara los datos para la interpolación necesaria para crear una superficie de volatilidad.

    Args:
        df (pd.DataFrame): DataFrame con las columnas 'Fecha', 'Strike', 'Vol_call' o 'Vol_put'.
        precio_subyacente (float): Precio actual del activo subyacente para calcular el Moneyness.
        fecha_base (datetime): Fecha de referencia para el cálculo de la madurez.

    Returns:
        tuple: Contiene tres arrays numpy que representan la malla de Tiempo a Madurez (T),
               Moneyness (M) y los valores interpolados de Volatilidad Implícita (IV).
    """
    df['TiempoAMadurez'] = calcular_tiempo_a_madurez(df['Fecha'], fecha_base)
    df['Moneyness'] = df['Strike'] / precio_subyacente
    df['VolatilidadImplicita'] = df['Vol_call'].fillna(df['Vol_put'])  # Asumiendo que quieres usar Vol_call o Vol_put donde esté disponible

    df_agrupado = df.groupby(['TiempoAMadurez', 'Moneyness'], as_index=False)['VolatilidadImplicita'].mean()

    TiempoAMadurez = np.linspace(df_agrupado['TiempoAMadurez'].min(), df_agrupado['TiempoAMadurez'].max(), 100)
    Moneyness = np.linspace(df_agrupado['Moneyness'].min(), df_agrupado['Moneyness'].max(), 100)
    T_grid, M_grid = np.meshgrid(TiempoAMadurez, Moneyness)

    IV_grid = griddata(
        (df_agrupado['TiempoAMadurez'].values, df_agrupado['Moneyness'].values),
        df_agrupado['VolatilidadImplicita'].values,
        (T_grid, M_grid),
        method='cubic'
    )

    return T_grid, M_grid, IV_grid

def pintar_superficie(X, Y, Z):
    """
    Pinta una superficie 3D de volatilidad implícita.
    """
    fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z)])
    fig.update_layout(
        title='Superficie de Volatilidad Implícita',
        scene=dict(
            xaxis_title='Tiempo a Madurez',
            yaxis_title='Moneyness',
            zaxis_title='Volatilidad Implícita',
        ),
        autosize=True
    )
    fig.show()

# Ejemplo de uso:
df = pd.read_csv('volatilidades.csv')
precio_subyacente = 11000  # Este valor debe ser el precio actual del subyacente
T, M, IV = preparar_datos(df, precio_subyacente)
pintar_superficie(T, M, IV)
