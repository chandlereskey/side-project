import dash
import pandas as pd
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from connection import engine
import datetime
import sqlalchemy
from waitress import serve

# constants
TODO = 0
COMPLETED = 1
CREATEDAT = 2
COMPLETEDAT = 3

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("To-Do List", className="text-center"), className="mb-4 mt-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Input(id="input-task", type="text", placeholder="Enter a task", className="form-control"), width=8),
        dbc.Col(dbc.Button("Add Task", id="add-task-button", color="primary", className="ml-2"), width=4)
    ]),
    dbc.Row([
        dbc.Col(html.Ul(id="task-list", className="list-group mt-4"), width=12)
    ])
], fluid=True)

# Callback to add tasks
@app.callback(
    Output("task-list", "children"),
    Input("add-task-button", "n_clicks"),
    State("input-task", "value"),
    State("task-list", "children")
)
def update_task_list(n_clicks, new_task, current_tasks):
    if n_clicks is not None and new_task is not None:
        df = pd.DataFrame({
            'todo': [new_task],
            'completed': [0],
            'createdAt': [datetime.datetime.now()],
            'completedAt': [None]
        })
        print(df)
        df.to_sql('todos', engine, if_exists='append', index=False)

    df = pd.read_sql_table('todos', engine)

    print(df.values)


    current_tasks = [html.Li([
        html.Span(row[TODO], className="task-text", style={"textDecoration": "line-through" if row[COMPLETED] == 1 else ""}),
        dbc.Button("Complete", id={"type": "complete-button", "index": i}, color="success", className="ml-2", disabled=row[COMPLETED] == 1),
        dbc.Button("Delete", id={"type": "delete-button", "index": i}, color="failure", className="ml-2", disabled=row[COMPLETED] != 1)
    ], className="list-group-item d-flex justify-content-between align-items-center") for i,row in enumerate(df.values)]

    return current_tasks

# Callback to mark tasks as complete
@app.callback(
    Output("task-list", "children", allow_duplicate=True),
    Input({"type": "complete-button", "index": dash.dependencies.ALL}, "n_clicks"),
    State("task-list", "children"),
    prevent_initial_call=True
)
def complete_task(n_clicks, current_tasks):
    if n_clicks is None:
        return current_tasks
    with engine.connect() as connection:
        for i, task in enumerate(current_tasks):
            if n_clicks[i] is not None:
                current_task_name = task["props"]["children"][0]["props"]["children"]
                update_query = f"update dbo.todos set completed = 1, completedAt = '{datetime.datetime.now()}' WHERE todo = '{current_task_name}'"
                print(update_query)
                connection.execute(sqlalchemy.text(update_query))
                task["props"]["children"][0]["props"]["style"] = {"textDecoration": "line-through"}
                task["props"]["children"][1]["props"]["disabled"] = True
                task["props"]["children"][2]["props"]["disabled"] = False
        connection.commit()

    return current_tasks

# Callback to mark delete tasks
@app.callback(
    Output("task-list", "children", allow_duplicate=True),
    Input({"type": "delete-button", "index": dash.dependencies.ALL}, "n_clicks"),
    State("task-list", "children"),
    prevent_initial_call=True
)
def complete_task(n_clicks, current_tasks):
    if n_clicks is None:
        return current_tasks
    with engine.connect() as connection:
        for i, task in enumerate(current_tasks):
            if n_clicks[i] is not None:
                current_task_name = task["props"]["children"][0]["props"]["children"]
                update_query = f"delete from dbo.todos WHERE todo = '{current_task_name}'"
                print(update_query)
                connection.execute(sqlalchemy.text(update_query))
                current_tasks.pop(i)
        connection.commit()

    return current_tasks

# Run the app
if __name__ == "__main__":
    serve(app.server, host="0.0.0.0", port=8050)
