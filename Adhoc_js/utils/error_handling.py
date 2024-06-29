import logging

def log_error_and_raise_exception(error_str: str, exc_obj: Exception = None):
    """
    Logs the error and raises an Exception.
    Pass the exc_obj if the exception details need to be logged.
    """
    logging.error(error_str, exc_info=exc_obj)
    raise Exception(error_str)

def log_error_and_exit(error_str: str, exc_obj: Exception = None):
    """
    Logs the error and exits the process with exit code 1.
    Pass the exc_obj if the exception details need to be logged.
    """
    logging.error(error_str, exc_info=exc_obj)
    exit(1)
