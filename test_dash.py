from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import base64
import datetime
import io

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px


from src import GenerateFigs

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

overall_drop_name = ['average number of pulls for 5 stars',
                     'average number of pulls for 4 stars']

app = Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

app.layout = dbc.Container([
    html.Div(
        html.H1("Honkai: Star Rail Warp Dashboard"), style={'textAlign':'center'}
    ),
    
    html.Hr(),
    
    dbc.Row(
            [   
                dbc.Col(
                    html.Div(
                        dcc.Upload(
                            id='upload-data',
                            children=dbc.Button('Select Files', color="light", class_name="m-2"),
                            # Allow multiple files to be uploaded
                            multiple=False
                        )
                    )
                ),
                dbc.Col(
                    html.Div(id='output-data-upload'),
                )
            ],
            align="center",
        ),
    html.Hr(),
    html.Div(id='output-div'),
    dcc.Store(id='store-data-selected', data=[], storage_type='memory'),
    dcc.Store(id='store-data-evo', data=[], storage_type='memory')
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
    Input('store-data-selected', 'data'),
    Input('banner-set', 'value')
)

# def create_table(data):
#     df = pd.DataFrame(data)

#     my_table = dash_table.DataTable(
#         columns=[{"name": i, "id": i} for i in df.columns],
#         data=df.to_dict('records')
#     )
#     return my_table

def update_layout(data, value):
    print(f"selected value: {value}")
    df = pd.DataFrame(data)
    if value == 'all Statistics':
        df = df.rename(columns={'AVG Pity 5★':'avg_pity_5_star', '5★': '5_star', '4★':'4_star', 'AVG Pity 4★':'avg_pity_4_star'})
        df_banners_tsliced = df.loc[:, :'avg_pity_4_star']
        df_grouped_type = df_banners_tsliced.groupby(['Type']).sum()

        avg_five__strs_pulls = df['avg_pity_5_star'][df['avg_pity_5_star']>0].mean()
        total_warp = df['Warps'].sum()

        nb_4star_char_event = df_grouped_type.loc['Character Event Warp', '4_star']
        nb_4star_beginner_banner = df_grouped_type.loc['Departure Warp', '4_star']
        nb_4star_cone_banner = df_grouped_type.loc['Light Cone Event Warp', '4_star']
        nb_4star_normal_banner = df_grouped_type.loc['Stellar Warp', '4_star']

        layout = dbc.Row(
            [
                dbc.Col(
                    dbc.Row([
                        dbc.Card([
                            dbc.Row(
                                dbc.Label("average numbers of pulls for a 5 star:"),class_name='mt-4', align='center'
                            ),
                            dbc.Row(
                                dbc.Label(avg_five__strs_pulls), align='center'
                            )
                        ],class_name='mt-2 mb-2'),
                        dbc.Card([
                            dbc.Row(
                                dbc.Label("total Warp: "),class_name='mt-4', align='center'
                            ),
                            dbc.Row(
                                dbc.Label(total_warp), align='center'
                            )
                        ],class_name='mt-2 mb-2'),
                        dbc.Card([
                            dbc.Row(
                                dbc.Label(f"nb of 4 star for Event banner: {nb_4star_char_event}"), class_name='mt-4'
                            ),
                            html.Hr(),
                            dbc.Row(
                                dbc.Label(f"nb of 4 star for Light Cone banner: {nb_4star_cone_banner}")
                            ),
                            html.Hr(),
                            dbc.Row(
                                dbc.Label(f"nb of 4 star for Normal banner: {nb_4star_normal_banner}")
                            ),
                            html.Hr(),
                            dbc.Row(
                                dbc.Label(f"nb of 4 star for Beginner banner: {nb_4star_beginner_banner}"), class_name='mb-4'
                            )
                        ], class_name='mt-2 mb-2')

                    ]), width=2, class_name='m-2'
                ),
                dbc.Col([
                    dbc.Row(
                        dcc.Dropdown(
                            id='overal_dropdown',
                            options=overall_drop_name,
                            value=overall_drop_name[0]
                        ), class_name='mb-4'
                    ),
                    dbc.Row(
                        dcc.Graph(id='evo_average_pull')
                    )], 
                    width=9, class_name='m-2'
            ),


            ]
        )
    else:
        layout = html.Div(html.H3("Work In progress"), style={'textAlign':'center'})
    return layout

@app.callback(
    Output('evo_average_pull', 'figure'),
    Input('overal_dropdown', 'value'),
    Input('store-data-selected', 'data')
)

def update_evo_graph(dropdown_value, df_data):
    print(f'dropdown value: {dropdown_value}')
    df = pd.DataFrame(df_data)
    df = df.rename(columns={'AVG Pity 5★':'avg_pity_5_star', '5★': '5_star', '4★':'4_star', 'AVG Pity 4★':'avg_pity_4_star'})
    df = df[df['Type'] == 'Character Event Warp']
    fig = GenerateFigs.evo_average_pull(dropdown_value, df)
    return fig



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