import pruebas_dash
from pruebas_dash import dcc
from pruebas_dash import html
import numpy as np
from datetime import datetime as dt


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = pruebas_dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Componentes principales"),
    html.Div(children=[
        html.H3("Dropdown:"),
        dcc.Dropdown(
            options=[
                {'label': 'Paris', 'value': 'Paris'},
                {'label': 'Roma', 'value': 'Roma'},
                {'label': 'Berlin', 'value': 'Berlin'}
            ],
            value='Paris'
        ),

        html.Br(),
        html.H3("Checkboxes:"),
        dcc.Checklist(
            options=[
                {'label': 'Paris', 'value': 'Paris'},
                {'label': 'Roma', 'value': 'Roma'},
                {'label': 'Berlin', 'value': 'Berlin'}
            ],
            value=['Paris']
        ),

        html.Br(),
        html.H3("Pestañas:"),
        dcc.Tabs(id="pests", value='pest-1', children=[
            dcc.Tab(
                label='Pestaña 1',
                value='pest-1',
                children=[
                    html.Div("Hello tab!")
                ]
            ),
            dcc.Tab(
                label='Pestaña 2',
                value='pest-2',
            ),
        ]),

        html.Br(),
        html.H3("Graficos:"),
        dcc.Graph(
            id='my_first_graph',
            figure={
                'data': [
                    {
                        'x': [1, 2, 3],
                        'y': [13, 3, 10],
                        'type': 'line',
                        'name': 'line'
                    },
                    {
                        'x': [1, 2, 3],
                        'y': [4, 10, 2],
                        'type': 'bar',
                        'name': 'bar'
                    },
                ],
                'layout': {
                    'title': 'Grafico'
                }
            }
        ),
    ], className="ten columns")
])

if __name__ == "__main__":
    app.run(debug=True)
