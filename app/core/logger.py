import inspect
import logging
import os
# from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from fastapi import Request
# from fastapi.encoders import jsonable_encoder
from app.core.config import settings
import time

from pymongo.collection import Collection, ObjectId
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from typing import Union
class LoggerConfig:
    """
    Logger configuration class to setup logging for the application.
    """
 
    def __init__(
        self, env=20, logger_name="MyLogs", log_directory="logger", log_file="logs.log"
    ):
        """
        Initialize the logger configuration.
 
        Args:
            env (int): Logging level (10: DEBUG, 20: INFO, etc.).
            logger_name (str): Name of the logger.
            log_directory (str): Directory to store log files.
            log_file (str): Name of the log file.
 
        Raises:
            HTTPException: If there is an error creating the logger configuration.
        """
        try:
            self.logger_name = logger_name
            self.log_directory = os.path.abspath(log_directory)
            self.log_file_path = os.path.join(self.log_directory, log_file)
            self.env = env
            self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
 
            self.logger = logging.getLogger(self.logger_name)
            self.root_logger = logging.getLogger()
            self.setup_logging()
            self.setup_logger()
        except Exception as e:
            print(f"Failed to initialize logger: {str(e)}")
 
    def setup_logging(self):
        """
        Configure the basic logging settings.
 
        Raises:
            HTTPException: If there is an error setting up logging.
        """
        try:
            if self.logger.hasHandlers():
                self.logger.handlers.clear()
            if self.root_logger.hasHandlers():
                self.root_logger.handlers.clear()
 
            self.logger.propagate = False
            self.logger.setLevel(self.env)
            self.root_logger.setLevel(20)
        except Exception as e:
            print(f"Failed to setup logging: {str(e)}")
 
    def setup_logger(self):
        """
        Setup the logger with file and console handlers.
 
        Raises:
            HTTPException: If there is an error setting up the logger.
        """
        try:
            os.makedirs(self.log_directory, exist_ok=True)
 
            file_handler = RotatingFileHandler(
                self.log_file_path, backupCount=21, maxBytes=1024 * 1024 * 20, encoding="utf-8"
            )
            file_handler.setLevel(self.env)
 
            console_handler = logging.StreamHandler()
            console_handler.setLevel(30)
 
            formatter = logging.Formatter(self.log_format)
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
 
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
 
            root_file_handler = RotatingFileHandler(
                self.log_file_path, backupCount=21, maxBytes=1024 * 1024 * 20, encoding="utf-8"
            )
            root_file_handler.setLevel(self.env)
 
            root_console_handler = logging.StreamHandler()
            root_console_handler.setLevel(30)
 
            root_file_handler.setFormatter(formatter)
            root_console_handler.setFormatter(formatter)
 
            self.root_logger.addHandler(root_file_handler)
            self.root_logger.addHandler(root_console_handler)
        except Exception as e:
            print(f"Failed to setup logger handlers: {str(e)}")
 
    def define_logger(
        self,
        level: int,
        request: Request = None,
        loggName: "inspect.FrameInfo" = None,
        pid: int = None,
        message: str = None,
        body=None,
        response=None,
    ):
        """
        Write logs with detailed information.
 
        Args:
            level (int): Logging level.
            user (dict, optional): User information.
            request (Request, optional): Request data.
            loggName (FrameInfo, optional): File and function name.
            pid (int, optional): Process ID.
            message (str, optional): Log message.
            body (dict, optional): Request body.
            response (optional): Response data.
 
        Raises:
            HTTPException: If there is an error writing logs.
        """
        try:
           
            log_parts = {
                "IP": f"{request.client.host}" if request else None,
                "URL": f"{request.method} {request.url}" if request else None,
                "MESSAGE": message,
                "PID": str(pid) if pid is not None else None,
                "FILE": f"{loggName[1]}:{loggName[3]}" if loggName else None,
                "BODY": str(body) if body is not None else None,
                "RESPONSE": str(response) if response is not None else None,
            }
 
            txt = " - ".join(
                [f"{key}: {value}" for key, value in log_parts.items() if value is not None]
            )
 
            self.logger.log(level=level, msg=txt)
        except Exception as e:
            print(f"Failed to write logs: {str(e)}")
 
# Usage Example
logs = LoggerConfig(
    env=settings.LOGGER, 
    logger_name="APP-BE", 
    log_directory="logger", 
    log_file="app.log"
)
