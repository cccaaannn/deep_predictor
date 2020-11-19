import threading
from database_handler import database_handler
from logger_creator import logger_creator
import time

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
        
        # time the prediction
        start = time.time()

        status, prediction, image_path = self.predictor.predict_image(self.temp_image_path)

        prediction_time = float("{0:.3f}".format(float(time.time() - start)))

        # save results to db
        if(status == 200):
            self.logger.info("prediction is successful {0}".format(status))
            self.db.update_successful_prediction(self.prediction_id, prediction, image_path, prediction_time)
        else:
            self.logger.warning("prediction failed with status {0}".format(status))
            self.db.update_failed_prediction(self.prediction_id, status, prediction_time)
