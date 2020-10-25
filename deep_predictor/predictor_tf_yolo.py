import os
import cv2
import numpy as np

# tf_yolo
from model_files.tf_yolo_files.detect import load_tf_yolo_model, perform_detect

# my classes
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator

class predictor_tf_yolo():
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
            self.tf_yolo_image_size = cfg["predictor_options"]["model_options"]["input_size"]
            self.iou_threshold = cfg["predictor_options"]["model_options"]["iou_threshold"]
            self.score_threshold = cfg["predictor_options"]["model_options"]["score_threshold"]

            # model_paths
            self.predictions_main_folder = cfg["predictor_options"]["model_paths"]["predictions_main_folder"] 
            self.not_confiedent_name = cfg["predictor_options"]["model_paths"]["not_confiedent_folder_name"] 
            self.tf_yolo_model_path = cfg["predictor_options"]["model_paths"]["model_path"]
            self.tf_yolo_names_path = cfg["predictor_options"]["model_paths"]["names_path"]

            return True
        except:
            self.logger.error("cfg file error", exc_info=True)
            return False

    def __init_backend(self):
        self.logger.info("loading tf_yolo network to ram")
        try:
            # load labels
            self.tf_yolo_names = file_folder_operations.read_class_names_tf_yolo(self.tf_yolo_names_path)

            # load model
            self.tf_yolo_model = load_tf_yolo_model(self.tf_yolo_model_path)

            self.is_inited = True
        except:
            self.logger.exception("could not load tf_yolo model")
            self.is_inited = False

    def __raw_prediction_to_json(self, raw_prediction):
        """converts tf_yolov4 raw prediction to json with required fields"""
        self.logger.info("converting raw_prediction to json raw_prediction: {0}".format(raw_prediction))
        predictions = {"predictions":[]}
        most_confident_score = 0
        most_confident_class = ""
        
        if(raw_prediction):
            for index, element in enumerate(raw_prediction):
                bounds = element[2]
                cx = bounds[0]
                cy = bounds[1]
                w = bounds[2] 
                h = bounds[3] 

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
        # load and check the image
        image, image_data = image_operations.load_image_tf_yolo(image_path, self.tf_yolo_image_size)
        if(not isinstance(image, np.ndarray)):
            self.logger.error("image could not been loaded")
            return 510, None, None

        # prediction 
        try:
            raw_prediction = perform_detect(self.tf_yolo_model, self.tf_yolo_names, image, image_data, self.iou_threshold, self.score_threshold)
        except:
            self.logger.error("perform_detect raised exception", exc_info=True)
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


