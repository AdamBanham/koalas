"""
This module contains information about the structure of complex
api for process data, being how to represent an event,
a trace and an event log in complex form, which considers the
data perspective.
"""

from typing import Mapping, Iterable, Set, List, Tuple
from copy import deepcopy
from time import time

from koalas._logging import info, debug, enable_logging
from koalas.simple import Trace, EventLog

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
        """ returns the activities seen in this trace """
        return deepcopy(self._acts)
    
    def data(self) -> Mapping[str,object]:
        """ returns the trace attributes """
        return deepcopy(self._map)
    
    def simplify(self) -> Trace:
        """ 
        returns a simplifed representation of this trace without data.
        """
        return Trace([ s.activity() for s in self])
    
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
        repr = "ComplexTrace(\n\t[\n" 
        # add events in sequence
        for ev in self:
            repr += "\t\t" + ev.__repr__() + ",\n"
        repr += "\t],\n"
        # add map
        repr += "\tdata= "+ self.data().__repr__() +"\n" 
        return repr + ")"
    
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

DEFAULT_COMPLEX_LOG_NAME = "complex log"
class ComplexEventLog():
    """
    A complex collection of complex traces and can have an 
    invariant mapping. This collection can express several 
    languages.
    """

    @enable_logging
    def __init__(self, traces: Iterable[ComplexTrace],
                 data:Mapping[str,object] = None,
                 name:str = DEFAULT_COMPLEX_LOG_NAME) -> None:
        # middleman to multi set repr
        self._freqset = dict()
        self._instances = dict()
        self._len = 0
        self._variants = 0
        self._pop_size = 0
        self._acts = set([])
        self._start_acts = set([])
        self._end_acts = set([])
        self._traces = None
        self._map = deepcopy(data)
        info("Computing language...")
        start = time()
        for trace in traces:
            
            strace = trace.simplify()
            if (strace in self._instances):
                collector = self._instances[strace]
                if trace not in collector:
                    self._pop_size += 1
                    collector.add(trace)
            else:
                self._instances[strace] = set()
                self._instances[strace].add(trace)
                self._pop_size += 1
            trace = strace
            if (trace in self._freqset.keys()):
                self._freqset[trace] += 1
            else:
                self._acts = self._acts.union(
                    trace.seen_activities()
                )
                if (len(trace) > 0):
                    self._start_acts.add(trace[0])
                    self._end_acts.add(trace[-1])
                self._freqset[trace] = 1
                self._variants += 1
            self._len += 1
        self._traces = set([ t for t in self._freqset.keys() ])
        info(f"Computed language in {(time()-start)*1000:.0f}ms")
        self.name = name 

    @enable_logging
    def simplify(self) -> EventLog:
        """
        Simplifies this event log to only consider the process
        activities. Returns a new instance of simple event log.
        """
        simple_traces = []
        for trace, freq in self._freqset:
            simple_traces = simple_traces + ([ trace ] * freq)
        return EventLog(simple_traces, self.name)

    def seen_activities(self) -> Set[str]:
        "Get a language of process activities from this language."
        return deepcopy(self._acts)

    def seen_start_activities(self) -> Set[str]:
        "Get a set of start activities from this language."
        return deepcopy(self._start_acts)

    def seen_end_activities(self) -> Set[str]:
        "Get a set of end activities from this language."
        return deepcopy(self._end_acts)
    
    def simple_language(self) -> Set[Trace]:
        "Get a simplified trace language from this language."
        return set(list(self._freqset.keys()))
    
    def simple_stochastic_language(self) -> Mapping[Trace,float]:
        "Get a simplified stochastic language from this language."
        return self._freqset.copy()
    
    def get_instances(self) -> Mapping[Trace, Set[ComplexTrace]]:
        """ 
        Get a map between seen simple traces and instances 
        of complex traces.
        """
        return deepcopy(self._instances)
    
    def seen_instances_for(self, trace:Trace) -> Set[ComplexTrace]:
        """
        Explores this collection for instances of the given 
        simplified trace, may return instances or an empty collection.
        """
        if (trace in self._traces):
            return deepcopy(self._instances[trace]) 
        else:
            return []
        
    def get_name(self) -> str:
        " returns the name of this collection."
        return self.name

    def get_nvariants(self) -> int:
        " returns the number of trace variants in this collection."
        return self._variants
    
    def get_population_size(self) -> int:
        " returns the number of traces instances in this collection."
        return self._pop_size
    
    def data(self) -> Mapping[str,object]:
        " returns a data mapping for this collection, i.e. log-level attributes."
        return self._map
    
    # data model functions
    def __len__(self) -> int:
        return self.get_population_size()
    
    def __iter__(self) -> Iterable[Tuple[Trace,Set[ComplexTrace]]]:
        for strace, collector in self._instances.items:
            yield deepcopy(strace), deepcopy(collector)


