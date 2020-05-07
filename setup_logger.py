import logging
import os
import time

formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
if not os.path.exists('logs'):
    os.makedirs('logs')
log_file_name = "logs/mesh_lora_" + time.strftime("%Y-%m-%d") + ".log"
file_handler = logging.FileHandler(log_file_name, mode="w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger = logging.getLogger('spam')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)



