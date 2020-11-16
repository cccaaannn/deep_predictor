from prediction_generator import prediction_generator

if __name__ == "__main__":
    id_prefix = "TEST" 
    id_size = 28
    test_image_folder = "test_images/food"
    api_key = "4c98a83efe384b53b1db01516907cabb"

    workers = 10
    request_count = 10

    prediction_gen = prediction_generator(id_prefix, id_size, test_image_folder, api_key)
    prediction_gen.post_multiple_predictions(workers=workers, request_count=request_count)
