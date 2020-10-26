import os
import cv2
import numpy as np

# keras-tf
import keras
import tensorflow as tf

# my classes
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator

class predictor_keras():
    def __init__(self, cfg_path):
        self.logger = logger_creator().deep_predictor_logger()
        self.is_inited = False
        is_cfg_ok =  self.__set_options(cfg_path)
        if(is_cfg_ok):
            self.__init_backend()

    # load cfg options
    def __set_options(self, cfg_path):
        try:
            cfg = file_folder_operations.read_json_file(cfg_path)
    
            # model_options
            self.predicted_image_action = cfg["predictor_options"]["model_options"]["predicted_image_action"]
            self.confidence_threshold = cfg["predictor_options"]["model_options"]["confidence_threshold"]
            self.keras_image_size = (cfg["predictor_options"]["model_options"]["image_w"], cfg["predictor_options"]["model_options"]["image_h"])
            self.keras_grayscale = cfg["predictor_options"]["model_options"]["grayscale"]
            self.keras_topN = cfg["predictor_options"]["model_options"]["return_topN"]

            # graph for tf 1 session
            self.tensorflow_version = cfg["predictor_options"]["model_options"]["tensorflow_version"]
            if(self.tensorflow_version == 1):
                self.tf_graph = tf.get_default_graph()

            # model_paths
            self.predictions_main_folder = cfg["predictor_options"]["model_paths"]["predictions_main_folder"] 
            self.not_confiedent_name = cfg["predictor_options"]["model_paths"]["not_confiedent_folder_name"] 
            self.keras_model_path = cfg["predictor_options"]["model_paths"]["model_path"]
            self.keras_names_path = cfg["predictor_options"]["model_paths"]["names_path"]

            return True
        except:
            self.logger.error("cfg file error", exc_info=True)
            return False

    def __init_backend(self):
        self.logger.info("loading keras network to ram")
        try:
            # load labels
            self.keras_names = file_folder_operations.read_from_file(self.keras_names_path).split()

            # load model
            self.keras_model = keras.models.load_model(self.keras_model_path)

            self.is_inited = True
        except:
            self.logger.exception("could not load keras model")
            self.is_inited = False

    def __raw_prediction_to_json(self, raw_prediction):
        """converts keras raw prediction to json with required fields"""
        self.logger.info("converting raw_prediction to json raw_prediction: {0}".format(raw_prediction))
        predictions = {"predictions":[]}

        topN_preds = raw_prediction.argsort()[0][-self.keras_topN:][::-1]
        
        for index, pred in enumerate(topN_preds):
            temp_prediction = {
                "class_index" : pred,
                "class_name" : str(self.keras_names[pred]),
                "confidence" :  float("{0:.5f}".format(raw_prediction[0][pred]))
            }
            predictions["predictions"].append(temp_prediction)

        # if first guess is lover than threshold mark as not confident and set image class to not-confident for saving
        if(predictions["predictions"][0]["confidence"] < self.confidence_threshold):
            image_class = self.not_confiedent_name
        else:
            image_class = predictions["predictions"][0]["class_name"]

        return predictions, image_class

    def predict_image(self, image_path):
        # load and check the image
        image = image_operations.load_image_keras(image_path, self.keras_image_size, self.keras_grayscale)
        if(not isinstance(image, np.ndarray)):
            self.logger.error("image could not been loaded")
            return 510, None, None

        # prediction
        try:
            # tf 1 uses sessions
            if(self.tensorflow_version == 1):
                with self.tf_graph.as_default():
                    raw_prediction = self.keras_model.predict(image)
            elif(self.tensorflow_version == 2):
                raw_prediction = self.keras_model.predict(image)
            else:
                self.logger.error("tensorflow version not supported (give 1 or 2)")
                return 560, None, None
        except:
            self.logger.error("model.predict raised exception", exc_info=True)
            return 500, None, None

        # convert prediction to json
        try:
            prediction_json, most_confident_class = self.__raw_prediction_to_json(raw_prediction)
            self.logger.info("predictions: {0}".format(prediction_json))
        except:
            self.logger.error("prediction can not converted to json", exc_info=True)
            return 520, None, None

        # perform image action
        try:
            self.logger.info("performing chosen action to image ({0})".format(self.predicted_image_action))
            predicted_image_path = image_operations.perform_image_action(image_path, self.predictions_main_folder, most_confident_class, self.predicted_image_action)
        except:
            self.logger.error("image action may not been performed", exc_info=True)
            return 530, None, None

        # success
        return 200, prediction_json, predicted_image_path


