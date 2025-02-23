import dash
from dash import html
import dash_bootstrap_components as dbc
from dash_canvas import DashCanvas


dash.register_page(__name__, path='/number-guesser')

layout = layout = dbc.Container([
    dbc.Row([
        html.H1('Draw a number')
    ]),
    dbc.Row([
        DashCanvas(id='drawn-number')
    ])
], fluid=True)