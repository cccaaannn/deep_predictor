import sys
sys.path.insert(0, 'deep_predictor')

import unittest
import uuid
import time

from prediction_thread import prediction_thread
from database_handler import database_handler
from predictor import predictor


class test_prediction_thread(unittest.TestCase): 

    def setUp(self):
        self.predictor_cfg = "test/unittest/unittest_predictors/ms_coco.cfg"
        self.image_path = "test/test_images/images_from_darknet_repo/dog.jpg"
        self.predictor_backend = "tf_yolo"
        self.model_id = 4000

        self.db_path = "test/unittest/database/unittest_database.db"
        self.prediction_id = str(uuid.uuid4())

        self.result_wait_time = 5

    def test_make_prediction_on_thread(self):

        # create predictor
        p = predictor(self.predictor_cfg)

        # connect to db
        db = database_handler(self.db_path)

        # get predictor info
        model_info, model_id = p.get_model_info()
        self.assertEqual(model_id, self.model_id)
        self.assertEqual(model_info["predictor_backend"], self.predictor_backend)

        # create prediction
        db.create_prediction(self.prediction_id, model_info, model_id)

        # start prediction on thread
        pred_thread = prediction_thread(
            self.db_path, 
            self.image_path,
            self.prediction_id, 
            predictor=p
            )
        pred_thread.start()

        # wait for prediction
        time.sleep(self.result_wait_time)

        # get prediction result
        pred_json = db.get_prediction_json(self.prediction_id)
        self.assertEqual(pred_json["prediction_status"], 200) 
        self.assertNotEqual(pred_json["predictions"], "")



if __name__ == '__main__': 
    unittest.main()
