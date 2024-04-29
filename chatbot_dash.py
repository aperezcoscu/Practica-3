import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime

# Estilos para el contenedor de mensajes del chatbot
messages_container_style = {
    "display": "flex",
    "flex-direction": "column",
    "height": "300px",
    "overflow-y": "auto"
}

# Estilos para los botones y mensajes del chatbot
message_button_style = {
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

user_message_style = {
    'align-self': 'flex-end',
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
    'border-radius': '8px 8px 0px 8px',
    'max-width': '284px',
    'align-content': 'stretch',
    'flex-wrap': 'nowrap',
    'flex-direction': 'column',
    'margin-top': '5px',
    'font-size': '14px',
}

option_button_style = {
    'font-size': '12px',
    'margin': '2px 10px',  # Agrega márgenes a los lados
    'border': '1px solid #4a8eda',
    'background-color': 'white',
    'color': '#2a3f5f',
    'text-align': 'center',
    'border-radius': '10px',
    'cursor': 'pointer',
    'transition': 'background-color 0.3s, color 0.3s',
    'display': 'block',  # Permite que el botón sea tratado como bloque
    'width': '100%',  # El botón ocupa el 100% del ancho del contenedor
    'box-sizing': 'border-box',  # Asegura que el padding y border estén incluidos en el ancho
}

# Estilo para el contenedor de las opciones
options_container_style = {
    'display': 'flex',
    'flex-direction': 'column',
    'align-items': 'center',  # Asegura que los botones estén alineados al centro
    'justify-content': 'center',
    'gap': '5px',  # Ajusta el espacio entre botones
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
messages = []

app.layout = html.Div([
    dbc.Button("Chat", id="chatbot-toggle-button", className="btn-circle", n_clicks=0,
               style={"position": "fixed", "bottom": "15px", "right": "15px", "z-index": "1000000"}),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Volatility Chatbot")),
        dbc.ModalBody([
            html.Div(id="messages-container", style=messages_container_style, **{"data-last-update": "0"}),
            html.Div([
                dbc.Button("Explicar la sonrisa de volatilidad", id="option-call", n_clicks=0, style=option_button_style),
                dbc.Button("Importancia de la volatilidad implícita", id="option-put", n_clicks=0, style=option_button_style)
            ], id="options-container", style=options_container_style),
            html.Div([
                dbc.Button("Sí", id="more-info-yes", n_clicks=0, style=option_button_style),
                dbc.Button("No", id="more-info-no", n_clicks=0, style=option_button_style)
            ], id="more-info-options", style={"display": "none"})
        ]),
        dbc.ModalFooter()
    ], id="chatbot-container", is_open=False, style={"position": "fixed", "bottom": "90px", "right": "15px", "width": "350px"})
])

@app.callback(
    [Output("chatbot-container", "is_open"),
     Output("messages-container", "children"),
     Output("options-container", "style"),
     Output("more-info-options", "style"),
     Output("messages-container", "data-last-update")],
    [Input("chatbot-toggle-button", "n_clicks"),
     Input("option-call", "n_clicks"),
     Input("option-put", "n_clicks"),
     Input("more-info-yes", "n_clicks"),
     Input("more-info-no", "n_clicks")],
    [State("chatbot-container", "is_open")],
    prevent_initial_call=True
)
def manage_chatbot(chat_button_clicks, option_call_clicks, option_put_clicks, more_info_yes_clicks, more_info_no_clicks, is_open):
    global messages
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "chatbot-toggle-button":
        if is_open:
            messages = []  # Reiniciar mensajes
            return False, [], {"display": "none"}, {"display": "none"}, str(datetime.now().timestamp())
        else:
            welcome_message = dbc.Card(dbc.CardBody("Bienvenidos a nuestro chat sobre volatilidad implícita"), style=message_button_style)
            follow_up_message = dbc.Card(dbc.CardBody("¿En qué tema específico te gustaría profundizar?"), style=message_button_style)
            messages = [welcome_message, follow_up_message]
            return True, messages, {"display": "flex"}, {"display": "none"}, str(datetime.now().timestamp())

    elif button_id == "option-call":
        user_question_message = dbc.Card(dbc.CardBody("Explicar la sonrisa de volatilidad"), style=user_message_style)
        messages.append(user_question_message)
        bot_answer_message = dbc.Card(dbc.CardBody("La sonrisa de volatilidad es una curva en forma de U que muestra que las opciones ITM y OTM tienen mayor volatilidad implícita que las ATM."), style=message_button_style)
        messages.append(bot_answer_message)
        more_info_prompt = dbc.Card(dbc.CardBody("¿Deseas saber más sobre este tema o algún otro aspecto de la volatilidad implícita?"), style=message_button_style)
        messages.append(more_info_prompt)
        return True, messages, {"display": "none"}, {"display": "flex"}, str(datetime.now().timestamp())

    elif button_id == "option-put":
        user_question_message = dbc.Card(dbc.CardBody("Importancia de la volatilidad implícita"), style=user_message_style)
        messages.append(user_question_message)
        bot_answer_message = dbc.Card(dbc.CardBody("La volatilidad implícita es crucial porque afecta el precio de las opciones y proporciona estimaciones sobre futuras fluctuaciones del mercado."), style=message_button_style)
        messages.append(bot_answer_message)
        more_info_prompt = dbc.Card(dbc.CardBody("¿Deseas profundizar más en cómo se calcula o cómo utilizarla para trading?"), style=message_button_style)
        messages.append(more_info_prompt)
        return True, messages, {"display": "none"}, {"display": "flex"}, str(datetime.now().timestamp())

    elif button_id == "more-info-yes":
        yes_response = dbc.Card(dbc.CardBody("Sí"), style=user_message_style)
        messages.append(yes_response)
        info_request_message = dbc.Card(dbc.CardBody("De acuerdo, sobre qué tema desea informarse?"), style=message_button_style)
        messages.append(info_request_message)
        return True, messages, {"display": "flex"}, {"display": "none"}, str(datetime.now().timestamp())

    elif button_id == "more-info-no":
        no_response = dbc.Card(dbc.CardBody("No"), style=user_message_style)
        messages.append(no_response)
        goodbye_message = dbc.Card(dbc.CardBody("Gracias por utilizar nuestro chat sobre volatilidad implícita. ¡Hasta pronto!"), style=message_button_style)
        messages.append(goodbye_message)
        return True, messages, {"display": "none"}, {"display": "none"}, str(datetime.now().timestamp())

if __name__ == "__main__":
    app.run_server(debug=True)
