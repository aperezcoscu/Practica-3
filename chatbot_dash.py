import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


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




# Inicialización de la aplicación Dash con `suppress_callback_exceptions` habilitado
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
messages = []

# Establecer la estructura inicial de la aplicación con todos los componentes necesarios.
app.layout = html.Div([
    dbc.Button("Chat", id="chatbot-toggle-button", className="btn-circle", n_clicks=0,
               style={"position": "fixed", "bottom": "15px", "right": "15px", "z-index": "1000000"}),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Chat con GVC Bot")),
        dbc.ModalBody([
            html.Div(id="messages-container", style=messages_container_style),
            html.Div([
                dbc.Button("Qué es una call", id="option-call", n_clicks=0, style=option_button_style),
                dbc.Button("Qué es una put", id="option-put", n_clicks=0, style=option_button_style)
            ], id="options-container", style={"display": "none"})  # Inicialmente oculto
        ]),
        dbc.ModalFooter()
    ], id="chatbot-container", is_open=False, style={"position": "fixed", "bottom": "90px", "right": "15px", "width": "350px"})
])

# Ajusta el callback para manejar la visibilidad de los botones y para restablecer el chat correctamente.
@app.callback(
    [Output("chatbot-container", "is_open"),
     Output("messages-container", "children"),
     Output("options-container", "style")],  # Cambiar la visibilidad de los botones mediante el estilo
    [Input("chatbot-toggle-button", "n_clicks"),
     Input("option-call", "n_clicks"),
     Input("option-put", "n_clicks")],
    State("chatbot-container", "is_open"),
    prevent_initial_call=True
)
def manage_chatbot(chat_button_clicks, option_call_clicks, option_put_clicks, is_open):
    global messages
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "chatbot-toggle-button":
        if is_open:
            messages = []  # Reiniciar mensajes
            return False, [], {"display": "none"}  # Cerrar chat y ocultar botones
        else:
            # Mensajes de bienvenida
            welcome_message = dbc.Card(dbc.CardBody("Bienvenidos a la visualización de datos"), style=message_button_style)
            follow_up_message = dbc.Card(dbc.CardBody("¿En qué puedo ayudaros?"), style=message_button_style)
            messages = [welcome_message, follow_up_message]
            return True, messages, {"display": "flex"}  # Mostrar chat y mostrar botones

    elif button_id in ["option-call", "option-put"]:
        user_query = "Una call es una opción de compra" if button_id == "option-call" else "Una put es una opción de venta"
        button_text = "Qué es una call" if button_id == "option-call" else "Qué es una put"
        user_button_message = dbc.Card(dbc.CardBody(button_text), style=user_message_style)
        bot_response_message = dbc.Card(dbc.CardBody(user_query), style=message_button_style)
        messages.append(user_button_message)
        messages.append(bot_response_message)
        return True, messages, {"display": "none"}  # Mantener el chat abierto y ocultar botones

    return is_open, messages, dash.no_update


# Ejecución del servidor
if __name__ == "__main__":
    app.run_server(debug=True)
