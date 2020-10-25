import os
import cv2
import numpy as np

# darknet
# from model_files.darknet_files.darknet_modified import performDetect
from model_files.darknet_files.darknet_images_modified import image_detection
from model_files.darknet_files.darknet import load_network, free_network_ptr

# my classes
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator

class predictor_darknet():
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
            # model_paths
            self.predictions_main_folder = cfg["predictor_options"]["model_paths"]["predictions_main_folder"] 
            self.not_confiedent_name = cfg["predictor_options"]["model_paths"]["not_confiedent_folder_name"] 
            self.darknet_configPath = cfg["predictor_options"]["model_paths"]["darknet_configPath"]
            self.darknet_weightPath = cfg["predictor_options"]["model_paths"]["darknet_weightPath"]
            self.darknet_metaPath = cfg["predictor_options"]["model_paths"]["darknet_metaPath"]

            return True
        except:
            self.logger.error("cfg file error", exc_info=True)
            return False

    # functions for darknet backend (causes memory leak because the c lib is most likely not thread safe)
    def __init_backend(self):
        self.logger.info("loading darknet network to ram")
        try:
            # performDetect(configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, initOnly=True)
            self.darknet_network, self.darknet_class_names, self.darknet_class_colors = load_network(self.darknet_configPath,self.darknet_metaPath,self.darknet_weightPath,batch_size=1)
            self.is_inited = True
        except:
            self.logger.exception("could not load darknet model")
            self.is_inited = False

    def __raw_prediction_to_json(self, raw_prediction, image_width, image_height):
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
                        "confidence" : float("{0:.5f}".format(float(element[1]))),
                        "bbox" : {
                            "cx" : float("{0:.5f}".format(cx)),
                            "cy" : float("{0:.5f}".format(cy)),
                            "w" : float("{0:.5f}".format(w)),
                            "h" : float("{0:.5f}".format(h))                     
                        } 
                    }
                
                predictions["predictions"].append(temp_dict)

                if(float(element[1]) > most_confident_score):
                    most_confident_score = float(element[1])
                    most_confident_class = element[0]

            return predictions, most_confident_class

        else:
            # if nothing detected
            return predictions, self.not_confiedent_name 

    def predict_image(self, image_path):
        # prediction 
        try:
            # raw_prediction, image_width, image_height = performDetect(imagePath=image_path, thresh=self.confidence_threshold, configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, showImage= False)
            self.darknet_network, self.darknet_class_names, self.darknet_class_colors = load_network(self.darknet_configPath, self.darknet_metaPath, self.darknet_weightPath, batch_size=1)
            raw_prediction, image_width, image_height = image_detection(image_path, self.darknet_network, self.darknet_class_names, self.darknet_class_colors, self.confidence_threshold)
            free_network_ptr(self.darknet_network)
        except:
            self.logger.error("performDetect raised exception", exc_info=True)
            return 500, None, None

        # convert prediction to json
        try:
            prediction_json, most_confident_class = self.__raw_prediction_to_json(raw_prediction, image_width, image_height)
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


