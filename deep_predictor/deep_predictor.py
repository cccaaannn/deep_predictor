import os
import cv2
import numpy as np

# import backends
import keras
import tensorflow as tf
# from model_files.darknet_files.darknet_modified import performDetect

# my classes
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator


class deep_predictor():
    def __init__(self, cfg_path, init=False):
        self.logger = logger_creator().deep_predictor_logger()

        self.__set_options(cfg_path)
        
        self.is_inited = False
        if(init):
            self.init_predictor()


    # class options
    def __set_options(self, cfg_path):
        try:
            cfg = file_folder_operations.read_json_file(cfg_path)
            
            self.predictor_backend = cfg["predictor_options"]["model_info"]["predictor_backend"]

            # this info only needed for sending to frontend
            _ = cfg["predictor_options"]["model_info"]["model_id"]

            if(self.predictor_backend == "keras"):
                # model info
                self.model_info = cfg["predictor_options"]["model_info"]
                self.method = cfg["predictor_options"]["model_info"]["method"]
                self.confidence_threshold = cfg["predictor_options"]["model_info"]["confidence_threshold"]

                self.keras_image_size = (cfg["predictor_options"]["model_info"]["image_w"], cfg["predictor_options"]["model_info"]["image_h"])
                self.keras_grayscale = cfg["predictor_options"]["model_info"]["grayscale"]
                self.keras_topN = cfg["predictor_options"]["model_info"]["return_topN"]

                # graph for tf 1 session
                self.tensorflow_version = cfg["predictor_options"]["model_info"]["tensorflow_version"]
                if(self.tensorflow_version == 1):
                    self.tf_graph = tf.get_default_graph()
                
                # paths
                # common paths
                self.predictions_main_folder = cfg["predictor_options"]["paths"]["predictions_main_folder"] 
                self.not_confiedent_name = cfg["predictor_options"]["paths"]["not_confiedent_folder_name"] 

                # backend specific paths
                self.keras_model_path = cfg["predictor_options"]["paths"]["model_path"]
                self.keras_names_path = cfg["predictor_options"]["paths"]["names_path"]

            elif(self.predictor_backend == "darknet"):
                # model info
                self.model_info = cfg["predictor_options"]["model_info"]
                self.method = cfg["predictor_options"]["model_info"]["method"]
                self.confidence_threshold = cfg["predictor_options"]["model_info"]["confidence_threshold"]
                
                # paths
                # common paths
                self.predictions_main_folder = cfg["predictor_options"]["paths"]["predictions_main_folder"] 
                self.not_confiedent_name = cfg["predictor_options"]["paths"]["not_confiedent_folder_name"]
                
                # backend specific paths
                self.darknet_configPath = cfg["predictor_options"]["paths"]["darknet_configPath"]
                self.darknet_weightPath = cfg["predictor_options"]["paths"]["darknet_weightPath"]
                self.darknet_metaPath = cfg["predictor_options"]["paths"]["darknet_metaPath"]

            else:
                self.logger.error("cfg file error, predictor backend is not supported")

        except:
            self.logger.error("cfg file error", exc_info=True)


    # backend initers
    def __init_darknet(self):
        self.logger.info("loading darknet network to ram")
        try:
            performDetect(configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, initOnly=True)
            return True
        except:
            self.logger.exception("could not load darknet model")
            return False

    def __init_keras(self):
        self.logger.info("loading keras network to ram")
        try:
            # load labels
            self.keras_names = file_folder_operations.read_from_file(self.keras_names_path).split()

            # load model
            self.keras_model = keras.models.load_model(self.keras_model_path)

            return True
        except:
            self.logger.exception("could not load keras model")
            return False

    def init_predictor(self):
        """initiates a backend for prediction"""
        if(self.predictor_backend == "darknet"):
            if(self.__init_darknet()):
                self.is_inited = True
        if(self.predictor_backend == "keras"):
            if(self.__init_keras()):
                self.is_inited = True


    # prediction processing
    def __keras_raw_prediction_to_json(self, raw_prediction):
        """converts keras raw prediction to json with required fields"""
        self.logger.info("converting raw_prediction to json raw_prediction: {0}".format(raw_prediction))
        predictions = {"predictions" : {"is_confident" : 1}}

        topN_preds = raw_prediction.argsort()[0][-self.keras_topN:][::-1]
        
        for index, pred in enumerate(topN_preds):
            temp_prediction = {
                "class_index" : pred,
                "class_name" : str(self.keras_names[pred]),
                "confidence" :  float("{0:.5f}".format(raw_prediction[0][pred]))
            }

            predictions["predictions"].update({str(index+1) : temp_prediction})

        # if first guess is lover than threshold mark as not confident and set image class to not-confident for saving
        if(predictions["predictions"]["1"]["confidence"] < self.confidence_threshold):
            predictions["predictions"].update({"is_confident" : 0})
            image_class = self.not_confiedent_name
        else:
            image_class = predictions["predictions"]["1"]["class_name"]

        return predictions, image_class

    def __darknet_raw_prediction_to_json(self, raw_prediction, image_width, image_height):
        """converts darknet raw prediction to json with required fields"""
        self.logger.info("converting raw_prediction to json raw_prediction: {0}".format(raw_prediction))
        predictions = {"predictions":[]}
        most_confident_score = 0
        most_confident_class = ""
        
        if(raw_prediction):
            for index, element in enumerate(raw_prediction):

                # convert coordinates (from darknet.py)
                # x2 = x1 - w/2 + w
                # x1 = int(bounds[0] - bounds[2] / 2)
                # y1 = int(bounds[1] - bounds[3] / 2)
                # x2 = x1 + int(bounds[2])
                # y2 = y1 + int(bounds[3])

                # ratio bboxes
                bounds = element[2]
                cx = bounds[0] / image_width
                cy = bounds[1] / image_height
                w = bounds[2] / image_width
                h = bounds[3] / image_height

                temp_dict = {
                        "class_name" : element[0],
                        "confidence" : float("{0:.5f}".format(element[1])),
                        "bbox" : {
                            "cx" : float("{0:.5f}".format(cx)),
                            "cy" : float("{0:.5f}".format(cy)),
                            "w" : float("{0:.5f}".format(w)),
                            "h" : float("{0:.5f}".format(h))                     
                        } 
                    }
                
                predictions["predictions"].append(temp_dict)

                if(element[1] > most_confident_score):
                    most_confident_score = element[1]
                    most_confident_class = element[0]

            return True, predictions, most_confident_class
        
        else:
            return False, predictions, most_confident_class


    # prediction functions
    def __predict_image_keras(self, image_path, image_action = ""):
        self.logger.info("performing prediction on the image path: {0} image action is: {1}".format(image_path, image_action))
        
        if(self.is_inited):
            # load image
            image = image_operations.load_image_keras(image_path, self.keras_image_size, self.keras_grayscale)

            # check the image
            if(not isinstance(image, np.ndarray)):
                self.logger.error("image could not been loaded")
                return 510, self.model_info, None, None
            
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
                    return 560, self.model_info, None, None
            except:
                self.logger.error("model.predict raised exception", exc_info=True)
                return 500, self.model_info, None, None

            # convert prediction
            try:
                prediction_json, image_class = self.__keras_raw_prediction_to_json(raw_prediction)
                self.logger.info("predictions: {0}".format(prediction_json))
            except:
                self.logger.error("prediction can not converted to json", exc_info=True)
                return 520, self.model_info, None, None
            
            # perform image action
            try:
                self.logger.info("performing chosen action to image ({0})".format(image_action))
                predicted_image_path = None
                if(image_action == "remove"):
                    os.remove(image_path)
                elif(image_action == "save"):
                    predicted_image_path = image_operations.move_image_by_class_name(image_path, self.predictions_main_folder, image_class)
                else:
                    pass
            except:
                self.logger.error("image action may not been performed", exc_info=True)
                return 530, self.model_info, None, None

            # success
            return 200, self.model_info, prediction_json, predicted_image_path
        else:
            self.logger.error("backend for this predictor is not inited")
            return 550, self.model_info, None, None

    def __predict_image_darknet(self, image_path, image_action = ""):
        self.logger.info("performing prediction on the image path: {0} image action is: {1}".format(image_path, image_action))
        
        if(self.is_inited):
            
            # prediction 
            try:
                raw_prediction, image_width, image_height = performDetect(imagePath=image_path, thresh=self.confidence_threshold, configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, showImage= False)
            except:
                self.logger.error("performDetect raised exception", exc_info=True)
                return 500, self.model_info, None, None
 
            # convert prediction
            try:
                status, prediction_json, most_confident_class = self.__darknet_raw_prediction_to_json(raw_prediction, image_width, image_height)
                
                # if nothing detected
                if(not status):
                    most_confident_class = self.not_confiedent_name 

                self.logger.info("predictions: {0}".format(prediction_json))
            except:
                self.logger.error("prediction can not converted to json", exc_info=True)
                return 520, self.model_info, None, None

            # perform image action
            try:
                self.logger.info("performing chosen action to image ({0})".format(image_action))
                predicted_image_path = None
                if(image_action == "remove"):
                    os.remove(image_path)
                elif(image_action == "save"):
                    predicted_image_path = image_operations.move_image_by_class_name(image_path, self.predictions_main_folder, most_confident_class)
                else:
                    pass
            except:
                self.logger.error("image action may not been performed", exc_info=True)
                return 530, self.model_info, None, None

            # success
            return 200, self.model_info, prediction_json, predicted_image_path
        else:
            self.logger.error("backend for this predictor is not inited")
            return 550, self.model_info, None, None


    # unified predict function
    def predict_image(self, image_path, image_action = ""):
        if(self.predictor_backend == "keras"):
            return self.__predict_image_keras(image_path, image_action = image_action)
        elif(self.predictor_backend == "darknet"):
            return self.__predict_image_darknet(image_path, image_action = image_action)
        else:
            self.logger.error("predictor backend is not supported check your cfg file")
            return 570, self.model_info, None, None