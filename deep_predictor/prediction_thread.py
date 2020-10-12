import threading
from database_handler import database_handler
from logger_creator import logger_creator


class prediction_thread(threading.Thread):
    def __init__(self, database_handler_cfg_path, temp_image_path, prediction_id, model_id, predictor, tf_version="2", tf_graph = None, is_dummy=False):
        super().__init__()
        self.db = database_handler(database_handler_cfg_path)
        self.logger = logger_creator().prediction_thread_logger()
        self.predictor = predictor
        self.prediction_id = prediction_id
        self.temp_image_path = temp_image_path
        self.model_id = model_id
        self.tf_version = tf_version
        self.tf_graph = tf_graph
        self.is_dummy = is_dummy

    def run(self):
        self.logger.info("prediction started on thread")
        if(not self.is_dummy):
            if(self.tf_version == "1"):
                # tf_graph is needed fot model to run on a thread
                with self.tf_graph.as_default():
                    if(self.model_id == 1):
                        status, prediction, image_path = self.predictor.predict_image_keras(self.temp_image_path, save_image = "save")
                    elif(self.model_id == 2):
                        status, prediction, image_path = self.predictor.predict_image_darknet(self.temp_image_path, save_image = "save")
                    
                    self.logger.info("prediction status {0}".format(status))

                    if(status == 200):
                        self.db.update_prediction(self.prediction_id, prediction, self.model_id, image_path)
                    else:
                        self.db.update_prediction_status(self.prediction_id, status)

            elif(self.tf_version == "2"):
                if(self.model_id == 1):
                    status, prediction, image_path = self.predictor.predict_image_keras(self.temp_image_path, save_image = "save")
                elif(self.model_id == 2):
                    status, prediction, image_path = self.predictor.predict_image_darknet(self.temp_image_path, save_image = "save")
                
                self.logger.info("prediction status {0}".format(status))

                if(status == 200):
                    self.db.update_prediction(self.prediction_id, prediction, self.model_id, image_path)
                else:
                    self.db.update_prediction_status(self.prediction_id, status)



        if(self.is_dummy):
            if(self.model_id == 1):
                status, prediction, image_path = self.predictor.predict_image_keras(self.temp_image_path, save_image = "save")
            elif(self.model_id == 2):
                status, prediction, image_path = self.predictor.predict_image_darknet(self.temp_image_path, save_image = "save")
            
            self.logger.info("prediction status {0}".format(status))

            if(status == 200):
                self.db.update_prediction(self.prediction_id, prediction, self.model_id, image_path)
            else:
                self.db.update_prediction_status(self.prediction_id, status)