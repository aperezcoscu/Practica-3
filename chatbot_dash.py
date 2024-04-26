import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc

# Inicialización de la aplicación Dash con `suppress_callback_exceptions` habilitado
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Definición de la estructura de la aplicación
app.layout = html.Div([
    dbc.Button("Chat", id="chatbot-toggle-button", className="btn-circle", n_clicks=0, style={"position": "fixed", "bottom": "15px", "right": "15px", "z-index": "1000000"}),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Chat con GVC Bot")),
        dbc.ModalBody([
            html.Div(id="messages-container", style={"height": "300px", "overflow-y": "auto"}),
            html.Div([
                dbc.Button("Qué es una call", id="option-call", color="primary", className="me-1"),
                dbc.Button("Qué es una put", id="option-put", color="primary")
            ], id="options-container", className="d-flex flex-column"),
        ]),
        dbc.ModalFooter(dbc.Input(placeholder="Escribe un mensaje aquí", type="text", id="user-input-text")),
    ], id="chatbot-container", is_open=False, style={"position": "fixed", "bottom": "90px", "right": "15px", "width": "350px"})
])

# Callback para manejar la apertura del chatbot y las respuestas
@callback(
    Output("chatbot-container", "is_open"),
    Output("messages-container", "children"),
    Output("options-container", "children"),
    Input("chatbot-toggle-button", "n_clicks"),
    Input("option-call", "n_clicks"),
    Input("option-put", "n_clicks"),
    [State("chatbot-container", "is_open")]
)
def manage_chatbot(chat_button_clicks, call_click, put_click, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "chatbot-toggle-button":
        if chat_button_clicks:
            welcome_message = dbc.Card(dbc.CardBody("Bienvenidos a la visualización de datos"), color="info", outline=True, className="mb-2")
            follow_up_message = dbc.Card(dbc.CardBody("¿En qué puedo ayudaros?"), color="info", outline=True, className="mb-2")
            options = [dbc.Button("Qué es una call", id="option-call", color="primary", className="me-1"),
                       dbc.Button("Qué es una put", id="option-put", color="primary")]
            return not is_open, [welcome_message, follow_up_message], options
        return is_open, dash.no_update, dash.no_update
    elif button_id in ["option-call", "option-put"]:
        if button_id == "option-call":
            response_message = dbc.Card(dbc.CardBody("Una call es una opción de compra"), color="secondary", outline=True)
        else:
            response_message = dbc.Card(dbc.CardBody("Una put es una opción de venta"), color="secondary", outline=True)
        options = dash.no_update  # Mantén los botones sin cambios
        return True, [response_message], options

    return is_open, dash.no_update, dash.no_update

# Ejecución del servidor
if __name__ == "__main__":
    app.run_server(debug=True)
