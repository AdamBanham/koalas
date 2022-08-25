"""
This module contains information about the structure of the simplified api for process data,
 being how to represent an event, a trace and an event log.
"""

from typing import Iterable, List, Mapping, Set, Tuple
from copy import deepcopy

class Event():
    """
    A simplified representation of an event.
    """

    def __init__(self, simple_name:str) -> None:
        self.name = simple_name

    # data model functions

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Event('{self.name}')"

    def __eq__(self, __o: object) -> bool:
        if ( isinstance(__o, Event)):
            return self.name.__eq__(__o.name)
        return False

    # accessors

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> str:
        return self.id


class Trace():
    """
    A simplified representation of a sequence of events
    """

    def __init__(self, sequence: List[Event]) -> None:
        self.sequence = deepcopy(sequence)
        self._hash = hash(tuple(event.name for event in self.sequence))

    # data model functions

    def __str__(self) -> str:
        rep = "<"
        for event in self:
            rep = rep + f"{str(event)},"
        rep = rep[:-1] + ">"
        return rep

    def __repr__(self) -> str:
        event_repr = "["
        for event in self:
            event_repr = event_repr + event.__repr__() +","
        event_repr = event_repr[:-1] + "]"

        return f"Trace({event_repr})"

    def __iter__(self):
        for event in self.sequence:
            yield event

    def __eq__(self, __o: object) -> bool:
        if ( isinstance(__o, Trace )  ):
            return self.sequence.__eq__(__o.sequence)
        return False

    def __hash__(self) -> int:
        return self._hash

    # accessors

    def get_id(self) -> str:
        return self.id


class EventLog():
    """
    A simplified representation of a language.
    """

    def __init__(self, traces: Iterable[Trace], name:str) -> None:
        # middleman to multi set repr
        self._freqset = dict()
        self._len = 0
        for trace in traces:
            if (trace in self._freqset.keys()):
                self._freqset[trace] += 1
            else:
                self._freqset[trace] = 1
            self._len += 1
        self.name = name 

    
    def get_language(self) -> Set[Trace]:
        return set()
    
    def get_stochastic_language(self) -> Mapping[Trace,float]:
        return dict() 

    # data model functions
    def __len__(self) -> int:
        return self._len

    def __iter__(self) -> Iterable[Tuple[Trace,int]]:
        return self._freqset.items().__iter__()

    def __str__(self) -> str:
        _str = "["
        for trace,freq in self:
            _str = _str + str(trace) + f"^{freq},"
        _str = _str[:-1] + "]"
        return _str

    def __repr__(self) -> str:
        return self.__str__()

    # accessors 
    def get_name(self) -> str:
        return self.name


