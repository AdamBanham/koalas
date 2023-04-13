"""
This module contains information about the structure of complex
api for process data, being how to represent an event,
a trace and an event log in complex form, which considers the
data perspective.
"""

from typing import Mapping
from copy import deepcopy

from koalas._logging import info, debug, enable_logging


class ComplexEvent():
    """
    A complex form of an event, an atomic change in the state
    of a process.
    """

    STR_FORMAT = "(e : {act}|{map})"

    def __init__(self, activity:str, data:Mapping[str,object]) -> None:
        self._act = activity
        self._map = deepcopy(data)
        self._hash = hash(
            tuple(
                [self._act,]+
                [hash(tuple([key,val])) for key,val 
                 in self._map.items()]
                )
        )

    def activity(self) -> str:
        """ the process activity denoted by this event """
        return self._act

    def data(self) -> Mapping[str,object]:
        """ returns a copy of the data attached at this event """
        return deepcopy(self._map)
    

    # data model functions
    def __getitem__(self, key):
        if key in self._map.keys():
            return deepcopy(self._map[key])
        else:
            return "UNDEFINED"

    def __str__(self) -> str:
        label = self.STR_FORMAT.format(act=self._act,map=self._map)
        return label

    def __repr__(self) -> str:
        repr = "ComplexEvent(\n\t"
        repr += f"'{self._act}'" + ", {\n"
        for key,val in self._map.items():
            repr += f"\t'{key}' : {val.__repr__()},\n"
        repr += "\t}\n)"
        return repr
    
    def __hash__(self) -> int:
        return self._hash
