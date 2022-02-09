import logging
import time

import dash
from IPython.core.display_functions import display
from dash import html, dcc
import plotly.express as px
import pycountry
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from sqlalchemy import create_engine
import pandas as pd


# Initialize the app
app = dash.Dash(__name__)
logger = logging.getLogger()
logging.basicConfig(filename="dash_logger.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
app.config.suppress_callback_exceptions = True
sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/test_database', pool_recycle=3600)
dbConnection = sqlEngine.connect()
logger.debug("get hotels details by id")
hotel_list=[]

def get_options():
    sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/test_database', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    logger.debug("get hotels list")
    try:
        df = pd.read_sql("SELECT * FROM `dim_hotel` ;", dbConnection)
        global hotel_list
        hotel_list=df;
        test = zip(df.Id_hotel, df.Hotel_name);
        dict_hotels = dict(test)
        list_drop_down = []
        for i, (key, value) in enumerate(dict_hotels.items()):
            list_drop_down.append({'label': value.replace('Hotel',''), 'value': key})
        logger.info("SELECT * FROM `dim_hotel` ;")
        return list_drop_down
    except Exception as e:
        logger.error(e)
        dbConnection.close()
        return "";


app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls',
                              children=[
                                  html.H2('Project BI'),
                                  html.P('Assessment of hotels e-reputation'),
                                  html.P('Pick one Hotel from the dropdown below.'),
                                  html.Div(
                                      className='div-for-dropdown',
                                      children=[
                                          dcc.Dropdown(id='stockselector', options=get_options(),
                                                       multi=False, value=get_options()[0]['value'],
                                                       style={'backgroundColor': '#1E1E1E'},
                                                       className='stockselector'
                                                       ),
                                      ],
                                      style={'color': '#1E1E1E'}),
                                  html.Br(),
                                  html.H2("Sentiment Analysis"),
                                  html.Div(children=[
                                      html.Div(className="sentiment_box",
                                               children=[
                                                   html.Span(id="sl_rs", children=''),
                                                   html.Img(src="/assets/smiling-face.png", className="img_smile")
                                               ]

                                               ),
                                      html.Br(),

                                      html.Div(className="sentiment_box",
                                               children=[
                                                   html.Span(id="sad_rs", children=''),
                                                   html.Img(src="/assets/sad.png", className="img_smile")
                                               ]
                                               ),
                                      html.Br()
                                      ,
                                      html.Div(className="sentiment_box",
                                               children=[
                                                   html.Span(id="normal", children=''),
                                                   html.Img(src="/assets/normal.png", className="img_smile")
                                               ]

                                               ),

                                  ], className="sentiment-style bg-grey"),

                              ]
                              ),
                     html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  html.Img(id='photo_p'),
                                  html.Div(
                                    children=[
                                        html.H1("Title: Hotel ", id="title"),
                                        html.H3("Score: ",id="Score")
                                    ]
                                  ),
                                        html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="sous-categories",
                                      animate=True,
                                  ),
                                  html.Br(), dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="scores_graph",
                                      animate=True,
                                  ), html.Br(), dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="graph",
                                      animate=True,
                                  ),
                                  html.Br(),
                                    html.H3("Hotel reviews word cloud"),
                                    html.Img(id='wordCloud'),
                                  html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="emotions_graph",
                                      animate=True,
                                  ),
                                  html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="geo-dist-pie",
                                  ),
                                  html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="geo-dist",
                                  ),html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="room_type",
                                  ), html.Br(),
                              dcc.Graph(
                                  config={'displayModeBar': False},
                                  id="nbr_night_room_type",
                              ),html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="client_type",
                                  ),html.Br(),
                                  dcc.Graph(
                                      config={'displayModeBar': False},
                                      id="client_type_number_of_nights",
                                  )
                              ]
                              ,
                              )
                 ])
    ]

)

query = 'SELECT DISTINCT fact_table.emotions,dim_reviewer.Type_of_stay,fact_table.Review_score ,dim_hotel.Id_hotel,dim_room.Room_type,dim_reviewer.Reviewer_nationality,dim_reviewer.Number_of_night,dim_date.year,dim_date.month from fact_table,dim_room,dim_reviewer,dim_hotel,dim_date WHERE fact_table.Id_hotel=dim_hotel.Id_hotel and fact_table.Id_reviewer=dim_reviewer.Id_reviewer and fact_table.Id_room=dim_room.Id_room and fact_table.Id_time=dim_date.Id_time;'
hotels_dataSet_g = pd.read_sql(query, dbConnection);
dbConnection.close()


@app.callback(Output('graph', 'figure'),
              [Input('stockselector', 'value')])
def comment_count(id):
    try:
        global hotels_dataSet_g;
        hotels_dataSet = hotels_dataSet_g;
        is_id_hotel = hotels_dataSet['Id_hotel'] == id;
        hotels_dataSet = hotels_dataSet.loc[is_id_hotel]
        hotels_dataSet = hotels_dataSet[['year']]
        tmp1 = hotels_dataSet.groupby(['year'])['year'].count().reset_index(name="Number of Reviews")
        f = px.line(
            tmp1, x="year", y="Number of Reviews",title='Number of Reviews  per year',markers=True
        )

        return f;
    except Exception as e:
        dbConnection.close()
        logger.error(e.with_traceback())
        return '';
    finally:
        dbConnection.close();


@app.callback([
    Output("sl_rs", "children"),
    Output("sad_rs", "children"),
    Output("normal", "children"),
    Output('emotions_graph', 'figure')
],
    [Input('stockselector', 'value')])
def anaylseEmotions(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    df2 = df[['emotions', 'year']]
    df = df[['emotions']];
    tmp = df.value_counts(normalize=True).reset_index(name="count");
    tmp2 = df2.value_counts(['emotions', 'year']).reset_index(name="Number of reviews");
    tmp2 = tmp2.sort_values(by="year")
    tmp2['years']=tmp2['year']
    sl_data = tmp[tmp['emotions'].str.contains('positive')]["count"].item();
    sd_data = tmp[tmp['emotions'].str.contains('negative')]['count'].item();
    nr_data = tmp[tmp['emotions'].str.contains('neutral')]['count'].item();
    sl_data = str(round(sl_data * 100, 2)) + " %";
    sd_data = str(round(sd_data * 100, 2)) + " %";
    nr_data = str(round(nr_data * 100, 2)) + " %";
    f = px.line(
        tmp2, x="years", y="Number of reviews", color="emotions",
        color_discrete_map={"positive": "green", "negative": "red", "neutral": "blue"}
        ,title='Number of positive, negative and neutral Reviews per year',markers=True)

    return sl_data, sd_data, nr_data, f;

@app.callback([Output('geo-dist', 'figure'),Output('geo-dist-pie', 'figure')],
    [Input('stockselector', 'value')])
def geo_dist(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    #-----------------------------------------
    df3 = df[['Reviewer_nationality', ]]
    countries = {}
    for country in pycountry.countries:
        countries[country.name] = country.alpha_3

    df3['countries'] = [countries.get(country) for country in df3['Reviewer_nationality']]
    df3 = df3.value_counts(['countries', 'Reviewer_nationality']).reset_index(name="count");
    fig = px.scatter_geo(df3, locations="countries", color="Reviewer_nationality", projection="natural earth",title='Number of reviews per nationality',
                         size="count")
    #----------------------------------------
    df['nationality'] = df[['Reviewer_nationality', ]]
    df2=df[['nationality']]
    df2 = df2.value_counts(['nationality']).reset_index(name="count");
    df2=df2.nlargest(5, 'count')
    df = df.value_counts(['nationality', 'year']).reset_index(name="count");
    fig2 = px.pie(df2, values="count",names='nationality',title='Percentage of reviews per country')
    return fig,fig2
@app.callback(Output('room_type', 'figure'),
    [Input('stockselector', 'value')])
def room_type_dist(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    df = df[['year', 'Room_type']]
    df['les types des chombers'] = df['Room_type']
    df = df.value_counts(['les types des chombers', 'year']).reset_index(name="Number of reviews")
    df = df.nlargest(10, 'Number of reviews');
    figure = px.bar(df, x='year', y='Number of reviews', color='les types des chombers',title=' Number of Reviews for each room type per year')
    return figure

@app.callback(Output('nbr_night_room_type', 'figure'),
    [Input('stockselector', 'value')])
def nbr_night_room_type(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    df5 = df[['Number_of_night', 'Room_type', 'year']]
    df5=df5[~df5['Room_type'].str.contains("nan")]
    df5["Number_of_night"] = pd.to_numeric(df5["Number_of_night"])
    df5 = df5.loc[df['Room_type'].str.contains('night') == False]
    df5 = df5.groupby(['Room_type', 'year'])['Number_of_night'].sum().reset_index(name="number of nights")
    figure = px.histogram(df5, x='year', y='number of nights', color="Room_type", barmode='group',title='Number of nights for each room type per year')
    return figure
@app.callback(Output('client_type_number_of_nights', 'figure'),
    [Input('stockselector', 'value')])
def client_type_number_of_nights(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    df5 = df[['Number_of_night', 'Type_of_stay', 'year']]
    df5=df5[~df5['Type_of_stay'].str.contains("nan")]
    df5["Number_of_night"] = pd.to_numeric(df5["Number_of_night"])
    df5 = df5.loc[df['Type_of_stay'].str.contains('night') == False]
    df5 = df5.groupby(['Type_of_stay', 'year'])['Number_of_night'].sum().reset_index(name="number of nights")
    figure = px.histogram(df5, x='year', y='number of nights',title='Number of nights for each client type per year' ,color="Type_of_stay", barmode='group')
    return figure
@app.callback(Output('client_type', 'figure'),
    [Input('stockselector', 'value')])
def client_type_dist(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    df = df[['year', 'Type_of_stay']]
    df['les types des clients'] = df['Type_of_stay']
    df['years'] = df['year']
    df = df.value_counts().reset_index(name="Number of reviews")
    df = df.sort_values(by=['years'])

    figure = px.histogram(df, x='years', y='Number of reviews', color="les types des clients", barmode='group',title='Number of Reviews for each client type per year ')

    return figure
@app.callback(Output('wordCloud', 'src'),
    [Input('stockselector', 'value')])
def get_wordCloud(value):
    path = 'assets/hotel_wordcloud\\'
    return path+value+"w_c.png"
@app.callback(Output('photo_p', 'src'),
    [Input('stockselector', 'value')])
def get_photos(value):
    path = 'assets/hotel_photo\\'
    return path+value+"_photo.jpeg"
@app.callback([Output('title', 'children'),Output('Score', 'children')],
    [Input('stockselector', 'value')])
def get_info(value):
    global hotel_list;
    df = hotel_list
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    tmp=df.iloc[0]['Hotel_name']
    title=tmp.replace('Hotel','')
    title=title.replace("Hôtel",'')
    title="Title: Hotel "+title
    score="Score: "+df['Score'];
    return title,score;
@app.callback(Output('scores_graph', 'figure'),
    [Input('stockselector', 'value')])
def get_scores(value):
    global hotels_dataSet_g;
    df = hotels_dataSet_g;
    is_id_hotel = df['Id_hotel'] == value;
    df = df.loc[is_id_hotel]
    df_tmp = df[['Review_score', 'year']]
    df_tmp = df_tmp.value_counts(['Review_score', 'year']).reset_index(name="Number of reviews")
    df_tmp = df_tmp.sort_values('year')
    df_tmp['years']=df_tmp['year']
    fig = px.scatter(df_tmp, x="years", y="Number of reviews",
                     color='Review_score'
                     ,title='Reviews score per year',
                     )
    return fig
@app.callback(Output('sous-categories', 'figure'),
    [Input('stockselector', 'value')])
def sous_categories(value):
    global hotel_list;
    df=hotel_list;
    is_id_hotel = df['Id_hotel'] == value;
    df2 = df.loc[is_id_hotel]
    print(df2)
    df2 = df2.T
    N = 4
    df2 = df2.iloc[N:, :]
    df2['sous Categories'] = df2.index
    df2['Scores'] = df2.iloc[:,0]
    df2 = df2.sort_values("Scores")
    fig = px.line_polar(df2, r="Scores", theta='sous Categories', line_close=True,title="Services rating")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
