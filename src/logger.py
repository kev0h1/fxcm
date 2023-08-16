import logging


def get_logger(logger_name: str) -> logging.Logger:
    # create logger
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # create console handler and set level to info
    handler = logging.StreamHandler()

    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(levelname)s:\t  %(asctime)s - %(name)s - %(message)s"
    )

    handler.setFormatter(formatter)  # type: ignore

    # add handler to logger
    logger.addHandler(handler)

    return logger
