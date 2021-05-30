import pandas as pd
import numpy as np
import plotly.express as px
from .data_collection import *
from flask import Flask, request
from flask_cors import CORS
import plotly.express as px
import plotly
import json as json
import plotly.graph_objs as go

#beta = effective_contact_rate
#delta = death_rate
#alpha = vaccination_rate
#gamma = recovery_rate
#sigma = vaccination_effectiveness_rate


app = Flask(__name__)
CORS(app)
@app.route('/chart', methods=['GET'])
def make_chart():
    location = request.args.get('location')
    day = int(request.args.get('days'))
    vaccine = int(request.args.get('vaccine'))
    return make_plot(location,60,day,vaccine), 200

def deriv(state, N, location_variables, alpha, location):
    S = state["susceptible"]
    I = state["infected"]
    R = state["recovered"]
    D = state["dead"]

    beta = location_variables["beta"]
    delta = location_variables["delta"]
    gamma_val = gamma(location)
    sigma = 0.95
    
    dSdt = ((-beta * S * I / N) - alpha) 
    dIdt = (beta * S * I / N - (gamma_val * I) +  (R*sigma*beta*I/N))
    dRdt = gamma_val * I * (1-delta) - (R*sigma*beta*I/N) +alpha
    dDdt = gamma_val * I * delta
    return [int(dSdt), int(dIdt), int(dRdt), int(dDdt)]


# data_collection.high_priority #make sure those states have people to vaccinate
@app.route('/calc', methods=['GET'])
def calc_route():
    total_vaccine_per_day = int(request.args.get('vaccine'))
    days= int(request.args.get('days'))
    
    return calc_all(total_vaccine_per_day,days),200

def calc_all(total_vaccine_per_day, days):

    location_data = {}
    location_variables = {}
    ordered = high_priority()
    for i in range(days):
        total_vaccine_left = total_vaccine_per_day
        location_data[i] = {}
        ordered_1 = {}
        for location in ordered:
            
            location_data[i][location] = {}
            if i == 0:
                location_variables[location] = {}
                SIDRV = get_SIDRV(0, location)              
                location_data[i][location]["infected"] = SIDRV['a']['confirmed']
                ordered_1[location] = location_data[i][location]["infected"]
                location_data[i][location]["recovered"] = SIDRV['a']['recovered'] + SIDRV['a']['vaccinated']
                location_data[i][location]["susceptible"] = SIDRV['a']['susceptible']
                location_data[i][location]["dead"] = SIDRV['a']['deceased']
                location_data[i][location]["vaccinated"] = SIDRV['a']['vaccinated']
                location_variables[location]["beta"] = get_beta(location)
                location_variables[location]["delta"] = get_delta(location)
            else:
                alpha = total_vaccine_per_day/5
                if (alpha < (location_data[i-1][location]["susceptible"] - alpha)) and (alpha < total_vaccine_left): 
                    total_vaccine_left -= alpha
                elif (alpha < (location_data[i-1][location]["susceptible"] - alpha)) and (alpha > total_vaccine_left):
                    alpha = total_vaccine_left
                    total_vaccine_left -= alpha
                else:
                    alpha = 0       
                location_data[i][location]['vaccinated'] = alpha + location_data[i-1][location]['vaccinated']
                deriv_array = deriv(location_data[i-1][location], pop[location], location_variables[location], alpha, location)
                location_data[i][location]["infected"] = location_data[i-1][location]["infected"] + deriv_array[1]
                ordered_1[location] = location_data[i][location]["infected"]
                location_data[i][location]["recovered"] = location_data[i-1][location]["recovered"] + deriv_array[2]
                location_data[i][location]["susceptible"] = location_data[i-1][location]["susceptible"] + deriv_array[0] if location_data[i-1][location]["susceptible"] + deriv_array[0] >=0 else 0
                location_data[i][location]["dead"] = location_data[i-1][location]["dead"] + deriv_array[3]
        
        # print(ordered_1)
        ordered = sorted(ordered_1, key=ordered_1.get, reverse=True)
        
    #     print (ordered)
    # print(location_data)
    return location_data

def make_plot(location, days_ago, days_forward, vaccines):
    the_dict = calc_all(vaccines, days_forward)
    master = {'days': [], 'deaths': [], 'active': [], 'vaccinated': []}
    for i in range(days_ago, 0, -1):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # df = data_frame()    
    # print(df)
    # fig = px.line(df, x="day", y="infected", title='Life expectancy in Canada')
    # fig.write_image("fig1.png")
