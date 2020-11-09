# deep predictor
### A simple backend for image prediction tasks that uses deep learning.

***

![GitHub top language](https://img.shields.io/github/languages/top/cccaaannn/deep_predictor?style=flat-square) ![](https://img.shields.io/github/repo-size/cccaaannn/deep_predictor?style=flat-square) [![GitHub license](https://img.shields.io/github/license/cccaaannn/deep_predictor?style=flat-square)](https://github.com/cccaaannn/deep_predictor/blob/master/LICENSE) 

## Features
- Supports multiple models running at the same time. [supported deep learning backends](#Supported-deep-learning-backends)
- Easy to configure for new models. [adding a new model](#Adding-a-new-model)
- Saves detailed info about model and prediction to the database.
- Organizes predicted images by saving them to folders named by most confident class names. [predicted images save structure](#Predicted-images-save-structure)
- Simple api style works with client side id, no need for login-register. [api](#Api)
- Example minimalist frontend. [how it looks](#How-it-looks)

</br>

## Setting it up
1. Install requirements for your os.
    - It would be less problematic if you use same tensorflow and keras versions that you used to train your models.
2. Add your models. [adding a new model](#Adding-a-new-model)
3. Run deep predictor. [running the application](#Running-the-application)

</br>

## Adding a new model
1. Create a cfg file for the new model with using cfg template under `cfg/templates`. [supported deep learning backends](#Supported-deep-learning-backends)
2. Fill the fields in the cfg template according to specifications of the new model.
3. Add the new cfg file's path and a frontend name for it to `predictors` field inside `deep_predictor.cfg`. 
4. Chose a default predictor and set `default_predictor_name`.
    - Default predictor will run if the `model_name` field is posted empty from the frontend.

**Deep predictor runs all models added under predictors.**

#### Example from `deep_predictor.cfg`
```json
"prediction_options":{
    "default_predictor_name" : "vgg16",
    "predictors" : {
        "vgg16" : "deep_predictor/cfg/predictors/vgg16.cfg",
        "densenet" : "deep_predictor/cfg/predictors/densenet201.cfg"
    }
}
```

</br>

## Running the application
1. `waitress_server.py` will run the app on production.
2. Directly running `flask_app.py` will run the app on development.
- If you have multiple `deep_predictor.cfg` files with different name or paths, pass the path of your file to `create_app` function.

</br>

## Supported deep learning backends
- Right now deep predictor supports regular `keras cnn` models and tensorflow converted `darknet yolo` models.
    - [Darknet](https://github.com/Alexeyab/darknet).
    - For converting yolo models you can use [tensorflow-yolov4-tflite github](https://github.com/hunglc007/tensorflow-yolov4-tflite).


</br>

## Configurations
- `deep_predictor.cfg` is the main config file, it has a lot of options and they are self explanatory.
- Logger names, logging levels and log files paths also can be modified from `loggers.cfg`.

</br>

## Api
1. Post required fields with these form names to `/upload`.
    1. `prediction_id`
        - String unique id, length can be modified from `deep_predictor.cfg`.
    2. `model_name`
        - Model names can be modified from `deep_predictor.cfg`.
        - You can get running model names from `/api?predictors`. [predictors result example](#Predictors-result-example)
    3. `image`
        - Accepted image types can be modified from `deep_predictor.cfg`.
2. Get the result from `/api?prediction_id=<prediction_id>` as json. [api response examples](#Api-response-examples)

- You can also use prediction status codes to make a better error output for frontend than I did 🤷🏻‍♂️. [prediction status codes](#Prediction-status-codes)

</br>

### Api response examples

#### Successful keras prediction result
```json
{
  "model_info": {
    "method": "vgg16",
    "model_id": 100,
    "predictor_backend": "keras"
  },
  "prediction_id": "dIeeoRzbNCYX",
  "prediction_status": 200,
  "prediction_time": 1604856542,
  "predictions": [
    {
      "class_index": 6,
      "class_name": "soup",
      "confidence": 0.97628
    },
    {
      "class_index": 4,
      "class_name": "apple",
      "confidence": 0.02319
    },
    {
      "class_index": 9,
      "class_name": "dessert",
      "confidence": 0.00041
    }
  ]
}
```

#### Successful tf_yolo prediction result
```json
{
  "model_info": {
    "method": "yolov4",
    "model_id": 4000,
    "predictor_backend": "tf_yolo"
  },
  "prediction_id": "JtGBTzNaj0A2",
  "prediction_status": 200,
  "prediction_time": 1604856413,
  "predictions": [
    {
      "bbox": {
        "cx": 0.28939,
        "cy": 0.66856,
        "h": 0.53053,
        "w": 0.23469
      },
      "class_name": "Dog",
      "confidence": 0.98514
    },
    {
      "bbox": {
        "cx": 0.75476,
        "cy": 0.21471,
        "h": 0.16953,
        "w": 0.29614
      },
      "class_name": "Truck",
      "confidence": 0.92009
    }
  ]
}
```
#### Failed prediction result
```json
{
  "model_info": {
    "method": "vgg16",
    "model_id": 100,
    "predictor_backend": "keras"
  },
  "prediction_id": "kdcwInSQ6RRE",
  "prediction_status": 510,
  "prediction_time": 1604857137,
  "predictions": ""
}
```


#### Predictors result example
```json
{
  "predictors": [
    "vgg16",
    "ms coco"
  ]
}
```


#### Prediction status codes
```
0 = prediction not exists
100 = predicting
200 = predicted successfully

predictor errors
500 = general prediction error
510 = image is not supported
520 = prediction cannot converted to json
530 = predicted image could not been saved, moved or deleted
550 = predictor backend not inited or crashed
560 = tensorflow version not supported
570 = predictor backend is not supported
```


### Predicted images save structure
```
|---densenet201
|   |---Kebap
|   |---Soup
|   |---not-confident
|   ...
|---vgg16
    |---Cookie
    |---Kebap
    |---Rice
    |---Soup
    |---Dessert
    |---not-confident
    ...
```


</br>

## How it looks
<img src="other/readme_images/main_page_example.png" alt="drawing" width="600"/>
<img src="other/readme_images/upload_image_example.png" alt="drawing" width="600"/>

</br>

## Results pages

<img src="other/readme_images/results_example1.png" alt="drawing" width="600"/>
<img src="other/readme_images/results_example2.png" alt="drawing" width="600"/>

</br>

## Mobile

<img src="other/readme_images/main_page_mobile_example.png" alt="drawing" width="200"/> <img src="other/readme_images/upload_image_mobile_example.png" alt="drawing" width="200"/> <img src="other/readme_images/results_mobile_example.png" alt="drawing" width="200"/>

</br>
