import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def evo_average_pull(dropdown_value, df):

    if dropdown_value == 'average number of pulls for 5 stars':
        fig = px.line(df, x='Start Time', y='avg_pity_5_star', markers='.', hover_name="Rate UP")
        fig.update_layout(title='Average Number of pulls for 5 stars by Event Banner',
                   xaxis_title='Date',
                   yaxis_title='Average number of pulls)')

    else:
        fig = px.line(df, x='Start Time', y='avg_pity_4_star', markers='.', hover_name="Rate UP")
        fig.update_layout(title='Average Number of pulls for 4 stars by Event Banner',
                   xaxis_title='Date',
                   yaxis_title='Average number of pulls)')

    return fig