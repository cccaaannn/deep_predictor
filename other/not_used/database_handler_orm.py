from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import time

Base = declarative_base() 

class prediction_record(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    prediction_id = Column(String, unique=True)
    prediction_status = Column(Integer)
    prediction = Column(String)
    image_path = Column(String)
    model_info = Column(String)
    model_id = Column(Integer)
    prediction_time = Column(Integer)


    def __init__(self, prediction_id, model_info, model_id):
        """creates new prediction with status 100(predicting)"""
        self.prediction_id = prediction_id
        self.prediction_status = 100
        self.prediction = ""
        self.image_path = ""
        self.model_info = str(model_info)
        self.model_id = int(model_id)
        self.prediction_time = int(time.time())


    def update_successful_prediction(self, prediction, image_path):
        """updates successful prediction status 200"""
        self.prediction_status = 200
        self.prediction = prediction
        self.model_info = str(model_info)
        self.model_id = int(model_id)
        self.image_path = image_path
        self.prediction_time = int(time.time())


    def update_failed_prediction(self, prediction_status):
        """updates failed prediction wit status code other than 200"""
        self.prediction_status = prediction_status
        self.prediction_time = int(time.time())

    def to_json(self):
        """converst prediction_record to json"""
        # database can save single quotes but json function needs double quoutes so we have this sad line
        model_info_json = json.loads(str( self.model_info).replace("'","\""))

        if(self.prediction_status == 200):
            predictions_json = json.loads(str(self.prediction).replace("'","\""))
            return {"prediction_id" : self.prediction_id, 
                    "prediction_status" : self.prediction_status, 
                    "predictions" : predictions_json["predictions"],
                    "model_info" : model_info_json,
                    "prediction_time" : self.prediction_time
                    }
        else:
            return {"prediction_id" : self.prediction_id, 
                    "prediction_status" : self.prediction_status, 
                    "predictions" : "",
                    "model_info" : model_info_json,
                    "prediction_time" : self.prediction_time
                    }



    def __repr__(self):
        """represent prediction_record object"""
        return (
        """
        prediction_id = {0}
        prediction_status = {1}
        prediction = {2}
        image_path = {3}
        model_info = {4}
        model_id = {5}
        prediction_time = {6}
        """.format(self.prediction_id, self.prediction_status, self.prediction, self.image_path, self.model_info, self.model_id, self.prediction_time)
        )



import sqlite3
import json
import time
import os

from logger_creator import logger_creator

class database_handler():
    def __init__(self, database_path = "database/database.db"):
        self.logger = logger_creator().database_handler_logger()

        self.engine = create_engine("sqlite:///{}".format(database_path))

        self.check_connection()


    def check_connection(self):
        """checks connection to db"""
        try:
            session = scoped_session(sessionmaker(bind=self.engine))()
            print("db connected")
        except:
            print("db error")


    def create_prediction(self, prediction_id, model_info, model_id):
        """creates prediction with 100 status code"""
        try:
            session = scoped_session(sessionmaker(bind=self.engine))()
            new_prediction_record = prediction_record(prediction_id, model_info, model_id)
            session.add(new_prediction_record)
            session.commit()
        except sqlite3.IntegrityError:
            print("most likely you are trying to write douplicate of a unique field")
        except:
            print("aaaaaaaaaaaaaa")
    

    def delete_prediction(self, prediction_id):
        try:
            session = scoped_session(sessionmaker(bind=self.engine))()
            session.query(prediction_record).filter(prediction_record.prediction_id == prediction_id).delete()
            session.commit()
        except:
            print("aaaaaaaa")


    def update_successful_prediction(self, prediction_id, prediction, image_path):
        """updates successful prediction"""
        try:
            session = scoped_session(sessionmaker(bind=self.engine))()
            successful_prediction = session.query(prediction_record).filter(prediction_record.prediction_id == prediction_id).first()
            successful_prediction.update_successful_prediction(prediction, image_path)
            session.commit()
        except:
            print("aaaaaaaa")


    def update_failed_prediction(self, prediction_id, prediction_status):
        """updates failed prediction"""
        try:
            session = scoped_session(sessionmaker(bind=self.engine))()
            failed_prediction = session.query(prediction_record).filter(prediction_record.prediction_id == prediction_id).first()
            failed_prediction.update_failed_prediction(prediction_status)
            session.commit()
        except:
            print("aaaaaaaa")


    def is_prediction_exists(self, prediction_id):
        """returns true if prediction id exists on the database"""
        session = scoped_session(sessionmaker(bind=self.engine))()
        prediction = session.query(prediction_record).filter(prediction_record.prediction_id == prediction_id).first()

        if(prediction):
            return prediction.prediction_status
        else:
            return 0


    def get_prediction_json(self, prediction_id):
        """returns prediction information as json by using prediction id"""
        session = scoped_session(sessionmaker(bind=self.engine))()
        prediction = session.query(prediction_record).filter(prediction_record.prediction_id == prediction_id).first()
        if(prediction):
            return  prediction.to_json()
        else:
            return {"prediction_status" : 0}


