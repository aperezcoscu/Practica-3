## Interfaz moderna

import dash
from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime
from dash.exceptions import PreventUpdate
import numpy as np


### Estilos 

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
    'border-radius': '0 25px 25px 0'  
}

# Estilos para los botones del menú
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


# Funciones Volatilidad

def calcular_tiempo_a_madurez(df):
    """
    Calcula el tiempo hasta la madurez desde la fecha actual hasta las fechas en la columna 'Fecha' del DataFrame dado.
    La función retorna una columna con los tiempos calculados.

    Args:
        df (pd.DataFrame): DataFrame que contiene una columna 'Fecha' con las fechas de expiración.

    Returns:
        pd.Series: Serie con los tiempos hasta la madurez en años.
    """
    df_temp = df.copy()  # Trabajar con una copia para evitar efectos secundarios en el DataFrame original
    df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha'])
    fecha_base = pd.Timestamp(datetime.now().date())
    return (df_temp['Fecha'] - fecha_base).dt.days / 365.25

def preparar_datos(df, precio_subyacente, tipo_opcion):
    """
    Prepara los datos para la interpolación necesaria para crear una superficie de volatilidad.

    Args:
        df (pd.DataFrame): DataFrame con las columnas 'Fecha', 'Strike', 'Vol_call', y 'Vol_put'.
        precio_subyacente (float): Precio actual del activo subyacente para calcular el Moneyness.
        tipo_opcion (str): Tipo de opción, 'call' o 'put'.

    Returns:
        tuple: Contiene tres arrays numpy que representan la malla de Tiempo a Madurez (T),
               Moneyness (M) y los valores interpolados de Volatilidad Implícita (IV).
    """
    # Calcula la madurez y asigna a la columna 'Maturity'
    df['Maturity'] = calcular_tiempo_a_madurez(df)
    
    # Calcula el Moneyness
    df['Moneyness'] = df['Strike'] / precio_subyacente
    
    # Selecciona la volatilidad según el tipo de opción y asegura no trabajar en copias
    if tipo_opcion == 'call':
        df = df.dropna(subset=['Vol_call']).copy()
        df.loc[:, 'VolatilidadImplicita'] = df['Vol_call']
    elif tipo_opcion == 'put':
        df = df.dropna(subset=['Vol_put']).copy()
        df.loc[:, 'VolatilidadImplicita'] = df['Vol_put']
    
    # Agrupa por 'Maturity' y 'Moneyness' y calcula la media de la volatilidad implícita
    df_agrupado = df.groupby(['Maturity', 'Moneyness'], as_index=False)['VolatilidadImplicita'].mean()

    # Prepara los datos para la interpolación
    Maturity = np.linspace(df_agrupado['Maturity'].min(), df_agrupado['Maturity'].max(), 100)
    Moneyness = np.linspace(df_agrupado['Moneyness'].min(), df_agrupado['Moneyness'].max(), 100)
    T_grid, M_grid = np.meshgrid(Maturity, Moneyness)

    # Interpolación para crear la superficie de volatilidad
    IV_grid = griddata(
        (df_agrupado['Maturity'].values, df_agrupado['Moneyness'].values),
        df_agrupado['VolatilidadImplicita'].values,
        (T_grid, M_grid),
        method='cubic'
    )

    return T_grid, M_grid, IV_grid

def plot_surface(X, Y, Z, title='Superficie de Volatilidad'):
    """
    Crea y muestra un gráfico de superficie usando Plotly.

    Args:
    X (array-like): Coordenadas X de la malla de la superficie, 
    representando el tiempo de madurez.
    Y (array-like): Coordenadas Y de la malla de la superficie, 
    representando la moneidad.
    Z (array-like): Valores de la superficie (elevación) para 
    cada par (X, Y), representando la volatilidad implícita.
    title (str): Título del gráfico.

    Returns:
    None - Muestra un gráfico interactivo.
    """
    # Crear el objeto figura y añadir la superficie
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='RdBu', cmin=Z.min(), cmax=Z.max())])
    
    # Personalizar la apariencia del gráfico
    fig.update_layout(
        title=title,
        autosize=False,
        width=600,
        height=600,
        scene=dict(
            xaxis=dict(title='Maturity Time', 
                       backgroundcolor="rgb(200, 200, 230)", 
                       gridcolor="white", 
                       showbackground=True, 
                       zerolinecolor="white", 
                       tickfont=dict(size=12)),
            
            yaxis=dict(title='Moneyness', 
                       backgroundcolor="rgb(230, 200,230)", 
                       gridcolor="white", 
                       showbackground=True, 
                       zerolinecolor="white", 
                       tickfont=dict(size=12)),
            
            zaxis=dict(title='Volatilidad Implícita', 
                       backgroundcolor="rgb(230, 230,200)", 
                       gridcolor="white", 
                       showbackground=True, 
                       zerolinecolor="white", 
                       tickfont=dict(size=12)),
            camera_eye=dict(x=1.5, y=1.5, z=0.5)
        ),
        margin=dict(l=65, r=50, b=65, t=90),
        
        paper_bgcolor='rgb(243, 243, 243)',
        
        font=dict(family="Arial, sans-serif", 
                  size=12, 
                  color="darkblue")
    )

    # Ajustes de iluminación para mejorar el aspecto tridimensional
    fig.update_traces(lighting=dict(ambient=0.3, diffuse=0.7, fresnel=0.1, specular=0.5, roughness=0.5))
    
    fig.show()




# Establecer estilos de la aplicación y componentes externos
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Leer el archivo CSV
df = pd.read_csv('volatilidades.csv')
unique_dates = df['Fecha'].unique()
precio_subyacente = 11123.70  # Este valor debe ser el precio actual del subyacente

# Asumiendo que 'messages' es una variable global o de sesión que almacena los mensajes
messages = []

# Dash app
app.layout = html.Div([
    html.Div([
        html.H2('Perfil de volatilidad implícita', style={'margin-bottom': '30px'}),
        html.Hr(),
        html.P('Tipo de opción', style={'font-weight': 'bold'}),
        html.Button('Opciones Call', id='btn-call', n_clicks=0, style=button_style),
        html.Button('Opciones Put', id='btn-put', n_clicks=0, style=button_style),
        html.Hr(),
        html.P('Superficie de volatilidad', style={'font-weight': 'bold'}),
        html.Button('Visualizar superficie', id='btn-visualize-surface', n_clicks=0, style=button_style),  # Nuevo botón aquí
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


# Mantén un estado global para el menú seleccionado
selected_menu = "btn-call"

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
    global selected_menu
    
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Filtrar el dataframe por la fecha seleccionada
    filtered_df = df[df['Fecha'] == selected_date]
    fig = None

    if triggered_id in ['btn-call', 'btn-put']:
        # Ajustar la lógica de selección basada en qué botón fue presionado
        if triggered_id == 'btn-call':
            fig = px.line(filtered_df, x='Strike', y='Vol_call', title='Volatilidad de Call en función del Strike',
                          markers=True)
            call_style = active_button_style
            put_style = button_style
            selected_menu = triggered_id
        elif triggered_id == 'btn-put':
            fig = px.line(filtered_df, x='Strike', y='Vol_put', title='Volatilidad de Put en función del Strike',
                          markers=True)
            call_style = button_style
            put_style = active_button_style
            selected_menu = triggered_id
    else:
        # Usar el estado actual del menú para determinar el gráfico y estilos
        if selected_menu == 'btn-call':
            fig = px.line(filtered_df, x='Strike', y='Vol_call', title='Volatilidad de Call en función del Strike',
                          markers=True)
            call_style = active_button_style
            put_style = button_style
        elif selected_menu == 'btn-put':
            fig = px.line(filtered_df, x='Strike', y='Vol_put', title='Volatilidad de Put en función del Strike',
                          markers=True)
            call_style = button_style
            put_style = active_button_style

    # Configuración común del gráfico
    if fig:
        fig.update_layout(
            xaxis=dict(
                showline=True,
                linecolor='black',
                linewidth=1,
                showgrid=True,
                showticklabels=True,
                ticks='outside',
                gridcolor='lightgrey'
            ),
            yaxis=dict(
                showline=True,
                linecolor='black',
                linewidth=1,
                showgrid=True,
                showticklabels=True,
                ticks='outside',
                gridcolor='lightgrey'
            ),
            plot_bgcolor='white'
        )

    return [call_style, put_style, fig]


# Chatbot
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


# Ejecución del servidor
if __name__ == "__main__":
    app.run_server(debug=True)