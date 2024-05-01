import pandas as pd
import plotly.graph_objects as go

# Cargar los datos
df = pd.read_csv('volatilidades.csv')

# Convertir la fecha a tipo fecha y asegurarse de que Strike sea un flotante
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Strike'] = df['Strike'].astype(float)

# Preparar datos para gráficos de superficie
df_pivot_call = df.pivot_table(index='Fecha', columns='Strike', values='Vol_call')
df_pivot_put = df.pivot_table(index='Fecha', columns='Strike', values='Vol_put')

# Crear gráfico de superficie para Call Options
fig_call = go.Figure(data=[go.Surface(z=df_pivot_call.values, x=df_pivot_call.columns, y=df_pivot_call.index)])
fig_call.update_layout(title='Superficie de Volatilidad para Call Options', autosize=True)
fig_call.update_layout(scene = dict(
                    xaxis_title='Strike',
                    yaxis_title='Fecha',
                    zaxis_title='Volatilidad Call'))

# Crear gráfico de superficie para Put Options
fig_put = go.Figure(data=[go.Surface(z=df_pivot_put.values, x=df_pivot_put.columns, y=df_pivot_put.index)])
fig_put.update_layout(title='Superficie de Volatilidad para Put Options', autosize=True)
fig_put.update_layout(scene = dict(
                    xaxis_title='Strike',
                    yaxis_title='Fecha',
                    zaxis_title='Volatilidad Put'))

# Mostrar los gráficos
fig_call.show()
fig_put.show()