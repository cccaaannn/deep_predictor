from deep_predictor import deep_predictor



dp = deep_predictor(cfg_path="deep_predictor/cfg/mnist_options.cfg")

dp.init_predictor(darknet=False, keras=True)
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/0.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/1.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/2.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/3.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/4.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/5.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/6.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/7.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/8.jpg")
# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/other/9.jpg")

# is_predicted, prediction = dp.predict_image_keras("deep_predictor/images/test_images/food/tavuk_sis/1asd.jpg")

# dp = deep_predictor()
#dp.init_predictor(darknet=True, keras=False)
#is_predicted, prediction, _ = dp.predict_image_darknet("images/test_images/food/asure/2.jpg")



