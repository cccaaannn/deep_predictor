import sqlite3
import json
import time
import os

from logger_creator import logger_creator
from helpers.file_folder_operations import file_folder_operations


class database_handler():
    def __init__(self, database_cfg_path = "deep_predictor/cfg/database.cfg"):
        self.logger = logger_creator().database_handler_logger()

        cfg = file_folder_operations.read_json_file(database_cfg_path)
        self.database_path = cfg["database_options"]["database_path"]
        
        self.check_connection()
        

    def check_connection(self):
        try:
            with sqlite3.connect(self.database_path) as _:
                self.logger.info("db connected")
        except:
            self.logger.critical("can not connect to database", exc_info=True)


    def create_prediction(self, prediction_id):
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.info("function: {0} param: {1}".format("create_prediction", prediction_id))
                query = "INSERT INTO predictions(prediction_id, prediction_status, prediction, image_path, model_id, prediction_time) VALUES(?,?,?,?,?,?);"
                cursor = connection.cursor()   
                cursor.execute(query, (prediction_id, 100, '', '', 0, 0))
                connection.commit()
        except sqlite3.IntegrityError:
            self.logger.error("", exc_info=True)
        except:
            self.logger.critical("", exc_info=True)
    
# TODO
    # def delete_prediction(self, prediction_id):
    #     try:
    #         with sqlite3.connect(self.database_path) as connection:
    #             self.logger.info("function: {0} param: {1}".format("create_prediction", prediction_id))
    #             query = "INSERT INTO predictions(prediction_id, prediction_status, prediction, image_path, model_id, prediction_time) VALUES(?,?,?,?,?,?);"
    #             cursor = connection.cursor()   
    #             cursor.execute(query, (prediction_id, 100, '', '', 0, 0))
    #             connection.commit()
    #     except:
    #         self.logger.critical("", exc_info=True)


    def update_prediction(self, prediction_id, prediction, model_id, image_path):
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.info("function: {0} param: {1}, {2}, {3}, {4}".format("update_prediction", prediction_id, prediction, model_id, image_path))
                query = """ UPDATE predictions SET 
                prediction_status = ?, 
                prediction = ?, 
                image_path = ?, 
                model_id = ?, 
                prediction_time = ? 
                WHERE prediction_id = ?;"""
                cursor = connection.cursor()
                # convert types
                cursor.execute(query, (200, str(prediction), os.path.normpath(image_path), model_id, int(time.time()), prediction_id))
                connection.commit()
        except:
            self.logger.critical("", exc_info=True)


    def update_prediction_status(self, prediction_id, prediction_status):
        try:
            with sqlite3.connect(self.database_path) as connection:
                self.logger.info("function: {0} param: {1}, {2}".format("update_prediction_status", prediction_id, prediction_status))
                query = """ UPDATE predictions SET 
                prediction_status = ? 
                WHERE prediction_id = ?;"""
                cursor = connection.cursor()   
                cursor.execute(query, (prediction_status, prediction_id))
                connection.commit()
        except:
            self.logger.critical("", exc_info=True)




    def is_prediction_exists(self, prediction_id):
        with sqlite3.connect(self.database_path) as connection:
            self.logger.info("function: {0} param: {1}".format("is_prediction_exists", prediction_id))
            
            query = "SELECT * FROM predictions WHERE prediction_id = ?;"

            cursor = connection.cursor()   
            cursor.execute(query, (prediction_id, ))
            prediction = cursor.fetchall()

            if(prediction):
                return  prediction[0][2]
            else:
                return 0


    def get_prediction_json(self, prediction_id):
        with sqlite3.connect(self.database_path) as connection:
            self.logger.info("function: {0} param: {1}".format("get_prediction", prediction_id))
            
            query = "SELECT * FROM predictions WHERE prediction_id = ?;"

            cursor = connection.cursor()   
            cursor.execute(query, (prediction_id, ))
            prediction = cursor.fetchall()

            if(len(prediction) > 0):
                if(prediction[0][2] == 200):

                    # database can save single quotes but json function needs double quoutes so we have this sad line
                    predictions_json = json.loads(str(prediction[0][3]).replace("'","\""))

                    return {"prediction_id" : prediction[0][1], 
                            "prediction_status" : prediction[0][2], 
                            "predictions" : predictions_json["predictions"],
                            "model_id" : prediction[0][5], 
                            "prediction_time" : prediction[0][6]
                            }
                else:
                    return  {"prediction_status" : prediction[0][2]}
            else:
                return {"prediction_status" : 0}


