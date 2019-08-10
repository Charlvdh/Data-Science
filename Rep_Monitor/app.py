import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import numpy as np
import back_end_integration as bei


colors = {
    'background': '#ffffff',
    'black': '#000000',
    'deloitte_green': '#86BC25',
    'deloitte_aqua': '#00A3E0',
    'deloitte_white': '#ffffff'
}

# placeholder_df to start off with
placeholder_df = pd.DataFrame([[0.0, 0.32682400941848755, 'Deloitte is full of corruption', '2019-06-23', '1', "neg_topic_1"],
                        [0.0, 0.32682400941848755, 'Deloitte is full of corruption', '2019-06-23', '1', "neg_topic_2"],
                        [1.0, 0.8592533469200134, 'Deloitte a favorite amoung listed companies', '2019-06-21', '1', "pos_topic_1"],
                        [1.0, 0.8592533469200134, 'Deloitte a favorite amoung listed companies', '2019-06-21', '1', "pos_topic_2"],
                        [0.0, 0.17859989404678345, 'Deloitte in the middle of yet another accounting scandal', '2019-06-20', '1', "neg_topic_3"],
                        [1.0, 0.841434895992279, 'Deloitte is the best accounting firm in South Africa', '2019-06-20', '1', "pos_topic_3"],
                        [1.0, 0.916645884513855, 'Having an amazing time at Deloitte', '2019-06-19', '1', "pos_topic_3"],
                        [0.0, 0.026026848703622818, 'Deloitte is a lost cause', '2019-06-17', '1', "neg_topic_3"]],
                        columns=["hard_pred", "soft_pred", "original_text", "created_at", "topic_id", "topic"])

# Initialise result_df as empty df as need to draw from this later
result_df = pd.DataFrame()

# Set up topics list to assist with referencing topic button ids later
pos_topic_ids = ['pos_topic_1', 'pos_topic_2', 'pos_topic_3']
neg_topic_ids = ['neg_topic_1', 'neg_topic_2', 'neg_topic_3']

# Set up figure and rep_children to assist with referencing them later
figure = 0
rep_children = 0
rep_score = 0
pie_chart = 0
table_1_children = 0
table_2_children = 0

# Set up topic_list
topic_list = []

# Topic tables
def generate_topic_tables(df, name):

    # Set topic_ds as empty list initially
    topic_ids = []

    # If statement for button color
    if df["hard_pred"].unique() == 1:
        button_background = colors['deloitte_green']
        button_text = colors['black']
        topic_ids = pos_topic_ids
        # Empty out topic_list
        global topic_list
        topic_list = []
    else:
        button_background = colors['black']
        button_text = colors['deloitte_white']
        topic_ids = neg_topic_ids

    # Get unique topics
    topics = df["topic"].unique()

    print(topics)

    for topic in topics:
        topic_list.append(topic)

    return html.Div([
    html.H3(children=name),
    html.Div([
    html.Div(children=topics[0], style={'display': 'inline-block'} ,className = "seven columns"),
    html.Button('Explore', id=topic_ids[0], style={'backgroundColor': button_background, 'color': button_text, 'display': 'inline-block'})
    ]),
    html.Div([
    html.Div(children=topics[1], style={'display': 'inline-block'} ,className = "seven columns"),
    html.Button('Explore', id=topic_ids[1], style={'backgroundColor': button_background, 'color': button_text, 'display': 'inline-block'})
    ]),
    html.Div([
    html.Div(children=topics[2], style={'display': 'inline-block'} ,className = "seven columns"),
    html.Button('Explore', id=topic_ids[2], style={'backgroundColor': button_background, 'color': button_text, 'display': 'inline-block'})
    ])
    ])

# Tweet tables
def generate_table(series, topic, max_rows=10):

    # reset index so can loop over tweets
    series = series.reset_index()

    print(series['original_text'])

    return html.Table(
        # Header
        [html.Tr(topic, style={'fontWeight': 'bold'})] +

        # Body
        [html.Tr(html.Td(series['original_text'][i])) for i in range(min(series['original_text'].size, max_rows))]
    )

# Set external stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initialise app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Set up app layout
app.layout = html.Div([

    # Headers
    html.Div([
        html.Div([
            html.H1(
                children='Rep Monitor',
                style={
                    'textAlign': 'right',
                    'color': colors['black']
                }
            )
        ], className = "six columns", id = "headerDiv1"),
        html.Div([
            html.H3(
                children='by ',
                style={
                    'textAlign': 'left',
                    'color': colors['black'],
                    'display': 'inline-block'
                }
            ),
            html.Img(
                src='https://nextreality.com/wp-content/uploads/2019/02/deloitte.png',
                style={
                'height': '3em',
                'width': '8em',
                'display': 'inline-block',
                'verticalAlign': 'bottom',
                'marginBottom': '0.7em'
                }
            )
        ], className = "six columns", id = "headerDiv2", style={'marginLeft': '1em', 'display':'inline'})
    ], className = "row", id = "outerHeaderDiv"),

    # Inputs and rep_score
    html.Div([
        html.Div([
            html.Div([
                dcc.Input(id='input-box1', type='text', value = "@DeloitteSA")
            ], className = "three columns", id = "queryStringDiv", style={'marginRight': '1em'}),
            html.Div([
                dcc.Input(id='input-box2', type='text', value = "2019-05-19")
            ], className = "three columns", id = "fromStringDiv", style={'marginRight': '1em'}),
            html.Div([
                html.Button('Submit a query', id='submit-button', style={'backgroundColor': colors['deloitte_green'], 'color': colors['black']})
            ], className = "three columns", id = "submitButtonDiv", style={'marginLeft': '2em'})
        ], className = "six columns", id = "queryDiv"),
        html.Div([
            html.H2(
                id='rep_score',
                style={
                    'textAlign': 'center',
                    'color': colors['black'],
                }
            )
        ], className = "six columns", id = "scoreDiv")
    ], className = "row", id = "outerQueryDiv", style={'marginTop': '2em'}),

    # Tables and pie chart
    html.Div([
        html.Div([
            html.Div(className = "row", id = "innerTableDiv1", children = generate_topic_tables(placeholder_df.loc[placeholder_df["hard_pred"]==1], "Positive Themes")),
            html.Div(className = "row", id = "innerTableDiv2", children = generate_topic_tables(placeholder_df.loc[placeholder_df["hard_pred"]==0], "Negative Themes")),
        ], className = "eight columns", id = "outerTableDiv"),
        html.Div([
            dcc.Graph(
                id='pie_chart',
            )
        ], className = "four columns", id = "pieDiv")
    ], className = "row", id = "tableAndPieDiv", style={'marginTop': '2em'}),

    # Bottom div for tweet table
    html.Div([

    ], className = "row", id = "tweetTableDiv", style={'marginTop': '2em'})

], id = "mainOuterDiv", style={'padding': '1em'})

# Callbacks

# Callback to show themes, plot graphs, calc rep score, etc
@app.callback(
    [Output('pie_chart', 'figure'),
     Output('rep_score', 'children'),
     Output('innerTableDiv1', 'children'),
     Output('innerTableDiv2', 'children'),
     Output('tweetTableDiv', 'children')
     ],
    [Input('submit-button', 'n_clicks'),
    Input(pos_topic_ids[0], 'n_clicks'),
    Input(pos_topic_ids[1], 'n_clicks'),
    Input(pos_topic_ids[2], 'n_clicks'),
    Input(neg_topic_ids[0], 'n_clicks'),
    Input(neg_topic_ids[1], 'n_clicks'),
    Input(neg_topic_ids[2], 'n_clicks')],
    [State('input-box1', 'value'),
     State('input-box2', 'value')])
def on_click(*args):

    global figure
    global rep_children
    global table_1_children
    global table_2_children

    n_clicks = args[0]
    q = args[-2]
    since = args[-1]

    if n_clicks == None:

        # Pie chart
        num_pos_tweets = placeholder_df["hard_pred"].sum()
        num_neg_tweets = placeholder_df["soft_pred"].shape[0] - num_pos_tweets
        rep_score = int(np.multiply(placeholder_df["soft_pred"].mean(), 100))


        labels = ["Positive","Negative"]
        values = [num_pos_tweets, num_neg_tweets]

        pie_chart = go.Pie(labels=labels,
                           values=values,
                           marker=dict(colors=[colors['deloitte_green'], colors['black']],
                                       line=dict(color=colors['deloitte_white'], width=2)))

        figure={
            'data': [
                pie_chart
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['black']
                },
                 'margin':{
                        'l':0,
                        'r':0,
                        'b':0,
                        't':0,
                        'pad':'1em'
                 }
            }
        }

        # rep score
        rep_children=f'Rep Score: {rep_score}%'

        #Themes
        table_1_children = generate_topic_tables(placeholder_df.loc[placeholder_df["hard_pred"]==1], "Positive Themes")
        table_2_children = generate_topic_tables(placeholder_df.loc[placeholder_df["hard_pred"]==0], "Negative Themes")

        # Tweet tables (empty)
        tweet_table_children = html.Div([])

        return figure, rep_children, table_1_children, table_2_children, tweet_table_children

    elif n_clicks > 0 and any(args[1:7]) == False:

        q = q
        since = since

        print(q)
        print(since)

        # Get result
        global result_df
        result_df = bei.get_predictions(q, since)

        # Pie chart
        num_pos_tweets = result_df["hard_pred"].sum()
        num_neg_tweets = result_df["soft_pred"].shape[0] - num_pos_tweets
        rep_score = int(np.multiply(result_df["soft_pred"].mean(), 100))

        labels = ["Positive","Negative"]
        values = [num_pos_tweets, num_neg_tweets]

        pie_chart = go.Pie(labels=labels,
                           values=values,
                           marker=dict(colors=[colors['deloitte_green'], colors['black']],
                                       line=dict(color=colors['deloitte_white'], width=2)))

        figure={
            'data': [
                pie_chart
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['black']
                },
                 'margin':{
                        'l':0,
                        'r':0,
                        'b':0,
                        't':0,
                        'pad':'1em'
                 }
            }
        }

        # rep score
        rep_children=f'Rep Score: {rep_score}%'

        #Themes
        table_1_children = generate_topic_tables(result_df.loc[result_df["hard_pred"]==1], "Positive Themes")
        table_2_children = generate_topic_tables(result_df.loc[result_df["hard_pred"]==0], "Negative Themes")

        # Tweet tables (empty)
        tweet_table_children = html.Div([])

        return figure, rep_children, table_1_children, table_2_children, tweet_table_children

    elif n_clicks > 0 and any(args[1:7]) == True:

        # Determine which explore button was clicked
        topic_inputs = args[1:7]
        selected_topic = topic_list[topic_inputs.index(1)]

        # Set up new outputs


        tweets_for_table = result_df.loc[(result_df["topic"] == selected_topic), "original_text"]

        print(tweets_for_table)

        tweet_table_children = generate_table(tweets_for_table, selected_topic, max_rows=10)

        return [figure, rep_children, table_1_children, table_2_children, tweet_table_children]



if __name__ == '__main__':
    app.run_server(debug=True)
