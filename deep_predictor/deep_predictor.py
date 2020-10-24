import os
import cv2
import numpy as np

# predictors
from predictor_keras import predictor_keras
from predictor_tf_yolo import predictor_tf_yolo
# from predictor_darknet import predictor_darknet
from predictor_dummy import predictor_dummy

# my classes
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator

class deep_predictor():
    def __init__(self, cfg_path):
        self.logger = logger_creator().deep_predictor_logger()
        self.cfg_path = cfg_path
        is_cfg_ok =  self.__set_options(cfg_path)
        if(is_cfg_ok):
            self.__init_backend()

    # load cfg options
    def __set_options(self, cfg_path):
        try:
            cfg = file_folder_operations.read_json_file(cfg_path)
            
            # model info
            self.model_info = cfg["predictor_options"]["model_info"]            
            self.predictor_backend = cfg["predictor_options"]["model_info"]["predictor_backend"]
            self.method = cfg["predictor_options"]["model_info"]["method"]
            self.model_id = cfg["predictor_options"]["model_info"]["model_id"]

            return True
        except:
            self.logger.error("cfg file error", exc_info=True)
            return False

    def __init_backend(self):
        """inits predictor backend"""
        if(self.predictor_backend == "keras"):
            self.predictor = predictor_keras(self.cfg_path)
        elif(self.predictor_backend == "tf_yolo"):
            self.predictor = predictor_tf_yolo(self.cfg_path)
        elif(self.predictor_backend == "darknet"):
            self.predictor = predictor_darknet(self.cfg_path)
        elif(self.predictor_backend == "dummy"):
            self.predictor = predictor_dummy(self.cfg_path)            
        else:
            self.logger.error("cfg file error, predictor backend is not supported")

    def predict_image(self, image_path):
        self.logger.info("performing prediction on the image path: {0} model id: {1}".format(image_path, self.model_id))
        if(self.predictor and self.predictor.is_inited):
            # call predictors predict image function  
            status, prediction_json, predicted_image_path = self.predictor.predict_image(image_path)
            # add model info to return
            return status, self.model_info, prediction_json, predicted_image_path
        else:
            self.logger.error("backend for this predictor is not inited")
            return 550, self.model_info, None, None

