import sys
sys.path.insert(0, 'deep_predictor')

from deep_predictor import deep_predictor

dp = deep_predictor("deep_predictor/cfg/predictors/darknet_coco.cfg", init=True)
status, model_info, predictions, image_path = dp.predict_image("/home/can/Desktop/asd.jpg")


print(status)
print()
print(model_info)
print()
print(predictions)
print()
print(image_path)





# dp = deep_predictor()
#dp.init_predictor(darknet=True, keras=False)
#is_predicted, prediction, _ = dp.predict_image_darknet("images/test_images/food/asure/2.jpg")



# from database_handler import database_handler

# db = database_handler()

# db.delete_prediction("PV8EbJvv7mbS")


