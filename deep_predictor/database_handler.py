import sqlite3
import json
import time
import os

from logger_creator import logger_creator
from helpers.file_folder_operations import file_folder_operations


class database_handler():
    def __init__(self, database_path = "database/database.db", check_connection = False, create_table = False):
        self.logger = logger_creator().database_handler_logger()
        self.database_path = database_path
        if(check_connection):
            self.check_connection()
        if(create_table):
            self.create_table_if_not_exists()

    def check_connection(self):
        """checks connection to db"""
        try:
            with sqlite3.connect(self.database_path) as _:
                self.logger.info("db connected on path {0}".format(self.database_path))
        except:
            self.logger.critical("can not connect to database on path {0}".format(self.database_path), exc_info=True)


    def create_table_if_not_exists(self):
        """creates predictions table if not exits"""
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.info("function: {0}".format("create_table_if_not_exists"))
                query = """CREATE TABLE IF NOT EXISTS "predictions" (
                    "id"	INTEGER UNIQUE,
                    "prediction_id"	TEXT UNIQUE,
                    "prediction_status"	INTEGER,
                    "prediction"	TEXT,
                    "image_path"	TEXT,
                    "model_info"	TEXT,
                    "model_id"	INTEGER,
                    "prediction_time"	INTEGER,
                    PRIMARY KEY("id" AUTOINCREMENT)
                    );"""
                cursor = connection.cursor()   
                cursor.execute(query)
        except:
            self.logger.error("", exc_info=True)


    def create_prediction(self, prediction_id, model_info, model_id):
        """creates prediction with 100 status code (100 is code for 'predicting')"""
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.debug("function: {0} param: {1}".format("create_prediction", prediction_id))
                query = "INSERT INTO predictions(prediction_id, prediction_status, prediction, image_path, model_info, model_id, prediction_time) VALUES(?,?,?,?,?,?,?);"
                cursor = connection.cursor()   
                cursor.execute(query, (prediction_id, 100, '', '', str(model_info), int(model_id), int(time.time())))
                connection.commit()
        except sqlite3.IntegrityError:
            self.logger.error("most likely you are trying to write douplicate of a unique field", exc_info=True)
        except:
            self.logger.error("", exc_info=True)
    

    # I don't use that but I wrote it anyways
    def delete_prediction(self, prediction_id):
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.debug("function: {0} param: {1}".format("delete_prediction", prediction_id))
                query = """DELETE FROM predictions WHERE prediction_id = ?;"""
                cursor = connection.cursor()   
                cursor.execute(query, (prediction_id,))
                connection.commit()
        except:
            self.logger.error("", exc_info=True)


    def update_successful_prediction(self, prediction_id, prediction, image_path):
        """updates successful prediction"""
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.debug("function: {0} prediction_id: {1}".format("update_successful_prediction", prediction_id))
                query = """ UPDATE predictions SET 
                prediction_status = ?, 
                prediction = ?, 
                image_path = ?, 
                prediction_time = ? 
                WHERE prediction_id = ?;"""
                cursor = connection.cursor()
                # convert types
                cursor.execute(query, (200, str(prediction), os.path.normpath(image_path), int(time.time()), prediction_id))
                connection.commit()
        except:
            self.logger.error("", exc_info=True)


    def update_failed_prediction(self, prediction_id, prediction_status):
        """updates failed prediction"""
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.debug("function: {0} param: {1}, {2}".format("update_failed_prediction", prediction_id, prediction_status))
                query = """ UPDATE predictions SET 
                prediction_status = ?,
                prediction_time = ? 
                WHERE prediction_id = ?;"""
                cursor = connection.cursor()   
                cursor.execute(query, (prediction_status, int(time.time()), prediction_id))
                connection.commit()
        except:
            self.logger.error("", exc_info=True)


    def is_prediction_exists(self, prediction_id):
        """returns true if prediction id exists on the database"""
        with sqlite3.connect(self.database_path) as connection:
            self.logger.debug("function: {0} param: {1}".format("is_prediction_exists", prediction_id))
            
            query = "SELECT * FROM predictions WHERE prediction_id = ?;"

            cursor = connection.cursor()   
            cursor.execute(query, (prediction_id, ))
            prediction = cursor.fetchall()

            if(prediction):
                return  prediction[0][2]
            else:
                return 0


    def get_prediction_json(self, prediction_id):
        """returns prediction information as json by using prediction id"""
        with sqlite3.connect(self.database_path) as connection:
            self.logger.debug("function: {0} param: {1}".format("get_prediction_json", prediction_id))
            
            query = "SELECT * FROM predictions WHERE prediction_id = ?;"

            cursor = connection.cursor()   
            cursor.execute(query, (prediction_id, ))
            prediction = cursor.fetchall()

            if(len(prediction) > 0):
                # database can save single quotes but json function needs double quoutes so we have this sad line
                model_info_json = json.loads(str( prediction[0][5]).replace("'","\""))

                if(prediction[0][2] == 200):
                    predictions_json = json.loads(str(prediction[0][3]).replace("'","\""))["predictions"]
                else:
                    predictions_json = "" 

                return {"prediction_id" : prediction[0][1], 
                        "prediction_status" : prediction[0][2], 
                        "predictions" : predictions_json,
                        "model_info" : model_info_json,
                        "prediction_time" : prediction[0][7]
                        }

            else:
                self.logger.warning("prediction_id does not exists {0}".format(prediction_id))
                return {"prediction_status" : 0}

