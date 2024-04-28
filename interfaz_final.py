## Interfaz moderna

import dash
from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Establecer estilos de la aplicación y componentes externos
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


# Estilos modernos para el sidebar y botones
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


# Estilos chatbot

# Estilos para el contenedor de mensajes del chatbot
messages_container_style = {
    "display": "flex",
    "flex-direction": "column",
    "height": "300px",
    "overflow-y": "auto"
}


message_button_style =  {
    'font-size': '14px',
    'margin': '5px',
    'position': 'relative',
    'word-break': 'break-word',
    'box-sizing': 'border-box',
    'border-style': 'solid',
    'border-width': '0px',
    'border-color': 'rgb(31, 57, 85)',
    'background-color': 'rgb(234, 240, 246)',
    'color': 'rgb(59, 67, 75)',
    'display': 'inline-flex',
    'align-items': 'flex-start',
    'flex-direction': 'column',
    'border-radius': '0px 8px 8px 8px',
}

option_button_style = {
    'font-size': '16px',  # Tamaño de la fuente
    'margin': '2px',  # Eliminar margen para evitar separación del borde izquierdo
    'border': '1px solid #4a8eda',  # Borde con color azul claro
    'background-color': 'white',  # Fondo blanco
    'color': '#2a3f5f',  # Texto en gris azulado oscuro
    'text-align': 'left',  # Alineación del texto a la izquierda
    'border-radius': '10px',  # Bordes redondeados
    'cursor': 'pointer',  # Cursor en forma de puntero para indicar que es clickeable
    'transition': 'background-color 0.3s, color 0.3s',  # Transición suave para el color de fondo y texto
    'display': 'inline-block',  # Display como bloque en línea para ajustar el ancho al contenido
    'white-space': 'nowrap'  # Evitar que el texto se envuelva a una nueva línea
}


user_message_style = {
    'align-self': 'flex-end',  # Alinea el mensaje a la derecha en el contenedor flex
    'position': 'relative',
    'word-break': 'break-all',
    'box-sizing': 'border-box',
    'border-style': 'solid',
    'border-width': '0px',
    'border-color': 'rgba(0, 0, 0, 0.2)',
    'background-color': 'rgb(46, 71, 93)',
    'color': 'rgb(255, 255, 255)',
    'display': 'inline-flex',
    'align-items': 'flex-start',
    'border-radius': '8px 8px 0px 8px',  # Cambiar el borde redondeado
    'max-width': '284px',
    'align-content': 'stretch',
    'flex-wrap': 'nowrap',
    'flex-direction': 'column',
    'margin-top': '5px',
    'font-size': '14px',
}

# Leer el archivo CSV
df = pd.read_csv('volatilidades.csv')
unique_dates = df['Fecha'].unique()

# Asumiendo que 'messages' es una variable global o de sesión que almacena los mensajes
messages = []

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
    html.Div([
        html.Div([
            html.Label('Escoge la fecha a visualizar:', style={'margin-right': '10px', 'color': 'black'}),
            dcc.Dropdown(
                id='date-picker',
                options=[{'label': date, 'value': date} for date in unique_dates],
                value=unique_dates[0],
                style={'width': '300px', 'border-radius': '10px'}
            )
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '20px', 'margin-left': '10px'}),
        dcc.Graph(id='volatility-graph', style={'margin-top': '10px'})
    ], style=content_style),
    
    # Elementos del Chatbot
    dbc.Button("Chat", id="chatbot-toggle-button", className="btn-circle", n_clicks=0, style={"position": "fixed", "bottom": "15px", "right": "15px", "z-index": "1000000"}),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Chat con GVC Bot")),
        dbc.ModalBody([
            html.Div(id="messages-container", style=messages_container_style),
            html.Div([
                dbc.Button("Qué es una call", id="option-call", n_clicks=0, style=option_button_style),
                dbc.Button("Qué es una put", id="option-put", n_clicks=0, style=option_button_style)
            ], id="options-container", style={"display": "flex", "flex-direction": "column"})
        ]),
        dbc.ModalFooter(dbc.Input(placeholder="Escribe un mensaje aquí", type="text", id="user-input-text")),
    ], id="chatbot-container", is_open=False, style={"position": "fixed", "bottom": "90px", "right": "15px", "width": "350px"})
])

# Callbacks de la aplicación
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


# Callbacks para el chatbot
@app.callback(
    Output("chatbot-container", "is_open"),
    Output("messages-container", "children"),
    Output("options-container", "children"),
    Input("chatbot-toggle-button", "n_clicks"),
    Input("option-call", "n_clicks"),
    Input("option-put", "n_clicks"),
    State("chatbot-container", "is_open")
)

def manage_chatbot(chat_button_clicks, option_call_clicks, option_put_clicks, is_open):
    global messages
    ctx = dash.callback_context
    
    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "chatbot-toggle-button" and chat_button_clicks:
        welcome_message = dbc.Card(dbc.CardBody("Bienvenidos a la visualización de datos"), style=message_button_style)
        follow_up_message = dbc.Card(dbc.CardBody("¿En qué puedo ayudaros?"), style=message_button_style)
        messages = [welcome_message, follow_up_message]  # Iniciar mensajes
        options = [
            dbc.Button("Qué es una call", id="option-call", style=option_button_style),
            dbc.Button("Qué es una put", id="option-put", style=option_button_style)
        ]
        return not is_open, messages, options

    elif button_id in ["option-call", "option-put"]:
        user_query = "Una call es una opción de compra" if button_id == "option-call" else "Una put es una opción de venta"
        button_text = "Qué es una call" if button_id == "option-call" else "Qué es una put"
        user_button_message = dbc.Card(dbc.CardBody(button_text), style=user_message_style)
        bot_response_message = dbc.Card(dbc.CardBody(user_query), style=message_button_style)
        messages.append(user_button_message)  # Agrega el texto del botón como mensaje del usuario
        messages.append(bot_response_message)  # Agrega la respuesta del bot
        options = []  # Vacía las opciones después de la selección
        return True, messages, options

    # Si no se presionó ninguno de los botones designados, simplemente devuelve el estado actual
    return is_open, messages, dash.no_update

# Ejecución del servidor
if __name__ == "__main__":
    app.run_server(debug=True)