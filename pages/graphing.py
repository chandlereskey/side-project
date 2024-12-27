import dash
from dash import dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from connection import engine


dash.register_page(__name__, path='/graphing')

main_df = pd.read_sql('select state, measure_name, sum(raw_value) as total from [dbo].[CountyHealthRankings] group by state, measure_name', engine)
measures = []
for m in main_df['measure_name'].unique():
    if m is not None:
        measures.append({'label': m, 'value': m})
print(measures)

layout = dbc.Container([
    dbc.Row([dcc.Dropdown(id='measures', options=measures, value='Unemployment', placeholder='Select Measure')]),
    dbc.Row(dbc.Col([dcc.Graph(id='my-graph-map', figure=None), dcc.Graph(id='my-graph-bar', figure=None)]),
    )], fluid=True)


# Callback to add tasks
@dash.callback(
    Output("my-graph-map", "figure"),
    Output("my-graph-bar", "figure"),
    Input("measures", "value"),
)
def update_task_list(measure):
    print(measure)
    if measure is None:
        return None, None
    df = main_df[main_df['measure_name'] == measure]
    map_fig = px.choropleth(df,
                    locations='state',
                    locationmode="USA-states",
                    scope="usa",
                    color='total',
                    color_continuous_scale="Oranges",
                   )
    # center the title
    map_fig.update_layout(title_text=f'{measure} per state', title_x=0.5)
    # label states with count
    map_fig.add_scattergeo(
        locations=df['state'],
        locationmode="USA-states",
        text = df['state'],
        featureidkey="properties.NAME_3",
        mode = 'text',
        textfont=dict(
                family="helvetica",
                size=10,
                color="white"
        )) 

    bar_fig = px.bar(df, x='state', y='total')

    return map_fig, bar_fig