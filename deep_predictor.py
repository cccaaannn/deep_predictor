import logging
import shutil
import os
import cv2
import numpy as np
import json

import keras
import darknet



class deep_predictor():
    def __init__(self, cfg_path="cfg/options.cfg"):
        
        self.__set_options(cfg_path)
        
        self.logger = self.__set_logger()

        self.is_darknet_inited = False
        self.is_keras_inited = False
        

    # class options
    def __set_options(self, cfg_path):
        try:
            cfg = self.__read_json_file(cfg_path)
            
            # general options
            self.predictions_main_folder = cfg["general"]["predictions_main_folder"] 
            self.logger_name = cfg["general"]["logger_name"]
            self.log_file = cfg["general"]["log_file"]
            
            # darknet options
            self.darknet_files = cfg["darknet"]["darknet_files"]
            self.predictions_temp_path = cfg["darknet"]["darknet_predictions_temp_path"]
            self.darknet_predictions_main_folder = cfg["darknet"]["darknet_predictions_main_folder"] 
            self.darknet_configPath = cfg["darknet"]["darknet_configPath"]
            self.darknet_weightPath = cfg["darknet"]["darknet_weightPath"]
            self.darknet_metaPath = cfg["darknet"]["darknet_metaPath"]

            # keras options
            self.keras_files = cfg["keras"]["keras_files"]
            self.keras_predictions_main_folder = cfg["keras"]["keras_predictions_main_folder"] 
            self.keras_model_path = cfg["keras"]["keras_model_path"]
            self.keras_names_path = cfg["keras"]["keras_names_path"]
            self.keras_image_size = (int(cfg["keras"]["keras_image_w"]), int(cfg["keras"]["keras_image_h"]))
            self.keras_grayscale = cfg["keras"]["keras_grayscale"]
            self.keras_confidence_threshold = float(cfg["keras"]["keras_confidence_threshold"])
        except:
            raise Exception("configuration file is broken")


    def __set_logger(self):
        """sets logger for predictor class"""
        logger = logging.getLogger(self.logger_name)  
        if(not logger.handlers):
            logger.setLevel(20)
            
            # log formatter
            formatter = logging.Formatter("[%(levelname)s] \n%(asctime)s \n%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

            # file handler
            if(self.log_file):
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            # stream handler
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger


    # file folder operations 
    def __read_from_file(self, file_name):
        """read file"""
        try:
            with open(file_name,'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except (OSError, IOError) as e:
            print(e)

    def __read_json_file(self, cfg_path):
        """read json file"""
        with open(cfg_path,"r") as file:
            d = json.load(file)
        return d


    def __create_dir_if_not_exists(self, path):
        if(not os.path.exists(path)):
            os.makedirs(path)

    def __create_unique_file_name(self, file_path, before_number="(", after_number=")"):
        """creates a unique image name for saving"""
        temp_file_path = file_path
        file_name_counter = 1
        if(os.path.isfile(temp_file_path)):
            while(True):
                save_path, temp_file_name = os.path.split(temp_file_path)
                temp_file_name, temp_file_extension = os.path.splitext(temp_file_name)
                temp_file_name = "{0}{1}{2}{3}{4}".format(temp_file_name, before_number, file_name_counter, after_number, temp_file_extension)
                temp_file_path = os.path.join(save_path, temp_file_name)
                file_name_counter += 1
                if(os.path.isfile(temp_file_path)):
                    temp_file_path = file_path
                else:
                    file_path = temp_file_path
                    break

        return file_path

    
    # image operations
    def __move_image(self, temp_image_path, image_class, backend):
        """saves image by moving image from temp folder to its class folder by its name"""

        if(backend == "darknet"):
            predictions_main_folder = self.darknet_predictions_main_folder
        elif(backend == "keras"):
            predictions_main_folder = self.keras_predictions_main_folder
        else:
            predictions_main_folder = self.predictions_main_folder
        

        # prepare new image name for predictions directory
        _ , temp_image_name = os.path.split(temp_image_path)
        predicted_image_class_path = os.path.join(predictions_main_folder, image_class)
        predicted_image_path = self.__create_unique_file_name(os.path.join(predicted_image_class_path, temp_image_name))

        # create class file if not exists
        self.__create_dir_if_not_exists(predicted_image_class_path)

        # move image from temp to predictions
        os.rename(temp_image_path, predicted_image_path)

    def __convert_prediction_array_to_byte(self, temp_image_path, image):
        """this method saves image array to convert it to bytes without saving it is not working"""
        _ , temp_image_name = os.path.split(temp_image_path)
        temp_predicted_image_path = self.__create_unique_file_name(os.path.join(self.predictions_temp_path, temp_image_name))
        cv2.imwrite(temp_predicted_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        byte_image = open(temp_predicted_image_path, "rb")
        os.remove(temp_predicted_image_path)
        return byte_image

    def __load_image_keras(self, image_path):
        """load, resize, reshape image for keras prediction"""
        
        img_width = self.keras_image_size[0]
        img_height = self.keras_image_size[1]
        
        try:
            if(self.keras_grayscale):
                third_dimension = 1
                img_array = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            else:
                third_dimension = 3
                img_array = cv2.imread(image_path)

            new_array = cv2.resize(img_array, (img_width, img_height))
            new_array = new_array.reshape(-1, img_width, img_height, third_dimension)
        except:
            return None

        return new_array




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
            self.keras_names = self.__read_from_file(self.keras_names_path).split()

            # load model
            self.keras_model = keras.models.load_model(self.keras_model_path)

            return True
        except:
            self.logger.exception("could not load keras model")
            return False


    def init_predictor(self, darknet = True, keras = False):
        """initiates a backend for prediction"""
        if(darknet):
            if(self.__init_darknet()):
                self.is_darknet_inited = True
        if(keras):
            if(self.__init_keras()):
                self.is_keras_inited = True



    def predict_image_keras(self, image_path, save_image = ""):
        if(self.is_keras_inited):

            image = self.__load_image_keras(image_path)

            if(not isinstance(image, np.ndarray)):
                self.logger.error("image could not been loaded")
                return False, None
            
            # prediction exception handling 
            try:
                # result = self.keras_model.predict_classes(image)
                raw_prediction = self.keras_model.predict(image)
                predicted_class = np.argmax(raw_prediction)
                prediction_confidence = raw_prediction[0][predicted_class]
                predicted_class_str = str(self.keras_names[predicted_class])
            except:
                self.logger.exception("model.predict raised exception")
                return False, None

            self.logger.info("predicted class: {0} confidence: {1}".format(predicted_class_str, prediction_confidence))
            

            # handle result for user
            if(prediction_confidence > self.keras_confidence_threshold):    
                image_class = predicted_class_str
            else:
                image_class = "not-classified"
                
            # save image by class
            if(save_image == "save"):
                self.__move_image(image_path, image_class, "keras")
            elif(save_image == "remove"):
                os.remove(image_path)
            else:
                pass
    
            return True, image_class

        else:
            self.logger.warning("first init the keras backend")
            return False, None



    def predict_image_darknet(self, image_path, save_image = ""):
        if(self.is_darknet_inited):
            # performDetect(imagePath="data/dog.jpg", thresh= 0.25, configPath = "./cfg/yolov4.cfg", weightPath = "yolov4.weights", metaPath= "./cfg/coco.data", showImage= True, makeImageOnly = False, initOnly= False):

            # prediction exception handling 
            try:
                result = darknet.performDetect(imagePath=image_path, configPath = self.darknet_configPath, weightPath = self.darknet_weightPath, metaPath= self.darknet_metaPath, showImage= True, makeImageOnly=True)
            except:
                self.logger.exception("performDetect raised exception")
                return False, None, None


            # handle result for user
            detections_str = "" 
            byte_image = None
            if(result and result["detections"]):    
                for detection in result["detections"]:
                    detections_str += "{0} - {1:.2f}\n".format(detection[0], detection[1])

                # print(result)
                # TODO database
                # assign image to first predicted classes folder
                image_class = result["detections"][0][0]

                # temporarily save image because telegram does not like othervise -_-
                byte_image = self.__convert_prediction_array_to_byte(image_path, result["image"])

            else:
                detections_str = "not-classified"
                image_class = "not-classified"
                

            # save image by class
            if(save_image == "save"):
                self.__move_image(image_path, image_class, "darknet")
            elif(save_image == "remove"):
                os.remove(image_path)
            else:
                pass


            return True, detections_str, byte_image
        else:
            self.logger.warning("first init the darknet backend")
            return False, None, None

