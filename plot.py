import math
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression, RANSACRegressor, HuberRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from plotly.subplots import make_subplots
from queries import get_health_data, get_edu_data


def make_plot(dataset, gdp, country, yaxes_title, table_header_outcome, column_name):
    earliest_year = dataset.year.min() 
    latest_year = dataset.year.max()
    years = sorted(dataset.year.unique().tolist())
    max_exp = dataset.gdp_per_capita_2017_ppp.max()
    color_map = {'LIC': 'red', 'LMC': 'orange', 'UMC': 'purple', 'HIC': 'blue'}
    income_level_legend_map = {'LIC': '1. Low Income', 'LMC': '2. Lower Middle', 'UMC': '3. Upper Middle', 'HIC': '4. High Income'}
    table_cols = ['year', 'income_level_label', 'country_name', 'gdp_per_capita_2017_ppp', column_name, 'link']
    table_headers = ['Year', 'Income Level', 'Country', 'Per Capita GDP (2017 PPP)', table_header_outcome, 'Link']

    def build_graph_and_table(year):
        graphs = []
        outlier_countries = pd.DataFrame(columns=dataset.columns + ['fitted_y'])
        dataset_by_year = dataset[dataset["year"] == year]
        for level in income_level_legend_map.keys():
            level_name = income_level_legend_map[level]
            dataset_by_year_level = dataset_by_year[
                dataset_by_year["income_level"] == level].sort_values(by="gdp_per_capita_2017_ppp")

            x = dataset_by_year_level["gdp_per_capita_2017_ppp"]
            y = dataset_by_year_level[column_name]
            country_names = dataset_by_year_level['country_name']

            if not dataset_by_year_level.empty:
                # trendline
                x_input = x.values.reshape(-1, 1)
                model = LinearRegression()
                fitted_y = model.fit(x_input, y.ravel()).predict(x_input)
                residuals = y - fitted_y
                std_residuals = np.abs(residuals / np.std(residuals))
                outlier_mask = std_residuals > 1.5
            else:
                fitted_y = y
                outlier_mask = y != fitted_y

            data_dict = {
                'y': list(fitted_y),
                'x': list(x),
                'line': dict(color=color_map[level]),
                'name': f'Trendline: {level_name}',
                'legendgroup': level_name,
                'showlegend': False,
                'hoverinfo': 'skip',
                'opacity': 0.5,
            }
            graphs.append(go.Scatter(**data_dict))

            # scatter non-outliers
            data_dict = {
                "x": list(x[~outlier_mask]),
                "y": list(y[~outlier_mask]),
                "mode": "markers",
                "text": list(country_names[~outlier_mask]),
                "marker": {
                    "color": color_map[level], 
                    "opacity": 0.3,
                },
                "name": level_name,
                "legendgroup": level_name,
                'showlegend': False,
            }
            graphs.append(go.Scatter(**data_dict))

            # scatter outliers
            textposition = np.where(y[outlier_mask] > fitted_y[outlier_mask], 'top center', 'bottom center')
            data_dict = {
                "x": list(x[outlier_mask]),
                "y": list(y[outlier_mask]),
                "mode": "markers",
                "text": list(country_names[outlier_mask]),
                "textposition": list(textposition),
                "marker": {
                    "color": color_map[level], 
                    "opacity": 0.6,
                },
                "name": level_name,
                "legendgroup": level_name,
            }
            graphs.append(go.Scatter(**data_dict))

            dataset_by_year_level['fitted_y'] = fitted_y
            outlier_countries = pd.concat([outlier_countries, dataset_by_year_level[outlier_mask]], ignore_index=True)

        outlier_countries['income_level_label'] = outlier_countries['income_level'].map(income_level_legend_map)
        outlier_countries['y_minus_fitted_y'] = outlier_countries[column_name] - outlier_countries.fitted_y
        outlier_countries['link'] = '<a href="https://app.powerbi.com/groups/75fff923-5acd-443e-877b-d2c6e88cdb31/reports/a28af24a-6a8a-4241-bd42-40a4c4af5716/ReportSection?experience=power-bi">investigate</a>'
        outlier_countries.sort_values(by=['year', 'income_level_label', 'y_minus_fitted_y'], inplace=True)
        # color underformers red, overperformers green
        colors = np.where(outlier_countries.y_minus_fitted_y > 0, '#D8FFB1', '#FFCCCB')

        if outlier_countries.shape[0] > 0:
            t = go.Table(
                header=dict(values=table_headers,
                                fill = dict(color='#C2D4FF'),
                                align = ['left'] * 5),
                cells=dict(values=[outlier_countries[col] for col in table_cols],
                            fill = dict(color=[colors for col in table_cols]),
                            align = ['left'] * 5),
                )
        else:
            t = go.Table(header=dict(values=[f'No outlier country detected for {year}']))


        return graphs, t, outlier_countries


    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.15,
        specs=[
            [{"type": "scatter"}],
            [{"type": "table"}],
        ],
        subplot_titles=('Institutional Capacity vs. Outcome', 'Outlier Countries')
    )

    graphs, t, _ = build_graph_and_table(latest_year)
    num_scatters = len(graphs)
    fig.add_traces(graphs, rows=1, cols=1)
    fig.add_trace(t, row=2, col=1)

    fig.update_layout(height=800)
    fig.update_xaxes(range=[-50, max_exp + 100], title="Per Capital GDP (2017 PPP)")
    fig.update_yaxes(range=[0, 1], title=yaxes_title)
    updatemenus = [{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
    }]

    sliders_dict = {
        "active": len(years)-1,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    frames = []
    for year in years:
        graphs, t, outliers = build_graph_and_table(year)

        # each frame must have the same number of traces, otherwise annimation may fail with out-of-index error
        assert len(graphs) == num_scatters, f'Expect the number of scatter traces ({num_scatters}) to be the same across years but got {len(graphs)} for {year}'
        assert t is not None, 'Expect outlier table to be present'

        frame = {
            "data": graphs + [t],
            "name": year,
        }
        frames.append(frame)

        slider_step = {
            "args": [
                [year],
                {"frame": {"duration": 300, "redraw": True},
                "mode": "immediate",
                "transition": {"duration": 300}}
            ],
            "label": year,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig.update(frames=frames),
    fig.update_layout(updatemenus=updatemenus,
                      sliders=[sliders_dict])
    return fig


def make_health_plot(gdp, country):
    dataset = get_health_data(gdp, country)
    return make_plot(dataset, gdp, country, 'Universal Health Coverage', 'Universal Health Coverage Index', 'universal_health_coverage_index')

def make_edu_plot(gdp, country):
    dataset = get_edu_data(gdp, country)
    return make_plot(dataset, gdp, country, 'Learning Poverty Rate', 'Learning Poverty Rate', 'learning_poverty_rate')
