"""
This module contains information about the structure of complex
api for process data, being how to represent an event,
a trace and an event log in complex form, which considers the
data perspective.
"""

from typing import Mapping, Iterable, Set
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
    
class ComplexTrace():
    """
    A complex form of sequence of complex events, where a trace
    can have a invariant mapping attached for trace level attributes.
    """

    def __init__(self, events:Iterable[ComplexEvent], 
                 data: Mapping[str,object] = None) -> None:
        self._sequence = [ 
            deepcopy(event)
            for event
            in events
        ]
        self._len = len(self._sequence)
        if data == None:
            self._map = dict()
        elif isinstance(data,(dict)):
            self._map = deepcopy(data)
        else:
            raise ValueError(f"Given data is not a map/dict :: {type(data)}")
        self._hash = hash( 
            tuple(list(self._map.items()) + [ s.__hash__() for s in self._sequence])
        )
        self._acts = set([ s.activity() for s in self._sequence])

    # accessors
    def get_id(self) -> str:
        return "complex"
    
    def seen_activities(self) -> Set[str]:
        return deepcopy(self._acts)
    
    def data(self) -> Mapping[str,object]:
        return deepcopy(self._map)
    
    # data model functions
    def __str__(self) -> str:
        if (self._len < 1):
            return f"<>:{str(self._map)}"
        else:
            rep = "<"
            for event in self:
                rep = rep + f"{str(event)}, "
            rep = rep[:-2] + ">"
            return rep

    def __repr__(self) -> str:
        repr = "ComplexTrace([ComplexEvent('a',{})],{})"
        # TODO
        return repr
    
    def __iter__(self) -> Iterable[ComplexEvent]:
        for event in self._sequence:
            yield event 

    def __getitem__(self,no:int) -> ComplexEvent:
        if (isinstance(no,(int))):
            no = int(no)
            if (no < self._len and no >= 0):
                return self._sequence[no]
            else:
                raise ValueError("Invalid sequence reference, "+ 
                                 f"must be between 0 and {self._len}"+
                                 f" but was given {no}.")
        else:
            raise ValueError(
                "Invalid sequence reference, expecting a int"+
                f" but was given {type(no)}."      
            )

    def __eq__(self, __o: object) -> bool:
        if ( isinstance(__o, ComplexTrace )  ):
            if (self._map.__eq__(__o._map)): 
                if (self._len == __o._len):
                    for e,oe in zip(self, __o):
                        if (not e.__hash__() == oe.__hash__()):
                            return False 
                    return True
                else:
                    return False
            else:
                return False
        return False

    def __hash__(self) -> int:
        return self._hash

    def __len__(self) -> int:
        return self._len
