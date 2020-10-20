import time

class predictor():
    def __init__(self, cfg_file, init=False):
        print("DUMMY PREDICTOR STARTED")
        self.is_inited = False

        if(init):
            self.init()

    def init(self):
        print("DUMMY PREDICTOR INITED")
        self.is_inited = True

    # simulate keras backend
    # def predict_image(self, temp_image_path, image_action = ""):
    #     if(self.is_inited):
    #         print("DUMMY PREDICTOR MAKING PREDICTION")
    #         time.sleep(2)
    #         return (
    #             200, 
    #             {'predictor_backend': 'keras', 'model_id': 200, 'image_w': 224, 'image_h': 224, 'grayscale': 0, 'return_topN': 3, 'confidence_threshold': 0.9}, 
    #             {'predictions': {'is_confident': 0, '1': {'class_index': 1, 'class_name': 'adanaKenap', 'confidence': 0.72227687}, '2': {'class_index': 2, 'class_name': 'akcaabatKofte', 'confidence': 0.17435183}, '3': {'class_index': 5, 'class_name': 'bulgurPilavi', 'confidence': 0.06662769}}}, 
    #             "deep_predictor/images/predictions/keras/1"
    #         )
            
    #     else:
    #         print("DUMMY PREDICTOR NOT INITED")

    # simulate darknet backend
    def predict_image(self, temp_image_path, image_action = ""):
        if(self.is_inited):
            print("DUMMY PREDICTOR MAKING PREDICTION")
            time.sleep(2)
            return (
                200,
                {'predictor_backend': 'darknet', 'method': 'yolov4', 'model_id': 1000, 'image_w': 608, 'image_h': 608, 'confidence_threshold': 0.25},
                {'predictions': [{'class_name': 'person', 'confidence': 0.99786, 'bbox': {'x1': 193, 'y1': 98, 'x2': 271, 'y2': 379}}, {'class_name': 'dog', 'confidence': 0.99429, 'bbox': {'x1': 62, 'y1': 265, 'x2': 203, 'y2': 345}}, {'class_name': 'horse', 'confidence': 0.98321, 'bbox': {'x1': 405, 'y1': 140, 'x2': 600, 'y2': 344}}]},
                "deep_predictor/images/predictions/darknet/yolov4/person"
            )
            
        else:
            print("DUMMY PREDICTOR NOT INITED")
