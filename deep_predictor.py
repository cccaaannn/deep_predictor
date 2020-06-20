import logging
import shutil
import os

import darknet



class deep_predictor():
    def __init__(self, predictions_main_folder = "images/predictions", darknet_files = "darknet_files", keras_files = "keras_files", logger_name = "deep_predictor_backend", log_file = None):
        self.logger_name = logger_name
        self.log_file = log_file
        self.logger = self.__set_logger()

        self.predictions_main_folder = predictions_main_folder 
        self.darknet_files = darknet_files
        self.keras_files = keras_files

        self.is_inited = False


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

    def __create_dir_if_not_exists(self, path):
        if(not os.path.exists(path)):
            os.makedirs(path)

    def __save_image(self, temp_image_path, image_class):
        """saves image by moving image from temp folder to its class folder by its name"""
        # prepare new image name for predictions directory
        _ , temp_image_name = os.path.split(temp_image_path)
        predicted_image_class_path = os.path.join(self.predictions_main_folder, image_class)
        predicted_image_path = self.__create_unique_file_name(os.path.join(predicted_image_class_path, temp_image_name))

        # create class file if not exists
        self.__create_dir_if_not_exists(predicted_image_class_path)

        # move image from temp to predictions
        os.rename(temp_image_path, predicted_image_path)


    def __init_darknet(self):
        self.logger.info("loading darknet network to ram")
        darknet.performDetect(configPath = "{0}/yolov4.cfg".format(self.darknet_files), weightPath = "{0}/yolov4.weights".format(self.darknet_files), metaPath= "{0}/coco.data".format(self.darknet_files), initOnly=True)

    def __init_keras(self):
        self.logger.info("loading keras network to ram")
        # TODO
        # load keras model
        pass

    def init_predictor(self, darknet = True, keras = False):
        """initiates a backend for prediction"""
        if(darknet):
            self.__init_darknet()
            self.is_inited = True
        if(keras):
            self.__init_keras()
            self.is_inited = True


    def predict_image(self, image_path, save_image = True):
        if(self.is_inited):
            # performDetect(imagePath="data/dog.jpg", thresh= 0.25, configPath = "./cfg/yolov4.cfg", weightPath = "yolov4.weights", metaPath= "./cfg/coco.data", showImage= True, makeImageOnly = False, initOnly= False):

            # result = darknet.performDetect(imagePath=image_path, configPath = "darknet_files/yolov4.cfg", weightPath = "darknet_files/yolov4.weights", metaPath= "darknet_files/coco.data", showImage= False)
            result = darknet.performDetect(imagePath=image_path, configPath = "{0}/yolov4.cfg".format(self.darknet_files), weightPath = "{0}/yolov4.weights".format(self.darknet_files), metaPath= "{0}/coco.data".format(self.darknet_files), showImage= True, makeImageOnly=True)

            # class_name labeled_image

            # if(save_image):
            #     self.__save_image(image_path, image_class)
            # else:
            #     os.remove(image_path)
            
            
            
            return result
        else:
            print("first init the predictor with a backend")




dp = deep_predictor()
dp.init_predictor()

prediction = dp.predict_image("images/temp/dog.jpg")







