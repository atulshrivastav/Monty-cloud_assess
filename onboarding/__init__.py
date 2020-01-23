import logging


FORMAT = "%(levelname)s - %(module)s: %(lineno)d - %(message)s"
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(format=FORMAT, level=logging.INFO)
