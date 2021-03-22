from pandas import DataFrame
import logging

def dataframe_empty_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AttributeError, KeyError, TypeError) as e:
            logging.info(args, kwargs)
            logging.info(e)
            return DataFrame()
    return wrapper