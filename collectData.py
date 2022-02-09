import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine


if __name__=='__main__':
    sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/test_database', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    query = 'SELECT DISTINCT fact_table.emotions,dim_reviewer.Type_of_stay,fact_table.Review_score ,dim_hotel.Id_hotel,dim_room.Room_type,dim_reviewer.Reviewer_nationality,dim_reviewer.Number_of_night,dim_date.year,dim_date.month from fact_table,dim_room,dim_reviewer,dim_hotel,dim_date WHERE fact_table.Id_hotel=dim_hotel.Id_hotel and fact_table.Id_reviewer=dim_reviewer.Id_reviewer and fact_table.Id_room=dim_room.Id_room and fact_table.Id_time=dim_date.Id_time;'
    df = pd.read_sql(query, dbConnection);
    dbConnection.close()
    is_id_hotel = df['Id_hotel'] == "1HL8s9dzei0H";
    df = df.loc[is_id_hotel]
    print(df)
    print("test")

