# V-MAP Back-end API

### Description
The backend is hosted on https://v-map-hackon.herokuapp.com/ and has two routes that can be used. See https://github.com/ernest1027/V-Map
for more details about the entire full-stack application

### Chart Route
The chart route provides the json for a plotly chart. The json can be translated by a script to create an interactive plotly chart. The plotly chart
provides a chart of actives cases and cumulative deaths. The route takes in location (based on two letter India state codes), days forward to predict, and 
the number of vaccine doses available to the whole of India. Note that the vaccinations are administered based on the proprietary vaccine distribution
algorithm (see calc route)

#### How to use
To use the chart route, type the following URL https://v-map-hackon.herokuapp.com/chart?location=INSERTLOCATIONNAME&days=INSERTDAYNUMBER.value&vaccine=INSERTVACCINENUMBER 
Be sure to replace the query values.

### Calc route
The calc route provides a json that has the susceptible, infected, recovered, dead, and vaccinated given certain variables. The input variables are
the number of vaccines available daily and the number of days to predict until. The back-end uses our algorithm to distribute the vaccines as effectively
as possible. Specifically, it uses the SIR model based on differential equations to predict which states will have the highest infection rate. From there,
it uses a greedy alogrithm to optimize vaccine distribution and focus on hotspots.

#### How to use
To use the calc route, type the following URL https://v-map-hackon.herokuapp.com/calc?vaccine=INSERTVACCINENUMBER&days=INSERTDAYNUMBER
Be sure to replace the query values.