import sys
sys.path.insert(0, 'deep_predictor')

from deep_predictor import deep_predictor
from telegram_bot_example.telegram_helpers import telegram_helpers



class deep_predictor_telegram(deep_predictor):
    def __init__(self, cfg_path="deep_predictor/cfg/deep_predictor.cfg", predictions_temp_path = "deep_predictor/images/predictions/yolo/temp"):
        super().__init__(cfg_path)
        self.predictions_temp_path = predictions_temp_path


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
                byte_image = telegram_helpers.convert_prediction_array_to_byte(image_path, result["image"], self.predictions_temp_path)

            else:
                detections_str = "not-classified"
                image_class = "not-classified"
                

            # save image by class
            if(save_image == "save"):
                self.__move_image_by_class_name(image_path, image_class, "darknet")
            elif(save_image == "remove"):
                os.remove(image_path)
            else:
                pass


            return True, detections_str, byte_image
        else:
            self.logger.warning("first init the darknet backend")
            return False, None, None


