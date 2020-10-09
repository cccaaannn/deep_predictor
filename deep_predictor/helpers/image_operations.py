import os
import cv2

import sys
sys.path.insert(0, 'deep_predictor')


from helpers.file_folder_operations import file_folder_operations

class image_operations():
    @staticmethod
    def validate_extension(possible_extensions, image_name):
        _ , ext = os.path.splitext(image_name)
        if(ext not in possible_extensions):
            return 0
        else:
            return 1
    
    @staticmethod
    def validate_image(image_path, delete = True):
        try:
            temp_array = cv2.imread(image_path) 
            _ = cv2.resize(temp_array, (224, 224)) 
            return 1
        except:
            if(delete):
                os.remove(image_path)
            return 0

    @staticmethod
    def move_image_by_class_name(temp_image_path, main_save_folder, image_class):
        """saves image by moving image from temp folder to its class folder by its name"""

        # prepare new image name for predictions directory
        _ , temp_image_name = os.path.split(temp_image_path)
        predicted_image_class_path = os.path.join(main_save_folder, image_class)
        predicted_image_path = file_folder_operations.create_unique_file_name(os.path.join(predicted_image_class_path, temp_image_name))

        # create class file if not exists
        file_folder_operations.create_dir_if_not_exists(predicted_image_class_path)

        # move image from temp to predictions
        os.rename(temp_image_path, predicted_image_path)
        
        return predicted_image_path

    @staticmethod
    def load_image_keras(image_path, image_size, grayscale):
        """load, resize, reshape image for keras prediction"""
        
        img_width = image_size[0]
        img_height = image_size[1]
        
        try:
            if(grayscale):
                third_dimension = 1
                img_array = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            else:
                third_dimension = 3
                img_array = cv2.imread(image_path)

            new_array = cv2.resize(img_array, (img_width, img_height))
            new_array = new_array.reshape(-1, img_width, img_height, third_dimension)
        except:
            return None

        return new_array