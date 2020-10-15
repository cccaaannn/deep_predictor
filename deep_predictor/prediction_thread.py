import threading
from database_handler import database_handler
from logger_creator import logger_creator


class prediction_thread(threading.Thread):
    def __init__(self, database_handler_cfg_path, temp_image_path, prediction_id, predictor, tf_version="dummy", tf_graph = None):
        super().__init__()
        self.db = database_handler(database_handler_cfg_path)
        self.logger = logger_creator().prediction_thread_logger()
        self.predictor = predictor
        self.prediction_id = prediction_id
        self.temp_image_path = temp_image_path
        self.tf_version = tf_version
        self.tf_graph = tf_graph

    def run(self):
        self.logger.info("prediction started on thread")

        if(self.tf_version == "1"):
            # tf_graph is needed fot model to run on a thread
            with self.tf_graph.as_default():
                status, model_info, prediction, image_path = self.predictor.predict_image(self.temp_image_path, save_image = "save")

        elif(self.tf_version == "2" or self.tf_version == "dummy"):
            status, model_info, prediction, image_path = self.predictor.predict_image(self.temp_image_path, save_image = "save")

        else:
            self.logger.error("tensorflow version not supported")

        self.logger.info("prediction status {0}".format(status))


        # save results to db
        if(status == 200):
            self.db.update_successful_prediction(
                self.prediction_id, 
                prediction, 
                model_info, 
                model_info["model_id"], 
                image_path
                )
        else:
            self.db.update_failed_prediction(
                self.prediction_id, 
                status, 
                model_info, 
                model_info["model_id"]
                )
