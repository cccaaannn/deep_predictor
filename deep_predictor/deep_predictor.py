import os
import cv2
import numpy as np

# keras-tf
import keras
import tensorflow as tf

# tf_yolo
from model_files.tf_yolo_files.detect import load_tf_yolo_model, perform_detect

# darknet
# from model_files.darknet_files.darknet_modified import performDetect
# from model_files.darknet_files.darknet_images_modified import image_detection
# from model_files.darknet_files.darknet import_modified load_network, free_network_ptr

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

    # load cfg options
    def __set_options(self, cfg_path):
        try:
            cfg = file_folder_operations.read_json_file(cfg_path)
            
            # model info
            self.model_info = cfg["predictor_options"]["model_info"]            
            self.predictor_backend = cfg["predictor_options"]["model_info"]["predictor_backend"]
            self.method = cfg["predictor_options"]["model_info"]["method"]
            _ = cfg["predictor_options"]["model_info"]["model_id"]
            
            # common model_options
            self.predicted_image_action = cfg["predictor_options"]["model_options"]["predicted_image_action"]

            # common model_paths
            self.predictions_main_folder = cfg["predictor_options"]["model_paths"]["predictions_main_folder"] 
            self.not_confiedent_name = cfg["predictor_options"]["model_paths"]["not_confiedent_folder_name"] 
 
            if(self.predictor_backend == "keras"):
                # model_options
                self.confidence_threshold = cfg["predictor_options"]["model_options"]["confidence_threshold"]
                self.keras_image_size = (cfg["predictor_options"]["model_options"]["image_w"], cfg["predictor_options"]["model_options"]["image_h"])
                self.keras_grayscale = cfg["predictor_options"]["model_options"]["grayscale"]
                self.keras_topN = cfg["predictor_options"]["model_options"]["return_topN"]

                # graph for tf 1 session
                self.tensorflow_version = cfg["predictor_options"]["model_options"]["tensorflow_version"]
                if(self.tensorflow_version == 1):
                    self.tf_graph = tf.get_default_graph()

                # backend specific model_paths
                self.keras_model_path = cfg["predictor_options"]["model_paths"]["model_path"]
                self.keras_names_path = cfg["predictor_options"]["model_paths"]["names_path"]
            
            elif(self.predictor_backend == "tf_yolo"):
                # model_options
                self.tf_yolo_image_size = cfg["predictor_options"]["model_options"]["input_size"]
                self.iou_threshold = cfg["predictor_options"]["model_options"]["iou_threshold"]
                self.score_threshold = cfg["predictor_options"]["model_options"]["score_threshold"]
                # backend specific model_paths
                self.tf_yolo_model_path = cfg["predictor_options"]["model_paths"]["model_path"]
                self.tf_yolo_names_path = cfg["predictor_options"]["model_paths"]["names_path"]

            elif(self.predictor_backend == "darknet"):
                # model_options               
                self.confidence_threshold = cfg["predictor_options"]["model_options"]["confidence_threshold"]
                # backend specific model_paths
                self.darknet_configPath = cfg["predictor_options"]["model_paths"]["darknet_configPath"]
                self.darknet_weightPath = cfg["predictor_options"]["model_paths"]["darknet_weightPath"]
                self.darknet_metaPath = cfg["predictor_options"]["model_paths"]["darknet_metaPath"]

            else:
                self.logger.error("cfg file error, predictor backend is not supported")

        except:
            self.logger.error("cfg file error", exc_info=True)



    # functions for keras backend
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
                predicted_image_path = ""
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



    # functions for tf_yolo backend
    def __init_tf_yolo(self):
        self.logger.info("loading tf_yolo network to ram")
        try:
            # load labels
            self.tf_yolo_names = file_folder_operations.read_class_names_tf_yolo(self.tf_yolo_names_path)

            # load model
            self.tf_yolo_model = load_tf_yolo_model(self.tf_yolo_model_path)

            return True
        except:
            self.logger.exception("could not load tf_yolo model")
            return False

    def __tf_yolo_raw_prediction_to_json(self, raw_prediction):
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

            return True, predictions, most_confident_class
        
        else:
            return False, predictions, most_confident_class

    def __predict_image_tf_yolo(self, image_path, image_action = ""):
        self.logger.info("performing prediction on the image path: {0} image action is: {1}".format(image_path, image_action))
        if(self.is_inited):
            # load image
            image, image_data = image_operations.load_image_tf_yolo(image_path, self.tf_yolo_image_size)

            # check the image
            if(not isinstance(image, np.ndarray)):
                self.logger.error("image could not been loaded")
                return 510, self.model_info, None, None

            # prediction 
            try:
                raw_prediction = perform_detect(self.tf_yolo_model, self.tf_yolo_names, image, image_data, self.iou_threshold, self.score_threshold)
            except:
                self.logger.error("perform_detect raised exception", exc_info=True)
                return 500, self.model_info, None, None

            # convert prediction
            try:
                status, prediction_json, most_confident_class = self.__tf_yolo_raw_prediction_to_json(raw_prediction)

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
                predicted_image_path = ""
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



    # functions for darknet backend (causes memory leak because the c lib is most likely not thread safe)
    def __init_darknet(self):
        self.logger.info("loading darknet network to ram")
        try:
            # performDetect(configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, initOnly=True)
            self.darknet_network, self.darknet_class_names, self.darknet_class_colors = load_network(self.darknet_configPath,self.darknet_metaPath,self.darknet_weightPath,batch_size=1)
            return True
        except:
            self.logger.exception("could not load darknet model")
            return False

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

            return True, predictions, most_confident_class
        
        else:
            return False, predictions, most_confident_class

    def __predict_image_darknet(self, image_path, image_action = ""):
        self.logger.info("performing prediction on the image path: {0} image action is: {1}".format(image_path, image_action))
        
        if(self.is_inited):
            
            # prediction 
            try:
               # raw_prediction, image_width, image_height = performDetect(imagePath=image_path, thresh=self.confidence_threshold, configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, showImage= False)

                self.darknet_network, self.darknet_class_names, self.darknet_class_colors = load_network(self.darknet_configPath, self.darknet_metaPath, self.darknet_weightPath, batch_size=1)
                raw_prediction, image_width, image_height = image_detection(image_path, self.darknet_network, self.darknet_class_names, self.darknet_class_colors, self.confidence_threshold)
                free_network_ptr(self.darknet_network)

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
                predicted_image_path = ""
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



    # unified functions
    def init_predictor(self):
        """initiates a backend for prediction"""
        if(self.predictor_backend == "keras"):
            if(self.__init_keras()):
                self.is_inited = True
        elif(self.predictor_backend == "tf_yolo"):
            if(self.__init_tf_yolo()):
                self.is_inited = True
        elif(self.predictor_backend == "darknet"):
            if(self.__init_darknet()):
                self.is_inited = True

    def predict_image(self, image_path):
        if(self.predictor_backend == "keras"):
            return self.__predict_image_keras(image_path, image_action = self.predicted_image_action)
        elif(self.predictor_backend == "tf_yolo"):
            return self.__predict_image_tf_yolo(image_path, image_action = self.predicted_image_action)      
        elif(self.predictor_backend == "darknet"):
            return self.__predict_image_darknet(image_path, image_action = self.predicted_image_action)
        else:
            self.logger.error("predictor backend is not supported check your cfg file")
            return 570, self.model_info, None, None

