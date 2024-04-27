## Minimalista, colores básicos


import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

# Estilos para el sidebar
sidebar_style = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '16rem',
    'padding': '2rem 1rem',
    'background-color': '#f8f9fa'
}

# Estilos para los botones
button_style = {
    'text-align': 'left',
    'border': 'none',
    'width': '100%',
    'padding': '0.75rem',
    'background-color': 'transparent',
    'text-transform': 'none',
    'border-radius': '15px',
    'transition': 'background-color 0.3s, color 0.3s'
}

active_button_style = {
    'text-align': 'left',
    'border': 'none',
    'width': '100%',
    'padding': '0.75rem',
    'background-color': '#63A6EE',
    'color': 'white',
    'text-transform': 'none',
    'border-radius': '15px',
    'transition': 'background-color 0.3s, color 0.3s'
}

content_style = {
    'margin-left': '18rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
}

# Leer el archivo CSV
df = pd.read_csv('volatilidades.csv')
# Obtener fechas únicas para el dropdown
unique_dates = df['Fecha'].unique()

app.layout = html.Div([
    html.Div([
        html.H2('Perfil de volatilidad impl', style={'margin-bottom': '30px'}),
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
            html.Label('Escoge la fecha a visualizar:', style={'margin-right': '10px'}),
            dcc.Dropdown(
                id='date-picker',
                options=[{'label': date, 'value': date} for date in unique_dates],
                value=unique_dates[0],  # Valor inicial
                style={'width': '300px'}
            )
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '20px', 'margin-left': '10px'}),

        # Espacio para el gráfico dinámico
        dcc.Graph(id='volatility-graph', style={'margin-top': '10px'})
    ], style={'margin-left': '18rem', 'padding': '2rem 1rem'})
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
                      markers=True)  # Agregar marcadores
        return [active_button_style, button_style, fig]
    else:
        fig = px.line(filtered_df, x='Strike', y='Vol_put', title='Volatilidad de Put en función del Strike',
                      markers=True)  # Agregar marcadores
        return [button_style, active_button_style, fig]
    
if __name__ == '__main__':
    app.run_server(debug=True)
