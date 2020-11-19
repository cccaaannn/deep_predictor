import sys
sys.path.insert(0, 'deep_predictor')

import uuid
import unittest
from database_handler import database_handler

class test_prediction_db_functions(unittest.TestCase):

    def setUp(self):
        self.prediction_id = str(uuid.uuid4())
        self.prediction = {'predictions': [{'class_index': 0, 'class_name': 'acibademKurabiyesi', 'confidence': 0.9982}, {'class_index': 7, 'class_name': 'kasarliPide', 'confidence': 0.00109}, {'class_index': 5, 'class_name': 'bulgurPilavi', 'confidence': 0.00071}, {'class_index': 3, 'class_name': 'asure', 'confidence': 0.0}, {'class_index': 9, 'class_name': 'kunefe', 'confidence': 0.0}]}
        self.image_path = "deep_predictor/images/predictions/keras/vgg16/acibademKurabiyesi/af360c56-c524-41f7-834a-d9b5150b797e.jpg"
        self.model_info = {'predictor_backend': 'keras', 'method': 'vgg16', 'model_id': 100}
        self.model_id = 100
        self.failed_prediction_status = 500
        self.prediction_time = 0.555

        self.db_path = "test/unittest/database/unittest_database.db"

    def test_successful_prediction(self):
        db = database_handler(self.db_path)
        self.assertIsNotNone(db)
        db.create_table_if_not_exists()

        status = db.is_prediction_exists(self.prediction_id)
        self.assertFalse(status)

        db.create_prediction(self.prediction_id, self.model_info, self.model_id)

        status = db.is_prediction_exists(self.prediction_id)
        self.assertTrue(status)

        db.update_successful_prediction(self.prediction_id, self.prediction, self.image_path, self.prediction_time)

        pred_json = db.get_prediction_json(self.prediction_id)
        self.assertEqual(pred_json["prediction_status"], 200) 
        self.assertNotEqual(pred_json["predictions"], "")
        self.assertEqual(pred_json["prediction_time"], 0.555)

    def test_failed_prediction(self):
        db = database_handler(self.db_path)
        self.assertIsNotNone(db)
        db.create_table_if_not_exists()

        status = db.is_prediction_exists(self.prediction_id)
        self.assertFalse(status)

        db.create_prediction(self.prediction_id, self.model_info, self.model_id)

        status = db.is_prediction_exists(self.prediction_id)
        self.assertTrue(status)

        db.update_failed_prediction(self.prediction_id, self.failed_prediction_status, self.prediction_time)

        pred_json = db.get_prediction_json(self.prediction_id)
        self.assertEqual(pred_json["prediction_status"], 500) 
        self.assertEqual(pred_json["predictions"], "")
        self.assertEqual(pred_json["prediction_time"], 0.555)

class test_other_db_functions(unittest.TestCase):

    def setUp(self):
        self.prediction_id = str(uuid.uuid4())
        self.model_info = {'predictor_backend': 'keras', 'method': 'vgg16', 'model_id': 100}
        self.model_id = 100
        self.db_path = "test/unittest/database/unittest_database.db"


    def test_delete_prediction(self):
        db = database_handler(self.db_path)
        self.assertIsNotNone(db)
        db.create_table_if_not_exists()

        status = db.is_prediction_exists(self.prediction_id)
        self.assertFalse(status)

        db.create_prediction(self.prediction_id, self.model_info, self.model_id)

        status = db.is_prediction_exists(self.prediction_id)
        self.assertTrue(status)

        db.delete_prediction(self.prediction_id)

        status = db.is_prediction_exists(self.prediction_id)
        self.assertFalse(status)



if __name__ == '__main__': 
    unittest.main()
