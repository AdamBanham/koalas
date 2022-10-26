"""
This modules handles creating directly flows pairs from a 
language.
"""

from tqdm import tqdm

from copy import deepcopy
from time import time
from typing import Iterable,Dict,List,Set
from tempfile import TemporaryFile
from random import randint

from koalas._logging import enable_logging,info,debug


DIRECTLY_SOURCE = "SOURCE"
DIRECTLY_END = "END"

class DirectlyFlowsPair():
    """
    This class describes one directly flow relation between
    two process activities seen in a language.
    """

    def __init__(self,left:str,right:str,freq:int) -> None:
        self._left = left.replace("\n","") 
        self._right = right.replace("\n","")
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
        left = self._left.replace("'","\\'")
        right = self._right.replace("'","\\'")
        return f"DirectlyFlowsPair(left='{left}'"+ \
            f",right='{right}',freq={self._freq})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, DirectlyFlowsPair)):
            return self.__hash__() == __o.__hash__()
        return False

class DirectlyFlowWalk():
    """
    A walk of FlowLanguage, which describes the absolute power of the walk.
    """

    def __init__(self,start:DirectlyFlowsPair) -> None:
        self._pow = start.frequency()
        self._loops = []
        self._nodes = [start.left(), start.right()]
        self._walk = [start.copy()]
        self._hash = hash(tuple([0]))
        self._hash = self._compute_hash()

    def append(self, next:DirectlyFlowsPair) -> object:
        if (next.left() != self._walk[-1].right()):
            raise ValueError("Given pair does not connect to last.")
        if (next.right() in self._nodes):
            self._loops.append(next.copy())
        self._pow += next.frequency()
        self._walk.append(next.copy())
        self._nodes.append(next.right())
        self._hash = self._compute_hash()
        return self

    def power(self) -> float:
        "Return how frequent this walk is."
        return self._pow

    def get(self) -> List[DirectlyFlowsPair]:
        "Return the connected walks of pairs"
        return deepcopy(self._walk)

    def last(self) -> DirectlyFlowsPair:
        "Returns the last seen pair in the walk."
        return self._walk[-1].copy()

    def should_cross(self, next:DirectlyFlowsPair) -> bool:
        "Returns if the walks should cross this path."
        if (next in self._loops):
            return False 
        return len([ p for p in self._walk if p == next]) <= 2

    def check_membership(self, checkfor:DirectlyFlowsPair) -> bool:
        "Check if this walk has crossed this pair before."
        return checkfor in self._walk

    def copy(self):
        "Returns a new instance of this walk"
        return deepcopy(self)

    def _compute_hash(self):
        return hash(tuple(
            [ 
                self._hash,
                self._walk[-1].__hash__(),
                self._pow
            ]
        ))

    # data model functions
    def __str__(self) -> str:
        repr = f"{self._walk[0].left()} -> {self._walk[0].right()}"
        for step  in self._walk[1:]:
            repr += f" -> {step.right()}"
        return repr

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, DirectlyFlowWalk)):
            return self.__hash__() == __o.__hash__()
        return False

    def __repr__(self) -> str:
        repr = f"DirectlyFlowWalk({self._walk[0].__repr__()})"
        for pair in self._walk[1:]:
            repr += f".append({pair.__repr__()})"
        return repr 

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
        self._walks = None
        self._pairs = 0
        start = time()
        debug("Computing new flow language")
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
        debug("Computed new flow language in" +
         f" {(time() - start)*1000:.1f}ms")
        debug(f"Computed :: {str(self)}")

    def _introduce_pairs(self, pairs: List[DirectlyFlowsPair]):
        """
        Internal function to update a state spaces with new paris.
        """
        start = time()
        debug("Computing new flow language")
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
        debug(f"Computed new flow language in {(time() - start)*1000:.1f}ms")
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
        "Returns all starting directly flow pairs."
        return list(self._starts.values())

    def ends(self) -> List[DirectlyFlowsPair]:
        "Returns all ending directly flow pairs."
        return list(self._ends.values())

    def get(self, target:DirectlyFlowsPair) -> List[DirectlyFlowsPair]:
        "Returns all pairs with left as target."
        relations = list()
        for pair in self:
            if (pair.left() == target):
                relations.append(pair)
        return relations

    @enable_logging
    def approx_walks(self, attempts:int=10000) -> List[DirectlyFlowWalk]:
        """
        Returns approximates walks from flow language based on frequency.
        Return list of walks will be unique but may not cover all directly flows
        relations. 
        """
        finished = set()
        starts = self.starts()
        ends= self.ends()
        starts.sort(key=lambda x: x.frequency())
        sfreq = [ (s,sum([ ss.frequency() for ss in starts[:i]])) 
         for i,s in enumerate(starts) ]
        info("approximating walks...")
        start = time()
        for attempt in range(attempts):
            # coin flip on starting point
            flip = randint(0, sfreq[-1][-1])
            walk = None
            for starting,chance in sfreq:
                if (flip <= chance):
                    walk = DirectlyFlowWalk(starting)
                    break
            failed = False
            # begin flipping and choosing
            while (not failed and walk.last() not in ends):
                # get next steps
                poss = [ pair for pair in self.get(walk.last().right()) 
                     if walk.should_cross(pair) ]
                if (len(poss) < 1):
                    failed = True
                    continue
                # flip between choices
                poss.sort(key=lambda x: x.frequency())
                nextsfreq = [ 
                    (s,sum([ss.frequency() for ss in poss[:i]])) for i,s 
                    in enumerate(poss)
                ]
                # 
                flip = randint(0,nextsfreq[-1][-1])
                for succ,chance in nextsfreq:
                    if (flip <= chance):
                        walk = walk.append(succ)
                        break

            # add to approximates
            if (not failed):
                finished.add(walk)

            if attempt > 0 and (attempt % 1000) == 0:
                info(f"Completed {attempt}/{attempts} attempts...")

        info(f"finished approximation in {(time() - start)*1000:.1f}ms")
        info(f"found {len(finished)} walks while approximating...")
        return finished


    @enable_logging
    def walks(self) -> List[DirectlyFlowWalk]:
        """Returns all walks possible in the language. Warning may not finish 
        compute in finite time or in finite memory. """
        # check computation
        if (self._walks == None):
            info("computing walks...")
            start = time()
            # init ques 
            finished = []
            seen = SetArray()
            que = QuequeContainer() 
            deadlocks = False
            deadlock_count = 0
            # add starting points
            for pair in self.starts():
                walker = DirectlyFlowWalk(pair)
                que.append(walker)
            # iterative build walks
            info(f"starting que size {len(que)}...")
            while len(que) > 0:
                nque = QuequeContainer()
                for walk in tqdm(que):
                    # is walk at the end of the language
                    if (walk.last() in self.ends()):
                        finished.append(walk)
                        continue
                    # get possible pairs to expand to
                    poss = [ pair for pair in self.get(walk.last().right()) 
                     if walk.should_cross(pair) ]
                    if (len(poss) < 1):
                        deadlocks = True
                        deadlock_count += 1
                        debug("closing walk before reaching end :: " + str(walk))
                    # create new walks
                    for next_pair in poss:
                        nwalk = walk.copy()
                        nwalk.append(next_pair)
                        if (nwalk.__hash__() not in seen):
                            nque.append(nwalk)
                            seen.add(nwalk.__hash__())
                # start next cycle
                que = nque
                info(f"cycled que size {len(que)}...")
            # save computed walks
            info(f"finished computing a toal of {len(finished)} walks...")
            info(f"computation took {(time() -start)*1000:.1f}ms")
            if (deadlocks):
                info(f"numbder of deadlocks seen :: {deadlock_count}")
            else:
                info("No deadlocks occured during computation")
            finished.sort(reverse=True,key=lambda x: x.power())
            self._walks = finished
        return self._walks
    
    def activities(self) -> Set[str]:
        "Returns all activities seen in the language"
        return self._activities - set([DIRECTLY_END,DIRECTLY_SOURCE])


    # data model functions
    def __add__(self, other:object) -> object:
        if (isinstance(other, FlowLanguage)):
            new_flang = deepcopy(self)
            new_flang._introduce_pairs(other._relations.values())
            return new_flang
        raise NotImplemented("Flow language addition not support with" +\
             f" :: {type(other)}")

    def __iter__(self) -> Iterable[DirectlyFlowsPair]:
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
            repr += f"{str(pair.__repr__())},\n\t"
        repr += "])"
        return repr

class SetArray():
    """
    An alternative storage instances for large sets. Only defines add and 
    membership.
    """

    def __init__(self,tmpsize=100000) -> None:
        self._members = [set()]
        self._max_size = tmpsize
        self._curr_size = 0 
        self._curr_set = self._members[-1]

    def add(self, item):
        if (item not in self):
            self._curr_size += 1
            self._curr_set.add(item)
            if (self._curr_size >= self._max_size):
                self._members.append(set())
                self._curr_set = self._members[-1]
                self._curr_size = 0

    def __contains__(self, item) -> bool:
        check = False 
        for setter in self._members:
            check = check or item in setter 
        return check


class QuequeContainer():
    """
    A alternative storage of things, with a set size of items to be stored in
    memory. Expects that items have a accurate representation via __repr__.
    """

    def __init__(self, hash:bool=False, tmpsize=10000) -> None:
        self._temp_hdrive = TemporaryFile()
        self._use_hashes = hash
        self._temp_lines = 0
        self._tmpsize = tmpsize
        self._storage = [ None for _ in range(self._tmpsize)]
        self._storage_used = 0

    def append(self, item:object):
        # if there is a slot free in memory then use it
        if (self._storage_used < self._tmpsize):
            self._storage[self._storage_used] = item 
            self._storage_used += 1
        else: 
            # otherwise flush content to file
            self._temp_hdrive.write(b'[')
            for sitem in self._storage:
                if (self._use_hashes):
                    self._temp_hdrive.write(sitem.__hash__().encode("UTF-8")) 
                else:
                    self._temp_hdrive.write(sitem.__repr__().encode("UTF-8"))
                self._temp_hdrive.write(b',')
                self._temp_lines += 1
            self._temp_hdrive.write(b']\n')
            self._temp_hdrive.flush()
            # then repopulate slots in memory
            self._storage_used = 0
            self._storage = [ None for _ in range(self._tmpsize)]
            self._storage[self._storage_used] = item 
            self._storage_used += 1
            
    
    def __iter__(self) -> Iterable[object]:
        # loop through storage
        for item in self._storage[:self._storage_used]:
            yield item 
        # loop through dumps in file if need
        if (self._temp_lines > 0):
            # flush file and return to start
            self._temp_hdrive.flush()
            old_index = self._temp_hdrive.tell()
            self._temp_hdrive.seek(0)
            # get a block and compute full list
            for bytes in self._temp_hdrive:
                items = eval(bytes)
                # yield item from block
                for item in items:
                    yield item
            # reset file seek in case of further appending
            self._temp_hdrive.seek(old_index)

    def __len__(self) -> int :
        return self._storage_used + self._temp_lines