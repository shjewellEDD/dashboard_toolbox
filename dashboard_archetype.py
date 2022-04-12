'''
TODO:
    Improvement:
        It probably makes more sense to create a dictionary of x,y pairs and have it read from those, instead of hard
        coding in 'time'
        Use ctx and dcc.Store to prevent updates when changing date
        Color:
            Probably should update_layout wiht color instead of px.scatter
        Data selection:
            Break up Prawler from set
        Profile plotting, see Scott's email
        Improve style sheet
        Generalize plotting, so I don't need separate functions to do it.
        Date errors:
            M200 science has a bunch of dates from the 70s and 80s
            How do we deal with this
            Just drop?
            Linearly interpolate?

Data for archetyping:


'''

import dash
from dash import html as dhtml
from dash import dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc

#non-plotly imports
# from lxml import html
import datetime
# from datetime import date
# import io
# import urllib

# my imports
import erddap_reader as erdr

prawlers = [#{'label':   'M200 Eng', 'value': 'M200Eng'},
            #{'label':   'M200 Sci', 'value': 'M200Sci'},
            {'label':   'M200 Wind', 'value': 'M200Wind'},
            {'label':   'M200 Temp/Humid', 'value': 'M200ATRH'},
            {'label':   'M200 Baro', 'value': 'M200Baro'}
            ]


dataset_dict = {
            #'M200Eng': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/TELOM200_PRAWE_M200.csv',
            #'M200Sci': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/TELOM200_PRAWC_M200.csv',
            'M200Wind': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/TELOM200_WIND.csv',
            'M200Baro': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/TELOM200_BARO.csv',
            'M200ATRH': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/TELOM200_ATRH.csv'
            }


skipvars = ['time', 'Time', 'TIME', 'latitude', 'longitude', 'timeseries_id', 'profile_id', 'Epoch_Time', 'NC_GLOBAL']


'''
========================================================================================================================
Start Dashboard
'''

#set_obj = Dataset(set_meta['Eng']['url'])
starting_set = 'M200Wind'

graph_config = {'modeBarButtonsToRemove' : ['hoverCompareCartesian','select2d', 'lasso2d'],
                'doubleClick':  'reset+autosize', 'toImageButtonOptions': { 'height': None, 'width': None, },
                'displaylogo': False}

colors = {'background': '#111111', 'text': '#7FDBFF'}

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']

variables_card = dbc.Card(
    [#dbc.CardHeader("Tools"),
     dbc.CardBody(
         dcc.Dropdown(
             id="select_var",
             # style={'backgroundColor': colors['background']},
             #        'textColor': colors['text']},
             # options=dataset_dict[starting_set].ret_vars(),
             # value=dataset_dict[starting_set].ret_vars()[0]['value'],
             clearable=False
         ),
    )],
    color='dark'
)

set_card = dbc.Card([
        dbc.CardBody(
            dcc.Dropdown(
                id="select_eng",
                # style={'backgroundColor': colors['background']},
                # style={'backgroundColor': colors['background']},
                options=prawlers,
                value=prawlers[0]['value'],
                clearable=False
            )
        )
])

date_card = dbc.Card([
    dbc.CardBody(
        dcc.DatePickerRange(
            id='date-picker',
            style={'backgroundColor': colors['background']},
            # min_date_allowed=dataset_dict[starting_set].t_start.date(),
            # max_date_allowed=dataset_dict[starting_set].t_end.date(),
            # start_date=(dataset_dict[starting_set].t_end - datetime.timedelta(days=14)).date(),
            # end_date=dataset_dict[starting_set].t_end.date(),
            # display_format='MMMM Y, DD',
            # start_date_placeholder_text='MMMM Y, DD'
        ),
    )
])

table_card = dbc.Card([
    dbc.CardBody(
        children=[
            dcc.Loading(children=[
                dcc.Textarea(id='t_mean',
                                value='',
                                readOnly=True,
                                style={'width': '100%', 'height': 40,
                                       'backgroundColor': colors['background'],
                                       'textColor':       colors['text']},
                                ),
                    dash_table.DataTable(id='table',
                                         style_table={'backgroundColor': colors['background'],
                                                      'height'         :'300px',
                                                      'overflowY'       :'auto'},
                                                      #'overflow'      : 'scroll'},
                                         style_cell={'backgroundColor': colors['background'],
                                                     'textColor':       colors['text']}
                    )
            ])
        ])
])

graph_card = dbc.Card(
    [
        dcc.Loading(
         dbc.CardBody([dcc.Graph(id='graph')
                       ])
        )
    ]
)


app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                #requests_pathname_prefix='/prawler/m200/',
                external_stylesheets=[dbc.themes.SLATE])
#server = app.server

app.layout = dhtml.Div([
   #dbc.Container([
            dbc.Row([dhtml.H1('Prawler M200')]),
            dbc.Row([
                dbc.Col(graph_card, width=9),
                dbc.Col(children=[date_card,
                                  set_card,
                                  variables_card,
                                  table_card],
                        width=3)
                    ])
   #             ])
])


'''
========================================================================================================================
Callbacks
'''

#engineering data selection
@app.callback(
    [Output('select_var', 'options'),
    Output('date-picker', 'min_date_allowed'),
    Output('date-picker', 'max_date_allowed'),
    Output('date-picker', 'start_date'),
    Output('date-picker', 'end_date'),
    Output('select_var', 'value')],
    Input('select_eng', 'value'))

def change_prawler(dataset):
    
    set_obj = erdr.Dataset(dataset_dict[dataset])

    min_date_allowed = set_obj.t_start.date(),
    max_date_allowed = set_obj.t_end.date(),
    start_date = (set_obj.t_end - datetime.timedelta(days=14)).date(),
    end_date = set_obj.t_end.date()

    vars = set_obj.gen_drop_vars(skips=['time', 'latitude', 'longitude', 'timeseries_id', 'NC_GLOBAL'])
    first_var = vars[0]['value']


    return vars, str(min_date_allowed[0]), str(max_date_allowed[0]), str(start_date[0]), str(end_date), first_var

#engineering data selection
@app.callback(
    [Output('graph', 'figure'),
     Output('table', 'data'),
     Output('table', 'columns'),
     Output('t_mean', 'value')],
    [Input('select_eng', 'value'),
     Input('select_var', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')
    ])

def plot_evar(dataset, select_var, start_date, end_date):
    '''
    :param dataset:
    :param select_var:
    :return:

    '''

    #ctx = dash.callback_context

    # if len(ctx.triggered) == 1:
    #
    #     if 'date-picker' in ctx.triggered[0]['prop_id']:

    set_obj = erdr.Dataset(dataset_dict[dataset])
    data = set_obj.get_data(True, [select_var])
    new_data = set_obj.ret_windowed_data(t_start=start_date, t_end=end_date)
    # new_data = set_obj.ret_data()

    t_mean = ''

    #new_data = set_obj.ret_data(start_date, end_date)

    # colorscale = 'Blues'
    #
    # print(dataset)
    #
    # if dataset in ['TELONAS2Gen', 'M200Sci']:
    colorscale = px.colors.sequential.Viridis

    if select_var == 'trips_per_day':

        trip_set = set_obj.trips_per_day(start_date, end_date)
        efig = px.scatter(trip_set, y='ntrips', x='days')#, color="sepal_length", color_continuous_scale=colorscale)

        columns = [{"name": 'Day', "id": 'days'},
                   {'name': select_var, 'id': 'ntrips'}]

        t_mean = "Mean Trips per day: " + str(trip_set['ntrips'].mean())

        try:
            table_data = trip_set.to_dict('records')
        except TypeError:
            table_data = trip_set.to_dict()

    elif select_var == 'errs_per_day':

        err_set = set_obj.errs_per_day(start_date, end_date)
        efig = px.scatter(err_set, y='nerrors', x='days')#, color="sepal_length", color_continuous_scale=colorscale)

        columns = [{"name": 'Day', "id": 'days'},
                   {'name': select_var, 'id': 'nerrors'}]

        t_mean = 'Mean errors per day ' + str(err_set['nerrors'].mean())

        try:
            table_data = err_set.to_dict('records')
        except TypeError:
            table_data = err_set.to_dict()

    elif select_var == 'sci_profs':

        sci_set = set_obj.sci_profiles_per_day(start_date, end_date)
        efig = px.scatter(sci_set, y='ntrips', x='days')#, color="sepal_length", color_continuous_scale=colorscale)

        columns = [{"name": 'Day', "id": 'days'},
                   {'name': select_var, 'id': 'ntrips'}]

        t_mean = 'Mean errors per day ' + str(sci_set['ntrips'].mean())

        try:
            table_data = sci_set.to_dict('records')
        except TypeError:
            table_data = sci_set.to_dict()

    #elif select_var in list(new_data.columns):

    else:
        efig = px.scatter(new_data, y=select_var, x='time')#, color="sepal_length", color_continuous_scale=colorscale)

        columns = [{"name": 'Date', "id": 'datetime'},
                   {'name': select_var, 'id': select_var}]

    try:
        t_mean = 'Average ' + select_var + ': ' + str(new_data.loc[:, select_var].mean())
    except TypeError:
        t_mean = ''

    try:
        table_data = new_data.to_dict('records')
    except TypeError:
        table_data = new_data.to_dict()

    if 'depth' in select_var.lower():

        efig['layout']['yaxis']['autorange'] = "reversed"

    efig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    # efig.style(
    #     height=700
    # )

    return efig, table_data, columns, t_mean


if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)