"""
Module to control logging and logger instance so not to clash with other loggers
"""

import logging
from logging import Logger
from functools import wraps

def get_logger() -> Logger:
    """
    This will get/create the unique logger for koalas.
    """

    # request or create a logger
    logger = logging.getLogger("koalas-log")

    # only do setup if needed
    if (not logger.hasHandlers()):
        logger.setLevel(logging.ERROR)
        fmt = '%(asctime)s|%(filename)-18s|%(funcName)-25s|%(levelname)-8s|: %(message)s'
        fmt_date = '%Y-%m-%dT%T'
        formatter = logging.Formatter(fmt, fmt_date)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger 

def info(msg:str, *args, **kwargs):
    """
    Sends a info message to the koalas logger.
    """
    get_logger().info(msg, stacklevel=2, *args, **kwargs) 

def debug(msg:str, *args, **kwargs):
    """
    Sends a debug message to the koalas logger.
    """
    get_logger().debug(msg, stacklevel=2, *args, **kwargs) 

def warn(msg:str, *args, **kwargs):
    """
    Sends a warning message to the koalas logger.
    """
    get_logger().warn(msg, stacklevel=2, *args, **kwargs) 

def error(msg:str, *args, **kwargs):
    """
    Sends a error message to the koalas logger.
    """
    get_logger().error(msg, stacklevel=2, *args, **kwargs)

def setLevel(level):
    """
    Sets the logging level for koalas.
    """
    get_logger().setLevel(level)

def enable_logging(func):
    """
    Optional Parameters
    -------------------
    - debug [`True/False`]: if `True` function will show info level msgs
    - debug_level: sets the level of logging to show. 
    """
    # add to docstrings so 
    func.__doc__  += enable_logging.__doc__

    @wraps(func)
    def wrapped(*args, **kwargs):
        # a tuple of the names of the parameters that func accepts
        func_params = func.__code__.co_varnames[:func.__code__.co_argcount]
        # grab all of the kwargs that are not accepted by func
        extra = set(kwargs.keys()) - set(func_params)
        debug = False
        # set logger settings
        if ("debug" in extra):
            # remove from kwargs
            debug = kwargs.pop("debug")
            # set debug on at info level
            get_logger().setLevel(logging.INFO)
        if (debug and "debug_level" in extra):
            # remove from kwargs
            level = kwargs.pop("debug_level")
            # set debug on at given level
            get_logger().setLevel(level)
        # run function as intended
        val = func(*args, **kwargs)
        # reset logger
        get_logger().setLevel(logging.ERROR)
        # pass value back if needed
        return val
    
    return wrapped