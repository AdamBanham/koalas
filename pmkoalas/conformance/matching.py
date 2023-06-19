"""
This module contains an alignment like process for transition trees, called 
matchings.
"""
from typing import Union
from copy import deepcopy

from pmkoalas.simple import Trace

class Matching():
    """
    A mapping of a trace to a path in a tree.
    """

    def __init__(self, path):
        self._path = deepcopy(path) 
        self._len = len(path)

    def __getitem__(self, i) -> Union[object,None]:
        if i < self._len:
            return self._path[i]
        else:
            return None