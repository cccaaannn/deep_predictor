import os   
import cv2

import sys
sys.path.insert(0, 'deep_predictor')

from helpers.file_folder_operations import file_folder_operations

class telegram_helpers():
    @staticmethod
    def convert_prediction_array_to_byte(temp_image_path, image, predictions_temp_path):
        """this method saves image array to convert it to bytes without saving it is not working"""
        _ , temp_image_name = os.path.split(temp_image_path)
        temp_predicted_image_path = file_folder_operations.create_unique_file_name(os.path.join(predictions_temp_path, temp_image_name))
        cv2.imwrite(temp_predicted_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        byte_image = open(temp_predicted_image_path, "rb")
        os.remove(temp_predicted_image_path)
        return byte_image