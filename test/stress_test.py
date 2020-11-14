from concurrent.futures import ThreadPoolExecutor
import requests
import random
import string
import json
import os


class stress_generator():
    def __init__(self, id_prefix, id_size, url, test_image_folder, model_names):
        self.id_prefix = id_prefix
        self.id_size = id_size
        self.url = url
        self.images = [os.path.join(test_image_folder, image) for image in os.listdir(test_image_folder)]
        self.model_names = model_names

    def __pick_random_image(self):
        return random.choice(self.images)

    def __pick_random_model(self):
        return random.choice(self.model_names)

    def __id_generator(self, chars=string.ascii_letters + string.digits):
        return self.id_prefix + ''.join(random.choice(chars) for _ in range(self.id_size))

    def __make_request(self):
        prediction_id = self.__id_generator()

        files = {'image': open(self.__pick_random_image(), 'rb')}
        data = {'model_name': self.__pick_random_model(), 'prediction_id': prediction_id}

        requests.post(url, files=files, data=data)


    def start_test(self, workers=10, request_count=10):
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for _ in range(request_count):
                pool.submit(self.__make_request)




if __name__ == "__main__":
    id_prefix = "TEST" 
    id_size = 28
    url = 'http://127.0.0.1:5000/test-upload'
    # test_image_folder = "test_images/other"
    test_image_folder = "test_images/food"

    model_names_json = json.loads(requests.get('http://127.0.0.1:5000/test-api?predictors').text)
    model_names = model_names_json["predictors"]

    workers = 10
    request_count = 10

    stress_gen = stress_generator(id_prefix=id_prefix, id_size=id_size, url=url, test_image_folder=test_image_folder, model_names=model_names)
    stress_gen.start_test(workers=workers, request_count=request_count)





