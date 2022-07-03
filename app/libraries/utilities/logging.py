import logging


def get_logger(name, level=None):
    level = logging.INFO if level is None else level
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
