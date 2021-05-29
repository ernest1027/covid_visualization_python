import pandas as pd
import numpy as np
import plotly.express as px
from .data_collection import *
from flask import Flask, request
from flask_cors import CORS
import plotly.express as px
import plotly
import json as json


#beta = effective_contact_rate
#delta = death_rate
#alpha = vaccination_rate
#gamma = recovery_rate
#sigma = vaccination_effectiveness_rate


app = Flask(__name__)
CORS(app)

@app.route('/chart', methods=['GET'])
def make_chart():
    return make_plot(), 200

def deriv(state, N, location_variables, alpha):
    S = state["susceptible"]
    I = state["infected"]
    R = state["recovered"]
    D = state["dead"]

    beta = location_variables["beta"]
    delta = location_variables["delta"]
    gamma = 1/3.5
    sigma = 0.95
    
    dSdt = ((-beta * S * I / N) - alpha) 
    dIdt = (beta * S * I / N - (gamma * I) +  (R*sigma*beta*I/N)) 
    dRdt = gamma * I * (1-delta) - (R*sigma*beta*I/N) +alpha
    dDdt = gamma * I * delta
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
                deriv_array = deriv(location_data[i-1][location], pop[location], location_variables[location], alpha)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # df = data_frame()    
    # print(df)
    # fig = px.line(df, x="day", y="infected", title='Life expectancy in Canada')
    # fig.write_image("fig1.png")
