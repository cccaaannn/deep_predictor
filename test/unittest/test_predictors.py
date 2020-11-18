import sys
sys.path.insert(0, 'deep_predictor')

import unittest
from predictor import predictor


class test_keras_predictor(unittest.TestCase): 

    def setUp(self):
        self.predictor_cfg = "test/unittest/unittest_predictors/vgg16_food10.cfg"
        self.image_path = "test/test_images/food/acibademkurabiyesi1.jpg"

    def test_make_prediction(self):
        p = predictor(self.predictor_cfg)
        status, predictions, path = p.predict_image(self.image_path)
        self.assertEqual(status, 200) 


class test_tf_yolo_predictor(unittest.TestCase): 

    def setUp(self):
        self.predictor_cfg = "test/unittest/unittest_predictors/ms_coco.cfg"
        self.image_path = "test/test_images/images_from_darknet_repo/dog.jpg"

    def test_make_prediction(self):
        p = predictor(self.predictor_cfg)
        status, predictions, path = p.predict_image(self.image_path)
        self.assertEqual(status, 200) 


class test_dummy_predictor(unittest.TestCase): 

    def setUp(self):
        self.predictor_cfg = "test/unittest/unittest_predictors/dummy_predictor.cfg"
        self.image_path = "test/test_images/food/acibademkurabiyesi1.jpg"

    def test_make_prediction(self):
        p = predictor(self.predictor_cfg)
        status, predictions, path = p.predict_image(self.image_path)
        self.assertEqual(status, 200) 



if __name__ == '__main__': 
    unittest.main() 
