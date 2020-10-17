from concurrent.futures import ThreadPoolExecutor
import requests
import random
import string


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return "can" + ''.join(random.choice(chars) for _ in range(size))


def request():
    prediction_id = id_generator()

    url = 'http://127.0.0.1:5000/upload'
    files = {'file': open('test.jpg', 'rb')}
    data = {
        'model_name': "food 10 vgg16", 
        'prediction_id': prediction_id
    }
    requests.post(url, files=files, data=data)



with ThreadPoolExecutor(max_workers=50) as pool:
    for _ in range(50):
        pool.submit(request)
