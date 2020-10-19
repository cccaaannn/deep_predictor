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
        
        if(init):
            self.is_inited = True
            self.init_predictor()
        else:
            self.is_inited = False



    # class options
    def __set_options(self, cfg_path):
        cfg = file_folder_operations.read_json_file(cfg_path)
        
        self.predictor_backend = cfg["predictor_options"]["model_info"]["predictor_backend"]

        _ = cfg["predictor_options"]["model_info"]["model_id"]
        _ = cfg["predictor_options"]["model_info"]["method"]


        if(self.predictor_backend == "keras"):
            # keras options

            # model info
            self.model_info = cfg["predictor_options"]["model_info"]
            self.keras_image_size = (cfg["predictor_options"]["model_info"]["image_w"], cfg["predictor_options"]["model_info"]["image_h"])
            self.keras_grayscale = cfg["predictor_options"]["model_info"]["grayscale"]
            self.keras_topN = cfg["predictor_options"]["model_info"]["return_topN"]
            self.confidence_threshold = cfg["predictor_options"]["model_info"]["confidence_threshold"]
            
            self.tensorflow_version = cfg["predictor_options"]["model_info"]["tensorflow_version"]
            # graph for tf 1 session
            if(self.tensorflow_version == 1):
                self.tf_graph = tf.get_default_graph()
            
            # paths
            self.keras_predictions_main_folder = cfg["predictor_options"]["paths"]["predictions_main_folder"] 
            self.keras_model_path = cfg["predictor_options"]["paths"]["model_path"]
            self.keras_names_path = cfg["predictor_options"]["paths"]["names_path"]
            self.not_confiedent_name = cfg["predictor_options"]["paths"]["not_confiedent_folder_name"]
            


        elif(self.predictor_backend == "darknet"):
            # darknet options

            # model info
            self.model_info = cfg["predictor_options"]["model_info"]
            self.confidence_threshold = cfg["predictor_options"]["model_info"]["confidence_threshold"]
            
            # paths
            self.darknet_predictions_main_folder = cfg["predictor_options"]["paths"]["darknet_predictions_main_folder"] 
            self.darknet_configPath = cfg["predictor_options"]["paths"]["darknet_configPath"]
            self.darknet_weightPath = cfg["predictor_options"]["paths"]["darknet_weightPath"]
            self.darknet_metaPath = cfg["predictor_options"]["paths"]["darknet_metaPath"]
            self.not_confiedent_name = cfg["predictor_options"]["paths"]["not_confiedent_folder_name"]


        else:
            self.logger.error("predictor backend is not supported")



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
        predictions = {"predictions" : {"is_confident" : 1}}

        topN_preds = raw_prediction.argsort()[0][-self.keras_topN:][::-1]
        
        for index, pred in enumerate(topN_preds):
            temp_prediction = {
                "class_index" : pred,
                "class_name" : str(self.keras_names[pred]),
                "confidence" :  float("{0:.5f}".format(raw_prediction[0][pred]))
            }

            predictions["predictions"].update({str(index+1) : temp_prediction})

        # if first guess is lover than threshold mark as not confident
        if(predictions["predictions"]["1"]["confidence"] < self.confidence_threshold):
            predictions["predictions"].update({"is_confident" : 0})
        
        return predictions

    def __darknet_raw_prediction_to_json(self, raw_prediction, image_width, image_height):
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




    # unified predict function
    def predict_image(self, image_path, image_action = ""):
        if(self.predictor_backend == "keras"):
            return self.predict_image_keras(image_path, image_action = image_action)
        if(self.predictor_backend == "darknet"):
            return self.predict_image_darknet(image_path, image_action = image_action)


    def predict_image_keras(self, image_path, image_action = ""):
        if(self.is_inited):

            # load image
            image = image_operations.load_image_keras(image_path, self.keras_image_size, self.keras_grayscale)

            # check the image
            if(not isinstance(image, np.ndarray)):
                self.logger.error("image could not been loaded")
                return 350, self.model_info, None, None
            
            # prediction
            try:
                # tf 1 uses sessions
                if(self.tensorflow_version == 1):
                    with self.tf_graph.as_default():
                        raw_prediction = self.keras_model.predict(image)
                elif(self.tensorflow_version == 2):
                    raw_prediction = self.keras_model.predict(image)
                else:
                    raise ValueError("tensorflow version not supported (give 1 or 2)")

                prediction_json = self.__keras_raw_prediction_to_json(raw_prediction)
            except:
                self.logger.exception("model.predict raised exception")
                return 500, self.model_info, None, None

            self.logger.info("predictions: {0}".format(prediction_json))
            
            # save-remove
            predicted_image_path = None
            if(image_action == "remove"):
                os.remove(image_path)
            elif(image_action == "save"):

                if(prediction_json["predictions"]["is_confident"]):
                    image_class = prediction_json["predictions"]["1"]["class_name"]
                else:
                    image_class = self.not_confiedent_name

                predicted_image_path = image_operations.move_image_by_class_name(image_path, self.keras_predictions_main_folder, image_class)
            else:
                pass

            # success
            return 200, self.model_info, prediction_json, predicted_image_path
        else:
            self.logger.warning("first init the keras backend")
            return 550, self.model_info, None, None



    def predict_image_darknet(self, image_path, image_action = ""):
        if(self.is_inited):

            # prediction 
            try:
                raw_prediction, image_width, image_height = performDetect(imagePath=image_path, thresh=self.confidence_threshold, configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, showImage= False)
            except:
                self.logger.exception("performDetect raised exception")
                return 500, self.model_info, None, None

            # convert prediction
            status, predictions, most_confident_class = self.__darknet_raw_prediction_to_json(raw_prediction, image_width, image_height)

            # if nothing detected
            if(not status):
                most_confident_class = self.not_confiedent_name           


            # save-remove
            predicted_image_path = None
            if(image_action == "remove"):
                os.remove(image_path)
            elif(image_action == "save"):
                predicted_image_path = image_operations.move_image_by_class_name(image_path, self.darknet_predictions_main_folder, most_confident_class)
            else:
                pass

            # success
            return 200, self.model_info, predictions, predicted_image_path
        else:
            self.logger.warning("first init the darknet backend")
            return 550, self.model_info, None, None




