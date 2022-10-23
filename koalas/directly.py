"""
This modules handles creating directly flows pairs from a 
language.
"""

from time import time
from typing import Iterable,Dict,List

from koalas._logging import enable_logging,info,debug


DIRECTLY_SOURCE = "SOURCE"
DIRECTLY_END = "END"

class DirectlyFlowsPair():
    """
    This class describes one directly flow relation between
    two process activities seen in a language.
    """

    def __init__(self,left:str,right:str,freq:int) -> None:
        self._left = left 
        self._right = right
        self._hash = hash((self._left,self._right))
        self._freq = freq

    def left(self) -> str:
        "Source process activity"
        return self._left
    
    def right(self) -> str:
        "Target process activity"
        return self._right

    def frequency(self) -> int:
        "Support for flow relation"
        return self._freq

    def incre(self,count:int=1) -> None:
        "Increase support for relation"
        self._freq += count 

    def decre(self,count:int=1) -> None:
        "Decrease support for relation"
        self._freq -= count
    
    def copy(self) -> object:
        return DirectlyFlowsPair(self._left, self._right, self._freq)

    # data model functions
    def __str__(self) -> str:
        return f"({self._left} -> {self._right})^{self._freq}"

    def __repr__(self) -> str:
        return f"DirectlyFlowsPair(left={self._left}"+\
            f",right={self._right},freq={self._freq})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, DirectlyFlowsPair)):
            return self.__hash__() == __o.__hash__()
        return False

class FlowLanguage():
    """
    A language of directly flow relations.
    """

    def __init__(self, pairs:Iterable[DirectlyFlowsPair]) -> None:
        self._relations = {}
        self._starts = {}
        self._ends = {}
        self._froms = {}
        self._tos = {}
        self._activities = set()
        self._pairs = 0
        start = time()
        info("Computing new flow language")
        for pair in pairs:
            self._activities.add(pair.left())
            self._activities.add(pair.right())
            # add to general collection
            self._update_state(pair,self._relations, "collection")
            # add to starts if needed
            if (pair.left() == DIRECTLY_SOURCE):
                self._update_state(pair,self._starts, "starts")
            # add to ends if needed
            if (pair.right() == DIRECTLY_END):
                self._update_state(pair,self._ends, "ends")
        self._pairs = len(self._relations.items())
        info(f"Computed new flow language in {(time() - start)*1000:.1f}ms")
        debug(f"Computed :: {str(self)}")

    def _update_state(self, pair:DirectlyFlowsPair, state:Dict, state_name:str):
        """
        Internal function to update a state space with a pair.
        A pair may be used differently in each state space, so
        always take a copy.
        """
        val = state.get(pair,None)
        # check if flow already is recorded
        debug(f"{state_name} :: existing flow? {str(val)=}")
        if (val != None):
            newval = val.copy()
            newval.incre(pair.frequency())
            debug(f"{state_name} :: update : {val}")
            state[newval] = newval
        else:
            debug(f"{state_name} :: added : {pair}")
            state[pair] = pair.copy()

    def starts(self) -> List[DirectlyFlowsPair]:
        "Returns all starting directly flow pairs"
        return self._starts.values()

    def ends(self) -> List[DirectlyFlowsPair]:
        "Return all ending directly flow pairs"
        return self._ends.values()

    # data model functions
    def __add__(self, other:object) -> object:
        if (isinstance(other, FlowLanguage)):
            relations = list(self._relations.values()) \
                + list(other._relations.values())
            return FlowLanguage(relations) 
        raise NotImplemented("Flow language addition not support with" +\
             f" :: {type(other)}")

    def __iter__(self) -> DirectlyFlowsPair:
        for pair in self._relations.values():
            yield pair

    def __len__(self) -> int:
        return self._pairs

    def __str__(self) -> str:
        rep = ""
        for pair in self._relations.values():
            rep += str(pair)
        return rep

    def __repr__(self) -> str:
        repr = "FlowLanguage([\n\t"
        for pair in self._relations.values():
            rep += f"{str(pair.__repr__())}\n\t"
        repr += "])"


