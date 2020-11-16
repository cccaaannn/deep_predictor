from concurrent.futures import ThreadPoolExecutor
import requests
import random
import json
import string
import os

class prediction_generator():
    """generates and posts prediction for testing"""
    def __init__(self, id_prefix, id_size, test_image_folder, api_key, model_names=None, post_url='http://127.0.0.1:5000/test-upload', predictors_url="http://127.0.0.1:5000/test-api?predictors"):
        self.id_prefix = id_prefix
        self.id_size = id_size
        self.post_url = post_url
        self.predictors_url = predictors_url
        self.images = [os.path.join(test_image_folder, image) for image in os.listdir(test_image_folder)]
        self.api_key = api_key

        # get test model name from api
        if(not model_names):
            model_names_json = json.loads(requests.get(self.predictors_url).text)
            model_names = model_names_json["predictors"]
        self.model_names = model_names

    def __id_generator(self, chars=string.ascii_letters + string.digits):
        """generates random id"""
        return self.id_prefix + ''.join(random.choice(chars) for _ in range(self.id_size))

    def __make_request(self, prediction_id):
        """picks random image and random model and makes post request"""
        files = {'image': open(random.choice(self.images), 'rb')}
        data = {'model_name': random.choice(self.model_names), 'prediction_id': prediction_id, "api_key":self.api_key}

        requests.post(self.post_url, files=files, data=data)


    def post_multiple_predictions(self, workers=1, request_count=1):
        """multiple posts with threading for stress tests"""
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for _ in range(request_count):
                prediction_id = self.__id_generator()
                pool.submit(self.__make_request, prediction_id)

    def post_prediction(self):
        """single post request for other tests"""
        prediction_id = self.__id_generator()
        self.__make_request(prediction_id)
        return prediction_id