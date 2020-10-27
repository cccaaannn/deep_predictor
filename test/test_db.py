import sys
sys.path.insert(0, 'deep_predictor')

from database_handler import database_handler
import uuid

# example results for testing database and database handler
prediction_id = str(uuid.uuid4())
prediction = {'predictions': [{'class_index': 0, 'class_name': 'acibademKurabiyesi', 'confidence': 0.9982}, {'class_index': 7, 'class_name': 'kasarliPide', 'confidence': 0.00109}, {'class_index': 5, 'class_name': 'bulgurPilavi', 'confidence': 0.00071}, {'class_index': 3, 'class_name': 'asure', 'confidence': 0.0}, {'class_index': 9, 'class_name': 'kunefe', 'confidence': 0.0}]}
image_path = "deep_predictor\images\predictions\keras\vgg16\acibademKurabiyesi\af360c56-c524-41f7-834a-d9b5150b797e.jpg"
model_info = {'predictor_backend': 'keras', 'method': 'vgg16', 'model_id': 100}
model_id = 100
failed_prediction_status = 500


# connect to db
db = database_handler("test/database/test_database.db")


# testing db functions
# db.create_prediction(prediction_id, model_info, model_id)
# db.update_failed_prediction(prediction_id, failed_prediction_status)
# db.delete_prediction(prediction_id)

status = db.is_prediction_exists(prediction_id)
if(not status):
    db.create_prediction(prediction_id, model_info, model_id)
    db.update_successful_prediction(prediction_id, prediction, image_path)
    result = db.get_prediction_json(prediction_id)
    print(result)
else:
    print("prediction exists")

