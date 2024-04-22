import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd

from queries import get_available_data

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ, dbc_css])

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        dbc.Row([
            dbc.Col(html.Img(src=app.get_asset_url('rpf_logo.png'), style={'height': '50px', 'margin-left': '20px'}), width="auto"),
            dbc.Col(html.H2("RPF", className="display-4", style={'color': 'white', 'margin-bottom': 0}), width="auto"),
        ], align='center'),
        dbc.Row([
            dbc.Col(html.Small("Reimagining Public Finance", className="text-muted"), width="auto")
        ], align='center'),

        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact"),
                dbc.NavLink("Thematic Studies", href="/thematic", active="exact"),
                dbc.NavLink("Data Availability", href="/availability", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/thematic":
        return dbc.Card(
            dbc.CardBody([
                dbc.Tabs(id='thematic-tabs', active_tab='tab-education', children=[
                    dbc.Tab(label='Education', tab_id='tab-education'),
                    dbc.Tab(label='Health', tab_id='tab-health'),
                ]),
                html.Div(id='thematic-content')
            ])
        )
    elif pathname == "/availability":
        df = get_available_data()

        df.columns = df.columns.str.replace('_', ' ').str.title()

        table = dash_table.DataTable(
            df.to_dict('records'),
            [{"name": i, "id": i} for i in df.columns],
            filter_action="native",
            sort_action="native",
            page_size=200,
            style_table={'overflowX': 'auto'},  # Scrollable table
            style_cell={'textAlign': 'left'},
            style_header={
                'fontWeight': 'bold',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#2c3034',
                },
            ],
        )

        return dbc.Card(
            dbc.CardBody([
                html.Div([
                    table
                ],  className="dbc", **{"data-bs-theme": "dark"})
            ])
        )

    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


@app.callback(Output('thematic-content', 'children'),
              Input('thematic-tabs', 'active_tab'))
def render_thematic_content(tab):
    if tab == 'tab-education':
        return html.Div([
            html.H3('Education Content')
        ])
    elif tab == 'tab-health':
        return html.Div([
            html.H3('Health Content')
        ])

if __name__ == '__main__':
    app.run_server(debug=True)

