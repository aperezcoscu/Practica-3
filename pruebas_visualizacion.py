import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

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

# Estilos para los botones normales
button_style = {
    'text-align': 'left',
    'border': 'none',
    'width': '100%',
    'padding': '0.75rem',
    'background-color': 'transparent',
    'text-transform': 'none',
    'border-radius': '15px',  # Agregamos bordes redondeados
    'transition': 'background-color 0.3s, color 0.3s'  # Agregamos transiciones suaves
}

# Estilos para el botón activo
active_button_style = {
    'text-align': 'left',
    'border': 'none',
    'width': '100%',
    'padding': '0.75rem',
    'background-color': '#63A6EE',
    'color': 'white',
    'text-transform': 'none',
    'border-radius': '15px',  # Consistente con los bordes redondeados
    'transition': 'background-color 0.3s, color 0.3s'  # Transiciones suaves
}

# Estilos para el contenido principal
content_style = {
    'margin-left': '18rem',
    'margin-right': '2rem',
    'padding': '2rem 1rem',
}

# Contenido principal inicial
initial_content = html.Div(id='content-area', children=[
    html.H1('Datos macroeconómicos', id='main-title')
], style=content_style)

app.layout = html.Div([
    html.Div([
        html.H2('Visualización de datos', style={'margin-bottom': '30px'}),
        html.Hr(),
        html.P('Europa', style={'font-weight': 'bold'}),
        html.Button('Opciones Call', id='btn-call', n_clicks=0, style=button_style),
        html.Button('Opciones Put', id='btn-put', n_clicks=0, style=button_style),
        html.Hr(),
        html.P('Serie de datos mundiales', style={'font-weight': 'bold'}),
    ], style=sidebar_style),

    initial_content
])

# Callback para cambiar el estilo del botón activo y actualizar el título
@app.callback(
    [Output('btn-call', 'style'),
     Output('btn-put', 'style'),
     Output('main-title', 'children')],
    [Input('btn-call', 'n_clicks'),
     Input('btn-put', 'n_clicks')],
    [State('btn-call', 'style'),
     State('btn-put', 'style')]
)
def update_button_style(call_clicks, put_clicks, call_style, put_style):
    ctx = dash.callback_context

    if not ctx.triggered:
        return [button_style, button_style, 'Datos macroeconómicos']
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-call':
        return [active_button_style, button_style, 'Observaciones de calls']
    elif button_id == 'btn-put':
        return [button_style, active_button_style, 'Observaciones de puts']

    return [button_style, button_style, 'Datos macroeconómicos']

if __name__ == '__main__':
    app.run_server(debug=True)
