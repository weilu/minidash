import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div(children=[
    dbc.Card(
        dbc.CardBody([
            dbc.Tabs(id='thematic-tabs', active_tab='tab-education', children=[
                dbc.Tab(label='Education', tab_id='tab-education'),
                dbc.Tab(label='Health', tab_id='tab-health'),
            ], style={"margin-bottom": "2rem"}),
            html.Div(id='thematic-spinner', children=[
                dbc.Spinner(color="primary", spinner_style={
                    "width": "3rem", "height": "3rem"
                }),
            ]),
            html.Div(id='thematic-content'),
        ])
    )
])

