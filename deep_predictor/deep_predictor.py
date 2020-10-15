import os
import cv2
import numpy as np

import keras
# import darknet

from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator


class deep_predictor():
    def __init__(self, cfg_path="deep_predictor/cfg/deep_predictor.cfg", init=False):
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
            self.model_info = cfg["predictor_options"]["model_info"]

            # model info
            self.keras_image_size = (cfg["predictor_options"]["model_info"]["image_w"], cfg["predictor_options"]["model_info"]["image_h"])
            self.keras_grayscale = cfg["predictor_options"]["model_info"]["grayscale"]
            self.keras_topN = cfg["predictor_options"]["model_info"]["return_topN"]
            self.keras_confidence_threshold = cfg["predictor_options"]["model_info"]["confidence_threshold"]

            # paths
            self.keras_predictions_main_folder = cfg["predictor_options"]["paths"]["predictions_main_folder"] 
            self.keras_model_path = cfg["predictor_options"]["paths"]["model_path"]
            self.keras_names_path = cfg["predictor_options"]["paths"]["names_path"]
            self.keras_not_confiedent_name = cfg["predictor_options"]["paths"]["not_confiedent_folder_name"]
            


        elif(self.predictor_backend == "darknet"):
            # darknet options
            # self.darknet_files = cfg["predictor_options"]["darknet"]["darknet_files"]
            self.darknet_predictions_main_folder = cfg["predictor_options"]["darknet_predictions_main_folder"] 
            self.darknet_configPath = cfg["predictor_options"]["darknet_configPath"]
            self.darknet_weightPath = cfg["predictor_options"]["darknet_weightPath"]
            self.darknet_metaPath = cfg["predictor_options"]["darknet_metaPath"]

        else:
            self.logger.error("predictor backend is not supported")



    # backend initers
    def __init_darknet(self):
        self.logger.info("loading darknet network to ram")
        try:
            darknet.performDetect(configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, initOnly=True)
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
                "confidence" :  raw_prediction[0][pred]
            }

            predictions["predictions"].update({str(index+1) : temp_prediction})

        # if first guess is lover than threshold mark as not confident
        if(predictions["predictions"]["1"]["confidence"] < self.keras_confidence_threshold):
            predictions["predictions"].update({"is_confident" : 0})
        
        return predictions



    # unified predict function
    def predict_image(self, image_path, save_image = ""):
        if(self.predictor_backend == "keras"):
            return self.predict_image_keras(image_path, save_image = save_image)
        if(self.predictor_backend == "darknet"):
            return self.predict_image_darknet(image_path, save_image = save_image)



    def predict_image_keras(self, image_path, save_image = ""):
        if(self.is_inited):

            # load image
            image = image_operations.load_image_keras(image_path, self.keras_image_size, self.keras_grayscale)

            # check the image
            if(not isinstance(image, np.ndarray)):
                self.logger.error("image could not been loaded")
                return 350, self.model_info, None, None
            
            # prediction
            try:
                raw_prediction = self.keras_model.predict(image)
                prediction_json = self.__keras_raw_prediction_to_json(raw_prediction)
            except:
                self.logger.exception("model.predict raised exception")
                return 500, self.model_info, None, None

            self.logger.info("predictions: {0}".format(prediction_json))
            
            # save-remove
            predicted_image_path = None
            if(save_image == "remove"):
                os.remove(image_path)
            elif(save_image == "save"):

                if(prediction_json["predictions"]["is_confident"]):
                    image_class = prediction_json["predictions"]["1"]["class_name"]
                else:
                    image_class = self.keras_not_confiedent_name

                predicted_image_path = image_operations.move_image_by_class_name(image_path, self.keras_predictions_main_folder, image_class)
            else:
                pass

            # success
            return 200, self.model_info, prediction_json, predicted_image_path
        else:
            self.logger.warning("first init the keras backend")
            return 550, self.model_info, None, None



    # TODO fix this function it is not meets new requirements
    def predict_image_darknet(self, image_path, save_image = ""):
        if(self.is_inited):

            # prediction 
            try:
                result = darknet.performDetect(imagePath=image_path, configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, showImage= False, makeImageOnly=True)
            except:
                self.logger.exception("performDetect raised exception")
                return 500, None, None

            # ******************************
            # handle result for user
            detections_str = "" 

            if(result and result["detections"]):    
                for detection in result["detections"]:
                    detections_str += "{0} - {1:.2f}\n".format(detection[0], detection[1])

                # print(result)
                # TODO database
                # assign image to first predicted classes folder
                image_class = result["detections"][0][0]

            else:
                detections_str = "not-classified"
                image_class = "not-classified"

            # save image by class
            if(save_image == "save"):
                image_operations.move_image_by_class_name(image_path, self.darknet_predictions_main_folder, image_class)
            elif(save_image == "remove"):
                os.remove(image_path)
            else:
                pass


            return True, detections_str


        # ******************************

        else:
            self.logger.warning("first init the darknet backend")
            return 550, None, None




