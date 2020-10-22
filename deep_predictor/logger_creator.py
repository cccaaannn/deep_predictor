import logging
import os

from helpers.file_folder_operations import file_folder_operations

class logger_creator():

    def __init__(self, cfg_file_path = ""):
        paths_to_check = ["deep_predictor/cfg/loggers.cfg", "cfg/loggers.cfg"]

        if(cfg_file_path):
            self.cfg_file_path = cfg_file_path
            self.read_cfg_file()
        else:
            for path in paths_to_check:
                try:
                    self.cfg_file_path = path
                    self.read_cfg_file()
                    break
                except:
                    pass
            else:
                raise ValueError("logger creator cfg file does not exists on default paths")
        
        # fix root path problem
        root_path = "deep_predictor"
        for logger_file in self.cfg["logger_files"]:
            if(self.cfg["logger_files"][logger_file]):
                if(not os.path.isfile(self.cfg["logger_files"][logger_file])):
                    self.cfg["logger_files"].update( { logger_file : os.path.join(root_path, self.cfg["logger_files"][logger_file]) } )


    
    def read_cfg_file(self):
        self.cfg = file_folder_operations.read_json_file(self.cfg_file_path)

    def flask_logger(self):
        return self.create_logger(self.cfg["logger_names"]["flask"], self.cfg["logger_files"]["flask"], self.cfg["logger_levels"]["flask"])

    def prediction_thread_logger(self):
        return self.create_logger(self.cfg["logger_names"]["prediction_thread"], self.cfg["logger_files"]["prediction_thread"], self.cfg["logger_levels"]["prediction_thread"])

    def database_handler_logger(self):
        return self.create_logger(self.cfg["logger_names"]["database_handler"], self.cfg["logger_files"]["database_handler"], self.cfg["logger_levels"]["database_handler"])
    
    def deep_predictor_logger(self):
        return self.create_logger(self.cfg["logger_names"]["predictor"], self.cfg["logger_files"]["predictor"], self.cfg["logger_levels"]["predictor"])


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
