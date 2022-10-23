"""
This module contains information about the structure of the simplified api 
for process data, being how to represent an event, a trace and an event log.
"""

from typing import Iterable, List, Mapping, Set, Tuple
from copy import deepcopy
from time import time

from koalas._logging import info,debug, enable_logging
from koalas.directly import DirectlyFlowsPair,FlowLanguage
from koalas.directly import DIRECTLY_SOURCE,DIRECTLY_END

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

    @enable_logging
    def __init__(self, traces: Iterable[Trace], 
                 name:str=DEFAULT_SIMPLE_LOG_NAME) -> None:
        # middleman to multi set repr
        self._freqset = dict()
        self._len = 0
        self._variants = 0
        info("Computing language...")
        start = time()
        for trace in traces:
            if (trace in self._freqset.keys()):
                self._freqset[trace] += 1
            else:
                self._freqset[trace] = 1
                self._variants += 1
            self._len += 1
        info(f"Computed language in {(time()-start)*1000:.0f}ms")
        self.name = name 
        self._relations = None

    
    def language(self) -> Set[Trace]:
        "Get a trace language from this language"
        return self._freqset.keys()
    
    def stochastic_language(self) -> Mapping[Trace,float]:
        "Get a stochastic language from this language"
        return self._freqset.copy()

    @enable_logging
    def directly_flow_relations(self) -> FlowLanguage:
        "Get the directly flow relations for this language"
        if (self._relations == None):
            # compute directly flow relations
            self._relations = FlowLanguage([])
            start = time()
            computed_times = []
            info("Starting computation of relations")
            for tid,(trace,freq) in enumerate(self._freqset.items()):
                if (len(trace) < 1):
                    continue
                compute_time = time()
                relations = []
                # build initial flow
                debug(f"{trace=} @ {freq=}")
                debug(f"{DIRECTLY_SOURCE} to {trace[0]=} @ {freq}")
                relations.append(DirectlyFlowsPair(left=DIRECTLY_SOURCE, 
                 right=trace[0], freq=freq))

                # build body flows
                for src,trg in zip(trace[:-1],trace[1:]):
                    debug(f"{src=} to {trg=} @ {freq=}")
                    relations.append(DirectlyFlowsPair(left=src,
                     right=trg, freq=freq))

                # build exit flow 
                debug(f"{trace[-1]=} to {DIRECTLY_END} @ {freq}")
                relations.append(DirectlyFlowsPair(left=trace[-1], 
                 right=DIRECTLY_END, freq=freq))

                # update lang
                self._relations  = self._relations + \
                    FlowLanguage(relations)
                
                if (len(computed_times) < 30):
                    computed_times.append(time() - compute_time)
                else:
                    computed_times.pop(0)
                    computed_times.append(time() - compute_time)

                if (tid > 0 and (tid % 100) == 0):
                    avg_time = (sum(computed_times)/ 
                     len(computed_times))* 1000
                    info(f"computed {tid}/{self._variants} @ " + 
                     f"{avg_time:.1f}ms/variant"
                    )

            # relations computed 
            info(f"Computed relations in {(time()-start)*1000:.0f}ms")
            return self._relations
        else:
            info("Already computed relations, returning existing" + 
             "computation.")
            return self._relations

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


