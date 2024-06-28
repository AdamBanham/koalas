"""
Module to control logging and logger instance so not to clash with other loggers
"""

import logging
from logging import Logger
from typing import Iterator
from functools import wraps
from sys import stdout

LOG_FRMT = '%(asctime)s|%(filename)-25s|%(funcName)-40s|%(levelname)-8s|: %(message)s'

fmt = LOG_FRMT
fmt_date = '%Y-%m-%dT%T'
formatter = logging.Formatter(fmt, fmt_date)
DEFAULT_HANDLER = logging.StreamHandler(stdout)
DEFAULT_HANDLER.setFormatter(formatter)

def get_logger() -> Logger:
    """
    This will get/create the unique logger for koalas.
    """

    # request or create a logger
    logger = logging.getLogger("koalas-log")

    # only do setup if needed
    if (not logger.hasHandlers()):
        logger.setLevel(logging.ERROR)
        logger.addHandler(DEFAULT_HANDLER)

    return logger 

class InfoIteratorProcessor():
    """
    A helper class to track the progress of an iterator.
    """
    LOGGER_MSG = "{name} :: {curr}/{size}"

    def __init__(self, itername:str, iter:Iterator, stack:int=3) -> None:
        self._iter = iter 
        self._name = itername 
        self._curr = 0
        self._size = len(iter)
        self._reportstack = stack

    def __iter__(self) -> Iterator:
        for step in self._iter:
            self._curr += 1
            yield step 
            self.update(stack_level=self._reportstack)

    def update(self, stack_level:int=2) -> None:
        get_logger().info(
            self.LOGGER_MSG.format(
                name = self._name,
                curr = self._curr,
                size = self._size
            )
            ,
            stacklevel=stack_level
        )


class InfoQueueProcessor():
    """
    A helper class to track the progress of queues.
    """
    LOGGER_MSG = "{name} :: {curr}/{size}"

    def __init__(self, itername:str, starting_size:int) -> None:
        self._processed = 0 
        self._name = itername
        self._size = starting_size

    def extent(self, extension:int) -> None:
        """
        Updates the length of the queue.
        """
        self._size += extension
        self.update(increase=0, stacklevel=3)

    def update(self, increase:int=1, stacklevel:int=2) -> None:
        """
        Updates the number of completed items from the queue and reports a
        message.
        """
        self._processed += increase

        get_logger().info(
            self.LOGGER_MSG.format(
                name = self._name,
                curr = self._processed,
                size = self._size
            )
            ,
            stacklevel=stacklevel
        )

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
    if (func.__doc__ != None):
        func.__doc__  += enable_logging.__doc__

    @wraps(func)
    def wrapped(*args, **kwargs):
        # keep the level before
        old_level = get_logger().getEffectiveLevel()
        # a tuple of the names of the parameters that func accepts
        func_params = func.__code__.co_varnames[:func.__code__.co_argcount]
        # grab all of the kwargs that are not accepted by func
        old_level = get_logger().level
        extra = set(kwargs.keys()) - set(func_params)
        debug = kwargs.pop("debug",False)
        level = kwargs.pop("debug_level", logging.INFO)
        # set logger settings
        if debug:
            # set debug on at info level
            get_logger().setLevel(level)
        # run function as intended
        val = func(*args, **kwargs)
        # reset logger
        get_logger().setLevel(old_level)
        # pass value back if needed
        return val
    
    return wrapped