import logging
import colorlog


def get_logger(logger_name: str) -> logging.Logger:
    # create logger
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    file_handler = logging.FileHandler("my_logger.log")

    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(levelname)s:\t  %(asctime)s - %(name)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.ERROR)

    handler.setFormatter(formatter)  # type: ignore

    # add handler to logger
    logger.addHandler(handler)
    logger.addHandler(file_handler)

    return logger
