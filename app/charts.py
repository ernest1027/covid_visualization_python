import json

import plotly.utils

from main import calc_all
from data_collection import cases_list, get_SIDRV, case_day
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt


def make_plot(days_ago=60, location, days_forward, vaccines):
    the_dict = calc_all(vaccines, days_forward)
    master = {'days': [], 'deaths': [], 'active': [], 'vaccinated': []}
    for i in range(days_ago, 0, -1):
        print(i)
        master['days'].append(-i)
        deceased = case_day('deceased', 'total', i, location)[location]
        recovered = case_day('recovered', 'total', i, location)[location]
        active = case_day('confirmed', 'total', i, location)[location] - (deceased + recovered)
        master['active'].append(active)

    for case in cases_list('deceased', days_ago, location)[location]:
        master['deaths'].append(case)

    for key, values in the_dict.items():

        master['days'].append(key)
        master['active'].append(values[location]['infected'])
        master['deaths'].append(values[location]['dead'])

    plot = go.Figure()

    plot.add_trace(go.Scatter(
        name='Cumulative Deaths',
        x=master['days'],
        y=master['deaths'],
        stackgroup='one'
    ))

    plot.add_trace(go.Scatter(
        name='Active Cases',
        x=master['days'],
        y=master['active'],
        stackgroup='one'
    )
    )

    plot.update_layout(
        title=location,
        xaxis_title="Days from Present",
        yaxis_title="Cases",
        legend_title="Legend",
        font=dict(
            family="Calibri, monospace",
            size=18
        )
    )
    # plot.show()
    graphJSON = json.dumps(plot, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
