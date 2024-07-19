import logging
import config

def logError(e, msg):
    logging.error(f"{msg} - {str(e)}")
    if config.Log_To_File:
        with open(config.Log_Path, "a") as log_file:
            log_file.write(f"{msg} - {str(e)}\n")
    if config.Log_To_Console:
        print(f"{msg} - {str(e)}")