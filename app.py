import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from dash.long_callback import DiskcacheLongCallbackManager
from queries import get_gdp, get_country, get_available_data
from plot import make_health_plot

import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.QUARTZ, dbc_css],
    long_callback_manager=long_callback_manager,
    suppress_callback_exceptions=True,
    use_pages=True,
)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}

CONTENT_STYLE = {
    "marginLeft": "18rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        dbc.Row([
            dbc.Col(html.Img(src=app.get_asset_url('rpf_logo.png'), style={'height': '50px', 'marginLeft': '20px'}), width="auto"),
            dbc.Col(html.H2("RPF", className="display-4", style={'color': 'white', 'marginBottom': 0}), width="auto"),
        ], align='center'),
        dbc.Row([
            dbc.Col(html.Small("Reimagining Public Finance", className="text-muted"), width="auto")
        ], align='center'),

        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact"),
                dbc.NavLink("Thematic Studies", href="/thematic", active="exact"),
                dbc.NavLink("Data Availability", href="/availability", active="exact", id="avail-nav"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(dash.page_container,
    id="page-content", style=CONTENT_STYLE
)

app.layout = html.Div([sidebar, content])


@app.long_callback(
    Output('thematic-content', 'children'),
    Input('thematic-tabs', 'active_tab'),
    running=[
        (
            Output("thematic-spinner", "style"),
            {"display": "block"},
            {"display": "none"},
        ),
        (
            Output("thematic-content", "style"),
            {"display": "none"},
            {"display": "block"},
        ),
    ],
)
def render_thematic_content(tab):
    gdp = get_gdp()
    country = get_country()
    if tab == 'tab-education':
        return html.Div([
            html.H3('Education Content')
        ])
    elif tab == 'tab-health':
        return html.Div([
            dcc.Graph(figure=make_health_plot(gdp, country))
        ])


@app.long_callback(
    Output('availability-content', 'children'),
    Input('avail-nav', 'active'),
    running=[
        (
            Output("availability-spinner", "style"),
            {"display": "block"},
            {"display": "none"},
        ),
        (
            Output("availability-content", "style"),
            {"display": "none"},
            {"display": "block"},
        ),
    ],
)
def render_availability_content(active):
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

    return table


if __name__ == '__main__':
    app.run_server(debug=True)

