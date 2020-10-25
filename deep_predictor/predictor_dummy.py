import time

# my classes
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations
from logger_creator import logger_creator

class predictor_dummy():
    def __init__(self, cfg_path):
        self.logger = logger_creator().deep_predictor_logger()
        self.is_inited = False
        is_cfg_ok =  self.__set_options(cfg_path)
        if(is_cfg_ok):
            self.__init_backend()

        self.simulate_result = {
            "keras" : {'predictions': [{'class_name': 'person', 'confidence': 0.99786, 'bbox': {'x1': 193, 'y1': 98, 'x2': 271, 'y2': 379}}, {'class_name': 'dog', 'confidence': 0.99429, 'bbox': {'x1': 62, 'y1': 265, 'x2': 203, 'y2': 345}}, {'class_name': 'horse', 'confidence': 0.98321, 'bbox': {'x1': 405, 'y1': 140, 'x2': 600, 'y2': 344}}]},
            "tf_yolo" :  {'predictions': {'is_confident': 0, '1': {'class_index': 1, 'class_name': 'adanaKenap', 'confidence': 0.72227687}, '2': {'class_index': 2, 'class_name': 'akcaabatKofte', 'confidence': 0.17435183}, '3': {'class_index': 5, 'class_name': 'bulgurPilavi', 'confidence': 0.06662769}}}
        }

    # load cfg options
    def __set_options(self, cfg_path):
        try:
            cfg = file_folder_operations.read_json_file(cfg_path)
            # model_options
            self.simulate = cfg["predictor_options"]["model_options"]["simulate"]
            self.image_class = cfg["predictor_options"]["model_options"]["image_class"]
            self.sleep = cfg["predictor_options"]["model_options"]["sleep"]
            self.predicted_image_action = cfg["predictor_options"]["model_options"]["predicted_image_action"]
            # model_paths
            self.predictions_main_folder = cfg["predictor_options"]["model_paths"]["predictions_main_folder"] 
            return True
        except:
            self.logger.error("cfg file error", exc_info=True)
            return False

    def __init_backend(self):
        self.logger.info("dummy predictor inited")
        self.is_inited = True

    def predict_image(self, image_path):
        if(self.is_inited):
            self.logger.info("predictor dummy making prediction")
            time.sleep(self.sleep)

            # perform image action
            try:
                self.logger.info("performing chosen action to image ({0})".format(self.predicted_image_action))
                predicted_image_path = image_operations.perform_image_action(image_path, self.predictions_main_folder, self.image_class, self.predicted_image_action)
            except:
                self.logger.error("image action may not been performed", exc_info=True)
                return 530, None, None
            
            return 200, self.simulate_result[self.simulate], predicted_image_path

        else:
            self.logger.error("predictor dummy not ininted")

