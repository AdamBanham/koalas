"""
This module contains information about the structure of the simplified api 
for process data, being how to represent an event, a trace and an event log.
"""

from typing import Iterable, List, Mapping, Set, Tuple
from copy import deepcopy


class Trace():
    """
    A simplified representation of a sequence of events
    """

    def __init__(self, sequence: List[str]) -> None:
        self.sequence = deepcopy(sequence)
        self._len = len(self.sequence)
        self._hash = hash(tuple(event for event in self.sequence))

    # data model functions

    def __str__(self) -> str:
        if len(self.sequence) == 0:
            return "<>"
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

    def __iter__(self) -> Iterable[str]:
        for event in self.sequence:
            yield event

    def __getitem__(self,key:int) -> str:
        return self.sequence[key]

    def __eq__(self, __o: object) -> bool:
        if ( isinstance(__o, Trace )  ):
            return self.sequence.__eq__(__o.sequence)
        return False

    def __hash__(self) -> int:
        return self._hash

    def __len__(self) -> int:
        return self._len

    # accessors

    def get_id(self) -> str:
        return self.id



DEFAULT_SIMPLE_LOG_NAME="simple"

class EventLog():
    """
    A simplified representation of a language.
    """

    def __init__(self, traces: Iterable[Trace], 
                 name:str=DEFAULT_SIMPLE_LOG_NAME) -> None:
        # middleman to multi set repr
        self._freqset = dict()
        self._len = 0
        self._variants = 0
        for trace in traces:
            if (trace in self._freqset.keys()):
                self._freqset[trace] += 1
            else:
                self._freqset[trace] = 1
                self._variants += 1
            self._len += 1
        self.name = name 

    
    def language(self) -> Set[Trace]:
        "Get a trace language from this language"
        return self._freqset.keys()
    
    def stochastic_language(self) -> Mapping[Trace,float]:
        "Get a stochastic language from this language"
        return self._freqset.copy()

    # data model functions
    def __len__(self) -> int:
        return self._len

    def __iter__(self) -> Iterable[Tuple[Trace,int]]:
        return self._freqset.items().__iter__()

    def __str__(self) -> str:
        if (self._variants < 1):
            return "[]"

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

    def get_nvariants(self) -> int:
        return self._variants

    # membership test
    def __contains__(self, other):
        if isinstance(other, Trace):
            return other in self._freqset.keys()
        raise NotImplemented("Membership test not defined for :: "
         + type(other))

    # Rich comparisons 
    # https://peps.python.org/pep-0207/#classes
    # ==, <, <=, >, >=
    def __eq__(self,other):
        if isinstance(other,EventLog):
            return self.stochastic_language() == \
             other.stochastic_language()
        return False

    def __lt__(self,other):
        pass 

    def __le__(self,other):
        pass 

    def __gt__(self,other):
        pass 

    def __ge__(self,other):
        pass 
    
    # Emulating numeric types
    # do we need these? could be cool for extra bits
    # <<, >>, &, ^, |
    def __lshift__(self, other):
        pass 

    def __rshift__(self, other):
        pass 

    def __and__(self, other):
        pass

    def __xor__(self, other):
        pass

    def __or__(self, other):
        pass


