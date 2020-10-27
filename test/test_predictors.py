import sys
sys.path.insert(0, 'deep_predictor')

from deep_predictor import deep_predictor

dp = deep_predictor("deep_predictor/cfg/predictors/tf_yolo_coco.cfg")
status, predictions, image_path = dp.predict_image("impath")

print(status)
print()
print(predictions)
print()
print(image_path)
