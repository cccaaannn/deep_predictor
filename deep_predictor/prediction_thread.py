import threading
from database_handler import database_handler
from logger_creator import logger_creator

class prediction_thread(threading.Thread):
    def __init__(self, database_path, temp_image_path, prediction_id, predictor):
        super().__init__()
        self.db = database_handler(database_path)
        self.logger = logger_creator().prediction_thread_logger()
        self.predictor = predictor
        self.prediction_id = prediction_id
        self.temp_image_path = temp_image_path

    def run(self):
        self.logger.info("prediction started on thread")

        status, model_info, prediction, image_path = self.predictor.predict_image(self.temp_image_path, image_action = "save")

        # save results to db
        if(status == 200):
            self.logger.info("prediction is successful {0}".format(status))
            self.db.update_successful_prediction(self.prediction_id, prediction, model_info, model_info["model_id"], image_path)
        else:
            self.logger.warning("prediction failed with status {0}".format(status))
            self.db.update_failed_prediction(self.prediction_id, status, model_info, model_info["model_id"])
