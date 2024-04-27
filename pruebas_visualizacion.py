## Interfaz moderna

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

# Estilos modernos para el sidebar
sidebar_style = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '16rem',
    'padding': '2rem 1rem',
    'background-color': '#2a3f5f',  # Gris azulado oscuro
    'color': 'white',
    'border-radius': '0 25px 25px 0'  # Bordes redondeados en el lado derecho
}

# Estilos para los botones
button_style = {
    'text-align': 'left',
    'border': 'none',
    'width': '100%',
    'padding': '0.75rem',
    'background-color': 'transparent',
    'color': 'white',
    'text-transform': 'none',
    'border-radius': '15px',
    'transition': 'background-color 0.3s, color 0.3s',
    'box-shadow': 'none'  # Eliminar sombra
}

active_button_style = {
    'text-align': 'left',
    'border': 'none',
    'width': '100%',
    'padding': '0.75rem',
    'background-color': '#4a8eda',  # Azul claro
    'color': 'white',
    'text-transform': 'none',
    'border-radius': '15px',
    'transition': 'background-color 0.3s, color 0.3s'
}

content_style = {
    'margin-left': '18rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
    'background-color': '#e9ecef',  # Gris claro
    'border-radius': '15px'  # Bordes redondeados
}

# Leer el archivo CSV
df = pd.read_csv('volatilidades.csv')
# Obtener fechas únicas para el dropdown
unique_dates = df['Fecha'].unique()

app.layout = html.Div([
    html.Div([
        html.H2('Perfil de volatilidad implícita', style={'margin-bottom': '30px'}),
        html.Hr(),
        html.P('Tipo de opción', style={'font-weight': 'bold'}),
        html.Button('Opciones Call', id='btn-call', n_clicks=0, style=button_style),
        html.Button('Opciones Put', id='btn-put', n_clicks=0, style=button_style),
        html.Hr(),
        html.P('Superficie de volatilidad', style={'font-weight': 'bold'}),
    ], style=sidebar_style),

    # Área de contenido principal que incluye el desplegable y el gráfico
    html.Div([
        # Menú desplegable para seleccionar fecha con etiqueta
        html.Div([
            html.Label('Escoge la fecha a visualizar:', style={'margin-right': '10px', 'color': 'black'}),
            dcc.Dropdown(
                id='date-picker',
                options=[{'label': date, 'value': date} for date in unique_dates],
                value=unique_dates[0],  # Valor inicial
                style={'width': '300px', 'border-radius': '10px'}
            )
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '20px', 'margin-left': '10px'}),

        # Espacio para el gráfico dinámico
        dcc.Graph(id='volatility-graph', style={'margin-top': '10px'})
    ], style=content_style)
])

# Callback para cambiar el estilo del botón, mostrar gráficos correspondientes y filtrar por fecha
@app.callback(
    [Output('btn-call', 'style'),
     Output('btn-put', 'style'),
     Output('volatility-graph', 'figure')],
    [Input('btn-call', 'n_clicks'),
     Input('btn-put', 'n_clicks'),
     Input('date-picker', 'value')],
    [State('btn-call', 'style'),
     State('btn-put', 'style')]
)
def update_content(call_clicks, put_clicks, selected_date, call_style, put_style):
    ctx = dash.callback_context

    # Identificar el botón que fue presionado
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-call'

    # Filtrar el dataframe por la fecha seleccionada
    filtered_df = df[df['Fecha'] == selected_date]

    if button_id == 'btn-call':
        fig = px.line(filtered_df, x='Strike', y='Vol_call', title='Volatilidad de Call en función del Strike',
                      markers=True)
        # Establecer estilo activo para Call y inactivo para Put
        call_style = active_button_style
        put_style = button_style
    else:
        fig = px.line(filtered_df, x='Strike', y='Vol_put', title='Volatilidad de Put en función del Strike',
                      markers=True)
        # Establecer estilo activo para Put y inactivo para Call
        call_style = button_style
        put_style = active_button_style

    # Actualizar el estilo del gráfico para que tenga líneas en los ejes X e Y
    fig.update_layout(
        xaxis=dict(
            showline=True,  # Mostrar la línea del eje x
            linecolor='black',  # Color de la línea del eje x
            linewidth=1,  # Grosor de la línea del eje x
            showgrid=True,  # Mostrar las líneas de la cuadrícula en el eje x
            showticklabels=True,
            ticks='outside',
            gridcolor='lightgrey'  # Color de las líneas de la cuadrícula del eje x
        ),
        yaxis=dict(
            showline=True,  # Mostrar la línea del eje y
            linecolor='black',  # Color de la línea del eje y
            linewidth=1,  # Grosor de la línea del eje y
            showgrid=True,  # Mostrar las líneas de la cuadrícula en el eje y
            showticklabels=True,
            ticks='outside',
            gridcolor='lightgrey'  # Color de las líneas de la cuadrícula del eje y
        ),
        plot_bgcolor='white'  # Fondo blanco para el área del gráfico
    )

    return [call_style, put_style, fig]

if __name__ == '__main__':
    app.run_server(debug=True)