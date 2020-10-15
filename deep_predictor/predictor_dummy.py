import time

class predictor():
    def __init__(self, init=False):
        print("**********************DUMMY PREDICTOR STARTED**********************")
        self.is_inited = False

        if(init):
            self.init()

    def init(self):
        print("**********************DUMMY PREDICTOR INITED**********************")
        self.is_inited = True


    def predict_image(self, temp_image_path, save_image = ""):
        if(self.is_inited):
            print("**********************INITED DUMMY PREDICTOR MAKING PREDICTION**********************")
            time.sleep(2)
            return (
                200, 
                {'predictor_backend': 'keras', 'model_id': 200, 'image_w': 224, 'image_h': 224, 'grayscale': 0, 'return_topN': 3, 'confidence_threshold': 0.9}, 
                {'predictions': {'is_confident': 0, '1': {'class_index': 1, 'class_name': 'adanaKenap', 'confidence': 0.72227687}, '2': {'class_index': 2, 'class_name': 'akcaabatKofte', 'confidence': 0.17435183}, '3': {'class_index': 5, 'class_name': 'bulgurPilavi', 'confidence': 0.06662769}}}, 
                "deep_predictor/images/predictions/keras/1"
            )
            
        else:
            print("**********************DUMMY PREDICTOR NOT INITED**********************")


    def predict_image_darknet(self, temp_image_path, save_image = ""):
        if(self.is_inited):
            print("**********************INITED DUMMY PREDICTOR MAKING PREDICTION**********************")
            time.sleep(5)
            return 200, '{ "pred1" : {"class" : 1,"x1" : 1,"y1" : 1,"c1" : 1,"c2" : 1}, "pred2" : {"class" : 2,"x1" : 2,"y1" : 2,"c1" : 2,"c2" : 2}}', "deep_predictor/images/predictions/yolo/1"
        else:
            print("**********************DUMMY PREDICTOR NOT INITED**********************")