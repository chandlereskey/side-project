import dash
from dash import html
import dash_bootstrap_components as dbc
from waitress import serve

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Todos", href="/todos")),
        dbc.NavItem(dbc.NavLink("Graphing", href="/graphing"))
    ],
    brand="Chandler Starter Website",
    color="dark",
    dark=True
)

app.layout = html.Div([
    navbar,
    dash.page_container
])

if __name__ == '__main__':
    serve(app.server, host="0.0.0.0", port=8000)