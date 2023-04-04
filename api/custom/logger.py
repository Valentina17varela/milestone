import logging

from config import ConfigClass


def set_logger(settings: ConfigClass) -> logging.Logger:
    level = logging.DEBUG if (settings.DEBUG or settings.TESTING) else logging.INFO
    name = "BELVO-INT"
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger = logging.Logger(name=name)

    handler = logging.StreamHandler()
    handler.setLevel(level=level)
    handler.setFormatter(fmt=format)

    logger.addHandler(hdlr=handler)

    return logger
