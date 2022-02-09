import json
import logging

from sqlalchemy import create_engine
import tensorflow as tf
import tensorflow_hub as hub

import pandas as pd
import  numpy as np
from tensorflow import keras


class Multi_Sentiment_Classifier:
    def __init__(self,module):
        self.model= keras.models.load_model('sentiment_classifier2')
        self.module=module

    def sentences_vectors(self,sentences, batch: int = 1000):
        """
        Compute the sentence embedding in batches to make it memory
        efficient.
        :param sentences: iterable of strings
        :param batch: batches size to compute the embeddings.The smaller
        the longer it takes.
        :return:  numpy nmatrix  of shape (X,512)
        """

        lower = 0
        upper = batch
        sent_vectors = self.module.signatures['question_encoder'](
            tf.constant(sentences[lower:upper]))["outputs"]
        while upper < len(sentences):
            lower += batch
            upper += batch
            print(lower)
            if sentences:
                sent_vectors = np.concatenate(
                    (sent_vectors, self.module.signatures['question_encoder'](
                        tf.constant(sentences[lower:upper]))["outputs"]))
        return sent_vectors

    def sentiment(self,s_setence: str) -> str:
        s_vector = self.sentences_vectors([s_setence])
        s_prediction = (self.model.predict(s_vector.numpy()) > 0.5).astype("int32")
        s_prediction = np.argmax(s_prediction, axis=1)
        s_prob = self.model.predict(s_vector.numpy())
        decode = {1: 'positive', 0: 'negative'}
        sentiment = decode[s_prediction[0]] if s_prob.max() >= 0.7 else 'neutral'
        return sentiment






def get_lg(word,sentiment_classifier):
    result = sentiment_classifier.sentiment(word)
    print(result)
    return  result;

if __name__=="__main__":
    file=open('Booking/twint/hotel_test.json');
    json_file=json.load(file);
    logger = logging.getLogger()
    module=hub.load("C:\Users\grich\Downloads\Compressed\universal-sentence-encoder-multilingual-qa_2.tar.");
    sentiment_classifier=Multi_Sentiment_Classifier(module);
    logging.basicConfig(filename="dash_logger.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/projetbi', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    query = 'SELECT DISTINCT fact_table.Comment ,fact_table.Review_score ,dim_hotel.Id_hotel,dim_room.Room_type,dim_reviewer.Reviewer_nationality,dim_reviewer.Number_of_night,dim_reviewer.Visite_date from fact_table,dim_room,dim_reviewer,dim_hotel,dim_date WHERE fact_table.Id_hotel=dim_hotel.Id_hotel and fact_table.Id_reviewer=dim_reviewer.Id_reviewer and fact_table.Id_room=dim_room.Id_room and fact_table.Id_time=dim_date.Id_time;'
    hotels_dataSet = pd.read_sql(query, dbConnection);
    is_id_hotel = hotels_dataSet['Id_hotel'] == '1H'
    hotels_dataSet=hotels_dataSet.loc[is_id_hotel]
    hotels_dataSet['Comment_en'] = hotels_dataSet.apply(lambda x: get_lg(x['Comment'],sentiment_classifier), axis=1)
    print(hotels_dataSet.tail())
    dbConnection.close()


