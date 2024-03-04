from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import base64
import datetime
import io

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

external_stylesheets = [dbc.themes.CYBORG, dbc.icons.BOOTSTRAP]

def reformat_df(df):
    new_df = df.replace({'Rarity':{ '★★★': '3',
                                    '★★★★':'4',
                                    '★★★★★': '5'}})
    return new_df

banners_dict = {
    'all Statistics' : 'stored-Banners',
    'Stellar Warp' : 'stored-stellar',
    'Departure Warp' : 'stored-departure',
    'Character Event Warp' : 'stored-char',
    'Light Cone Event Warp' : 'stored-cone'
    }

app = Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

app.layout = dbc.Container([
    html.H1("Honkai: Star Rail Warp Dashboard"),
    html.Hr(),
    
    dbc.Row(
            [   
                dbc.Col(
                    html.Div(
                        dcc.Upload(
                            id='upload-data',
                            children=dbc.Button('Select Files', color="light", className="me-1"),
                            # Allow multiple files to be uploaded
                            multiple=False
                        ), className=".col-md-4"
                    )
                ),
                dbc.Col(
                    html.Div(id='output-data-upload'),
                    className=".col-xs-12 .col-md-8"
                )
            ],
            align="center",
        ),
    html.Hr(),
    dbc.Row([
                dbc.Col(
                    html.Div(id='output-div'), class_name=".col-xs-6 .col-md-4"
                    )
            ]
        ),
    dcc.Store(id='store-data-selected', data=[], storage_type='memory')
    ],
    fluid=True
)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            # banner_xlsx = pd.ExcelFile(io.BytesIO(decoded))
            df_banners = reformat_df(pd.read_excel(io.BytesIO(decoded), sheet_name='Banners'))
            df_stellar = reformat_df(pd.read_excel(io.BytesIO(decoded), sheet_name='Stellar Warp'))
            df_departure = reformat_df(pd.read_excel(io.BytesIO(decoded), sheet_name='Departure Warp'))
            df_char_event = reformat_df(pd.read_excel(io.BytesIO(decoded), sheet_name='Character Event Warp'))
            df_lightcone = reformat_df(pd.read_excel(io.BytesIO(decoded), sheet_name='Light Cone Event Warp'))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return dbc.Container([

        html.Div(
            [   
                
                dcc.Store(id='stored-banner', data=df_banners.to_dict('records'), storage_type='memory'),
                dcc.Store(id='stored-stellar', data=df_stellar.to_dict('records'), storage_type='memory'),
                dcc.Store(id='stored-departure', data=df_departure.to_dict('records'), storage_type='memory'),
                dcc.Store(id='stored-char', data=df_char_event.to_dict('records'), storage_type='memory'),
                dcc.Store(id='stored-cone', data=df_lightcone.to_dict('records'), storage_type='memory'),
                dbc.Label("Banners"),
                dcc.Dropdown(
                    id="banner-set",
                    options=[
                        {"label": keys, "value": keys} for keys in banners_dict
                    ],value='all Statistics'),
            ]
        ),
        # html.H5(filename),
        # html.H6(datetime.datetime.fromtimestamp(date)),

        # dash_table.DataTable(
        #     df.to_dict('records'),
        #     [{'name': i, 'id': i} for i in df.columns]
        # ),

        # html.Hr(),  # horizontal line    
    ])



@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        if type(list_of_contents) != list:
            list_of_contents = [list_of_contents]
        if type(list_of_names) != list:
            list_of_names = [list_of_names]
        if type(list_of_dates) != list:
            list_of_dates = [list_of_dates]
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    

@app.callback(
    Output('store-data-selected', 'data'),
    State('stored-banner', 'data'),
    State('stored-stellar', 'data'),
    State('stored-departure', 'data'),
    State('stored-char', 'data'),
    State('stored-cone', 'data'),
    Input('banner-set', 'value')
)

def select_data(data_banners, data_stellar, data_departure, data_char, data_cone, value):
    if value == 'all Statistics':
        dataset = data_banners
    elif value == 'Stellar Warp':
        dataset = data_stellar
    elif value == 'Departure Warp':
        dataset = data_departure
    elif value == 'Character Event Warp':
        dataset = data_char
    elif value == 'Light Cone Event Warp':
        dataset = data_cone
    return dataset

@app.callback(
    Output('output-div', 'children'),
    Input('store-data-selected', 'data')
)

def create_table(data):
    df = pd.DataFrame(data)

    my_table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records')
    )
    return my_table
# @app.callback(Output('output-div', 'children'),
#                 Input('stored-Banners','data'),
#                 Input('stored-stellar','data'),
#                 Input('stored-departure','data'),
#                 Input('stored-cone','data'),
#                 Input('stored-char','data')
#               )
# def update_layout(value, data):
#     print(f"selected value: {value}")
#     df = pd.DataFrame(data)
#     if value == 'all Statistics':
#         return dbc.Card([
#             dbc.col(
#                 dbc.Label("average pull")
#             ),
#             dbc.Col(
#                 dash_table.DataTable(
#                     df.to_dict('records'),
#                     [{'name': i, 'id': i} for i in df.columns]
#                 )
#             )
#         ])


if __name__=='__main__':
    app.run(debug=True)