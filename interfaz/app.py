# Librerias interfaz
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import no_update

import numpy as np
import pandas as pd
from datetime import datetime
from scipy.interpolate import griddata
from datetime import date

import plotly.express as px
import plotly.graph_objects as go

#Librerias para obtener datos
import boto3
import pandas as pd
from decimal import Decimal
from io import BytesIO

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
chat_button_style = {
    'font-size': '16px',
    'background-color': 'rgb(0, 0, 0)',  # Color de fondo negro
    'color': 'rgb(255, 255, 255)',  # Color de texto blanco
    'border-radius': '50%',  # Hace el botón completamente redondo
    'padding': '10px',  # Espacio interno uniforme
    'width': '65px',  # Ancho fijo
    'height': '65px',  # Altura fija, igual al ancho para ser un círculo perfecto
    'border': 'none',  # Sin borde
    'cursor': 'pointer',  # Cursor en forma de mano al pasar por encima
    'display': 'flex',  # Uso de Flexbox para centrar el texto
    'justify-content': 'center',  # Centrado horizontal del texto
    'align-items': 'center',  # Centrado vertical del texto
    'position': 'fixed',  # Posición fija en la pantalla
    'bottom': '35px',  # Posición desde abajo
    'right': '110px',  # Posición desde la derecha
    'z-index': '1000000',  # Z-index para asegurarse que esté sobre otros elementos
}

messages_container_style = {
    "display": "flex",
    "flex-direction": "column",
    "height": "300px",
    "overflow-y": "auto",
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

chatbot_modal_style = {
    'position': 'fixed',  # Posicionamiento fijo respecto al viewport
    'bottom': '105px',  # Altura desde el bottom, debe ser mayor que la del botón para que aparezca encima
    'right': '110px',  # Alineado con el botón derecho
    'width': '350px',  # Ancho fijo del modal
    'z-index': '1000001',  # Asegurándose de que está por encima de otros elementos, incluso el botón
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

def plot_surface(X, Y, Z):
    # Crear el objeto figura y añadir la superficie
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='RdBu', cmin=Z.min(), cmax=Z.max())])
    
    # Personalizar la apariencia del gráfico
    fig.update_layout(
        autosize=False,
        height=700,
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
            
            aspectratio=dict(x=2, y=0.8, z=0.8),  # Aquí se ajusta la relación de aspecto para hacer el eje X más ancho
            camera_eye=dict(x=0, y=1.7, z=0.2)
        ),
        margin=dict(l=25, r=25, b=25, t=25),
        
        paper_bgcolor='rgb(243, 243, 243)',
        
        font=dict(family="Arial, sans-serif", 
                  size=12, 
                  color="black"),
    )

    # Ajustes de iluminación para mejorar el aspecto tridimensional
    fig.update_traces(lighting=dict(ambient=0.3, diffuse=0.7, fresnel=0.1, specular=0.5, roughness=0.5))
    
    return fig
    
def crear_grafico(df, subyacente, tipo_opcion):
    T_type, M_type, IV_type = preparar_datos(df, subyacente, tipo_opcion)
    return plot_surface(T_type, M_type, IV_type)


# Establecer estilos de la aplicación y componentes externos
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


# Obtenemos datos

# Inicializar un cliente de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')

# Seleccionar la tabla
table = dynamodb.Table('volatiliy_table')

response = table.scan()
data = response['Items']

# Convertir la lista de diccionarios a DataFrame
df = pd.DataFrame(data)

# Convertir todas las columnas que contienen decimales a flotantes
for column in ['Vol_call', 'Strike', 'Vol_put']:
    df[column] = df[column].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
    
df = df.loc[:, ['Fecha', 'Strike', 'Vol_call', 'Vol_put']]

# Ordenar los datos primero por 'Fecha' y luego por 'Strike'
df = df.sort_values(by=['Fecha', 'Strike'])

# Resetear el índice del DataFrame
df = df.reset_index(drop=True)

# Reemplazar valores menores que 0.001 en 'Vol_call' y 'Vol_put' por NaN
df['Vol_call'] = df['Vol_call'].mask(df['Vol_call'] < 0.001, np.nan)
df['Vol_put'] = df['Vol_put'].mask(df['Vol_put'] < 0.001, np.nan)


# Crear un cliente S3
s3 = boto3.client('s3', region_name='eu-west-3')

# Definir el nombre del bucket y la clave del archivo
bucket_name = 'miax-12-scrap-meff'
file_key = 'datos_futuros.json'

# Obtener el objeto S3
response = s3.get_object(Bucket=bucket_name, Key=file_key)

# Leer el contenido del objeto
file_content = response['Body'].read()

# Convertir bytes a un objeto similar a un archivo usando BytesIO
json_bytes = BytesIO(file_content)

# Cargar el contenido del objeto BytesIO en un DataFrame
df_futuro = pd.read_json(json_bytes)


# Comprobamos que no nos encontramos en la fecha actual de vencimiento
today = str(date.today())

# Obtenemos datos necesarios para representar las volatilidades
unique_dates = df['Fecha'].unique()

# Filtramos para excluir la fecha de hoy
unique_dates = unique_dates[unique_dates != today]

# Convertimos el resultado final a un arreglo de NumPy con dtype object
unique_dates = np.array(unique_dates, dtype=object)
precio_subyacente = df_futuro.loc[0, 'Ant']


# Asumiendo que 'messages' es una variable global o de sesión que almacena los mensajes
messages = []

# Dash app
app.layout = html.Div([
    html.Div([
        html.H2('Perfil de volatilidad implícita', style={'margin-bottom': '30px'}),
        html.Hr(),
        html.P('Volatilidad implícita', style={'font-weight': 'bold'}),
        html.Button('Opciones Call', id='btn-call', n_clicks=0, style=button_style),
        html.Button('Opciones Put', id='btn-put', n_clicks=0, style=button_style),
        html.Hr(),
        html.P('Superficie de volatilidad', style={'font-weight': 'bold'}),
        html.Button('Visualizar Volatilidad', id='btn-visualize', n_clicks=0, style=button_style),
    ], style=sidebar_style),
    html.Div([
        html.H2("Volatilidad implícita", className="text-left", style={'margin-bottom': '30px'}),
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
    html.Div(id='dynamic-content', style=content_style),
    # Elementos del Chatbot
    dbc.Button("Chatbot", id="chatbot-toggle-button", n_clicks=0, style=chat_button_style),
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
    ], id="chatbot-container", is_open=False, style=chatbot_modal_style)
])

### Volatilidad implícita
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
            filtered_df = filtered_df.dropna(subset=['Vol_call'])
            fig = px.line(filtered_df, x='Strike', y='Vol_call', title='Volatilidad de Call en función del Strike',
                          markers=True)
            call_style = active_button_style
            put_style = button_style
            selected_menu = triggered_id
            
        elif triggered_id == 'btn-put':
            filtered_df = filtered_df.dropna(subset=['Vol_put'])
            fig = px.line(filtered_df, x='Strike', y='Vol_put', title='Volatilidad de Put en función del Strike',
                          markers=True)
            call_style = button_style
            put_style = active_button_style
            selected_menu = triggered_id
            
    else:
        # Usar el estado actual del menú para determinar el gráfico y estilos
        if selected_menu == 'btn-call':
            filtered_df = filtered_df.dropna(subset=['Vol_call'])
            fig = px.line(filtered_df, x='Strike', y='Vol_call', title='Volatilidad de Call en función del Strike',
                          markers=True)
            call_style = active_button_style
            put_style = button_style
            
        elif selected_menu == 'btn-put':
            filtered_df = filtered_df.dropna(subset=['Vol_put'])
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


### Superficie volatilidad
@app.callback(
    [Output('dynamic-content', 'children'),
     Output('btn-visualize', 'style')],
    [Input('btn-visualize', 'n_clicks')],
    [State('dynamic-content', 'children')]
)
def update_visualization_area(n_clicks, children):
    if n_clicks is None or n_clicks == 0:
        return no_update, button_style

    if children:
        return None, button_style
    else:
        # El contenido de las columnas
        column1_content = html.Div([
            html.H4("¿Qué es?"),
            html.P("""
                La superficie de volatilidad es una representación gráfica tridimensional que ilustra cómo la 
                volatilidad implícita de opciones varía con el precio de ejercicio y el tiempo hasta la expiración. 
                Esta visualización ayuda a entender cómo el mercado percibe futuros movimientos del activo subyacente 
                bajo diferentes condiciones de mercado.
                """, style={'text-align': 'justify'})
        ], className="mb-3 p-2")

        column2_content = html.Div([
            html.H4("¿Para qué sirve?"),
            html.P("""
                La superficie de volatilidad es esencial para los traders y analistas financieros ya que proporciona 
                insights sobre la expectativa de volatilidad en el mercado. Facilita la identificación de oportunidades 
                de arbitraje y ayuda en la toma de decisiones estratégicas para la gestión de riesgos y la valorización 
                de opciones.
                """, style={'text-align': 'justify'})
        ], className="mb-3 p-2")

        # Dropdown para seleccionar entre Call y Put
        option_selector = html.Div([
            html.Label('Escoge la superficie que desees visualizar:', style={'margin-right': '10px', 'color': 'black'}),
            dcc.Dropdown(
                id='option-dropdown',
                options=[
                    {'label': 'Call Options', 'value': 'call'},
                    {'label': 'Put Options', 'value': 'put'}
                ],
                value='call',
                style={'width': '200px', 'display': 'inline-block', 'vertical-align': 'middle', 'border-radius': '10px'}
            )
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'flex-start', 'flex-wrap': 'wrap', 'padding': '20px 0'})

        content = html.Div([
            html.H2("Superficie de Volatilidad", className="text-left mb-2", style={'border-bottom': '1px solid grey', 'padding-bottom': '25px'}),
            dbc.Row([
                dbc.Col(column1_content, width=6, style={'padding-left': '50px', 'padding-right': '50px', 'border-right': '1px solid grey'}),  
                dbc.Col(column2_content, width=6, style={'padding-left': '50px', 'padding-right': '50px'})
            ], className="g-2"),
            option_selector,
            dcc.Graph(id='surface-volatility-graph')  # El gráfico específico para la superficie de volatilidad
        ], style={'padding': '10px'})

        return content, active_button_style

@app.callback(
    Output('surface-volatility-graph', 'figure'),  # Actualizar el gráfico en la interfaz
    [Input('option-dropdown', 'value')]  # Escuchar los cambios en el dropdown
)
def update_surface_graph(option_type):
    return crear_grafico(df, precio_subyacente, option_type)  # Usar df_final como ejemplo



### Chatbot
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
    app.run_server(debug=True, host='0.0.0.0', port=8050)