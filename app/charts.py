from .main import calc_all
from data_collection import cases_list
import plotly.express as px
import plotly
import json as json

the_dict = calc_all(1000000, 21)

def make_plot():
        master = {'days': [], 'count': []}
        for key, values in the_dict.items():
                master['days'].append(key)
                master['count'].append(values['DL']['infected'])
        print(type(the_dict))

        fig = px.line(master, x='days', y='count')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
