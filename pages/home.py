import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/')

layout = layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Welcome to My Fancy Dash App", className="text-center text-primary mb-4 mt-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.P("This is a starter website built with Dash. I will be adding new features occasionally for practice and learning.", className="lead"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(className="my-2"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Todo List", className="card-title"),
                html.P("This page is a simple todo list where the data is stored in an Azure SQL database.", className="card-text")
            ])
        ), width=4),
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Graphing", className="card-title"),
                html.P("This is still in progress (not really even started) but I want to add a graph like a map or something to see data of something of the US.", className="card-text")
            ])
        ), width=4)
    ]),
    dbc.Row([
        dbc.Col(html.Hr(className="my-2"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.Footer("© 2024 My Fancy Dash App", className="text-center text-muted"), width=12)
    ])
], fluid=True)