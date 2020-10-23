import json
import pathlib
import os

class file_folder_operations():
    @staticmethod
    def read_from_file(file_name):
        """read file"""
        try:
            with open(file_name,'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except (OSError, IOError) as e:
            print(e)

    @staticmethod
    def read_json_file(cfg_path):
        """read json file"""
        with open(cfg_path,"r") as file:
            d = json.load(file)
        return d

    @staticmethod
    def create_dir_if_not_exists(path):
        """pathlib is not raises exception if path exists"""
        pathlib.Path(path).mkdir(parents=True, exist_ok=True) 
        # if(not os.path.exists(path)):
        #     os.makedirs(path, exist_ok=True)

    @staticmethod
    def create_unique_file_name(file_path, before_number="(", after_number=")"):
        """creates a unique image name for saving"""
        temp_file_path = file_path
        file_name_counter = 1
        if(os.path.isfile(temp_file_path)):
            while(True):
                save_path, temp_file_name = os.path.split(temp_file_path)
                temp_file_name, temp_file_extension = os.path.splitext(temp_file_name)
                temp_file_name = "{0}{1}{2}{3}{4}".format(temp_file_name, before_number, file_name_counter, after_number, temp_file_extension)
                temp_file_path = os.path.join(save_path, temp_file_name)
                file_name_counter += 1
                if(os.path.isfile(temp_file_path)):
                    temp_file_path = file_path
                else:
                    file_path = temp_file_path
                    break

        return file_path

    @staticmethod
    def read_class_names_tf_yolo(class_file_name):
        names = {}
        with open(class_file_name, 'r') as data:
            for ID, name in enumerate(data):
                names[ID] = name.strip('\n')
        return names