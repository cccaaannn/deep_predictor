import os
import cv2
import shutil
import pathlib
from PIL import Image

# fixing import problems caused by root path
# try:
#     from file_folder_operations import file_folder_operations
# except:
#     import sys
#     sys.path.insert(0, 'deep_predictor')
#     from helpers.file_folder_operations import file_folder_operations

class image_operations():
    @staticmethod
    def validate_extension(possible_extensions, image_name):
        """validates extension"""
        _ , ext = os.path.splitext(image_name)
        if(ext not in possible_extensions):
            return 0
        else:
            return 1
    
    @staticmethod
    def validate_image(image_path, try_to_convert = True, delete = True):
        """validates image by trying to resize it with opencv, if selected tries to convert unresizable image to jpg and tres to resize again"""
        is_image_ok = image_operations.try_to_resize_image(image_path)
        if(not is_image_ok and try_to_convert):
            # try to convert to jpg with pillow
            is_image_ok, image_path = image_operations.convert_to_jpg(image_path)
            # try resizing again
            if(is_image_ok):
                is_image_ok = image_operations.try_to_resize_image(image_path) 

            # if(not is_image_ok):
            #     # try to convert to jpg with ...
            #     is_image_ok, image_path = image_operations.convert_to_jpg(image_path)
            #     # try resizing again
            #     if(is_image_ok):
            #         is_image_ok = image_operations.try_to_resize_image(image_path) 


        if(is_image_ok):
            return 1, image_path
        else:
            if(delete):
                os.remove(image_path)
            return 0, image_path

    @staticmethod
    def try_to_resize_image(image_path):
        """tries to resize image with opencv"""
        try:
            temp_array = cv2.imread(image_path) 
            _ = cv2.resize(temp_array, (224, 224)) 
            return 1
        except:
            return 0

    @staticmethod
    def convert_to_jpg(image_path):
        """tries to convert the image to jpg with pillow"""
        try:
            # create new path name
            file_name, _ = os.path.splitext(image_path)
            new_path = file_name + ".jpg"
            
            # convert image
            im = Image.open(image_path).convert('RGB')
            im.save(new_path)

            # remove old extension image
            os.remove(image_path)
            return 1, new_path
        except Exception as e:
            print(e)
            return 0, image_path

    @staticmethod
    def move_image_by_class_name(temp_image_path, main_save_folder, image_class):
        """saves image by moving image from temp folder to its class folder by its name"""

        # prepare new image name for predictions directory
        _ , temp_image_name = os.path.split(temp_image_path)
        predicted_image_class_path = os.path.join(main_save_folder, image_class)
        predicted_image_path = os.path.join(predicted_image_class_path, temp_image_name)

        # create class file if not exists
        pathlib.Path(predicted_image_class_path).mkdir(parents=True, exist_ok=True) 

        # move image from temp to predictions
        shutil.move(temp_image_path, predicted_image_path)
        
        return predicted_image_path

    @staticmethod
    def perform_image_action(image_path, main_save_folder, image_class, image_action):
        """saves or removes image by given action RETURNS EMPTY STR IF ACTION IS NOT SPECIFIED"""
        predicted_image_path = ""
        if(image_action == "remove"):
            os.remove(image_path)
        elif(image_action == "save"):
            predicted_image_path = image_operations.move_image_by_class_name(image_path, main_save_folder, image_class)
        else:
            pass
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

    @staticmethod
    def load_image_tf_yolo(image_path, image_size):
        """load, resize image for tf yolo prediction"""
        try:
            original_image = cv2.imread(image_path)
            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

            image_data = cv2.resize(original_image, (image_size, image_size))
            image_data = image_data / 255.
        except:
            return None

        return original_image, image_data