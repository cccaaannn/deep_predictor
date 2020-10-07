import logging
from helpers.file_folder_operations import file_folder_operations

class logger_creator():

    def __init__(self, cfg_file_path = "deep_predictor/cfg/loggers.cfg"):
        self.cfg_file_path = cfg_file_path
        self.read_cfg_file()

    
    def read_cfg_file(self):
        self.cfg = file_folder_operations.read_json_file(self.cfg_file_path)

    def flask_logger(self):
        return self.create_logger(self.cfg["flask_logger"]["logger_name"], self.cfg["flask_logger"]["log_file"], self.cfg["flask_logger"]["log_level"])

    def prediction_thread_logger(self):
        return self.create_logger(self.cfg["prediction_thread_logger"]["logger_name"], self.cfg["prediction_thread_logger"]["log_file"], self.cfg["prediction_thread_logger"]["log_level"])

    def database_handler_logger(self):
        return self.create_logger(self.cfg["database_handler_logger"]["logger_name"], self.cfg["database_handler_logger"]["log_file"], self.cfg["database_handler_logger"]["log_level"])
    
    def deep_predictor_logger(self):
        return self.create_logger(self.cfg["predictor_logger"]["logger_name"], self.cfg["predictor_logger"]["log_file"], self.cfg["predictor_logger"]["log_level"])


    def create_logger(self, logger_name, log_file, log_level):
        logger = logging.getLogger(logger_name)  
        if(not logger.handlers):
            logger.setLevel(log_level)
            
            # log formatter
            formatter = logging.Formatter("[{0}][%(levelname)s] %(asctime)s %(message)s".format(logger_name), datefmt="%Y-%m-%d %H:%M:%S")

            # file handler
            if(log_file):
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            # stream handler
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger
