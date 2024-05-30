import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

dash.register_page(__name__)


layout = html.Div(children=[
    dbc.Card(
        dbc.CardBody([
            html.Div(id='availability-spinner', children=[
                dbc.Spinner(color="primary", spinner_style={
                    "width": "3rem", "height": "3rem"
                }),
            ]),
            html.Div(id='availability-content', className="dbc", **{"data-bs-theme": "dark"}),
        ])
    )
])

