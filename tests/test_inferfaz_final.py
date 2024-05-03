import sys
import os
# Asegura que el directorio raíz del proyecto esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from freezegun import freeze_time
import pandas as pd
from interfaz_final import calcular_tiempo_a_madurez 


@freeze_time("2022-01-01")
def test_calcular_tiempo_a_madurez():
    # Crear un DataFrame de prueba
    data = {'Fecha': ['2022-01-31', '2022-12-31']}
    df = pd.DataFrame(data)

    # Llamar a la función que estamos probando
    result = calcular_tiempo_a_madurez(df)

    # Crear la serie esperada
    expected = pd.Series([0.0822, 1.0027], name='Maturity')  # Asegúrate de ajustar los valores esperados

    # Verificar que el resultado sea el esperado
    pd.testing.assert_series_equal(result, expected, rtol=1e-3)  # Ajusta la tolerancia según sea necesario