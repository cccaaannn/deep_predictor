import time

class predictor():
    def __init__(self):
        print("**********************DUMMY PREDICTOR STARTED**********************")
        self.is_inited = False

    def init(self):
        print("**********************DUMMY PREDICTOR INITED**********************")
        self.is_inited = True


    def predict_image_keras(self, temp_image_path, save_image = ""):
        if(self.is_inited):
            print("**********************INITED DUMMY PREDICTOR MAKING PREDICTION**********************")
            time.sleep(5)
            return 200, {'predictions': {'is_confident': 1, '1': {'class_name': '1', 'confidence': 1.0, 'class_index': 1}}}, "deep_predictor\images\predictions\keras\1"
        else:
            print("**********************DUMMY PREDICTOR NOT INITED**********************")


    def predict_image_darknet(self, temp_image_path, save_image = ""):
        if(self.is_inited):
            print("**********************INITED DUMMY PREDICTOR MAKING PREDICTION**********************")
            time.sleep(5)
            return 200, '{ "pred1" : {"class" : 1,"x1" : 1,"y1" : 1,"c1" : 1,"c2" : 1}, "pred2" : {"class" : 2,"x1" : 2,"y1" : 2,"c1" : 2,"c2" : 2}}', "deep_predictor\images\predictions\keras\1"
        else:
            print("**********************DUMMY PREDICTOR NOT INITED**********************")