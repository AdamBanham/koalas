"""
This module is a implementation of the alpha miner (original).

See the following article for more information about the 
alpha miner process discovery technique:\n
W.M.P. van der Aalst, A.J.M.M. Weijters, and L. Maruster. 
Workflow Mining: Discovering Process Models from Event Logs. 
IEEE Transactions on Knowledge and Data Engineering,
16(9):1128–1142, 2004.
"""
from typing import Set,Tuple,Dict,List,Union
from enum import Enum
from copy import deepcopy,copy

from koalas.simple import EventLog
from koalas.directly import DirectlyFollowPair

class AlphaRelationType(Enum):
    DF = ">"
    CD = "->"
    NF = "#"
    PD = "||"

class AlphaRelation():
    """
    A helper data class to work out what relation is suitable
    for a row, column in the footprint matrix for the alpha
    miner.

    Supported Relations:
    --------------------
    >  : directly follows\n
    -> : causal dependency\n
    \# : never follows\n
    || : parallel dependency\n
    """

    def __init__(self, src:str, target:str, follows:List[Tuple[str,str]]=None) -> None:
        self.target = target
        self.src = src
        self._follows = [] if follows == None else follows
        self.__members = [src, target]
        self.__hash = hash((target,src))

    def add_follows(self, src:str, follow:str) -> None:
        if (src in self.__members and follow in self.__members):
            self._follows.append((src,follow))

    def relation(self) -> AlphaRelationType:
        "returns the alpha relation between src and target"
        if ((self.src,self.target) in self._follows and 
            (self.target,self.src) in self._follows
        ):
            return AlphaRelationType.PD 
        elif ((self.src,self.target) in self._follows and 
              (self.target,self.src) not in self._follows
        ):
            return AlphaRelationType.CD 
        elif ( (self.src,self.target) in self._follows):
            return AlphaRelationType.DF
        return AlphaRelationType.NF

    # data model functions
    def __str__(self) -> str:
        formatter = "({src} {relation} {target})"
        return formatter.format(src=self.src, target=self.target,
            relation=self.relation().value
        )

    def __repr__(self) -> str:
        formatter = 'AlphaRelation(src="{src}",target="{target}",follow={follows})'
        return formatter.format(src=self.src, target=self.target,
            follows=self._follows
        )

    def __hash__(self) -> int:
        return self.__hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, AlphaRelation)):
            return __o.__hash__() == self.__hash__()
        return False

class AlphaPair():
    """
    Data class helper for place generation.
    """

    def __init__(self, left:Set, right:Set) -> None:
        self.left = left 
        self.right = right 
        ord_left = sorted(list([l for l in left]))
        ord_right = sorted(list([r for r in right]))
        self.__hash = hash(
            tuple([l for l in ord_left] + [r for r in ord_right])
        )

    def can_add_left(self, add:str, 
        matrix:Dict[str,Dict[str,AlphaRelation]]) -> bool:
        "Checks if we can add new input transition"
        # check that add is unseen
        if (add in self.left):
            return False
        # check for cd between new left and old rights
        for right in self.right:
            relation = matrix[add][right]
            if (relation.relation() != AlphaRelationType.CD):
                return False
        # check for nf between add and old lefts
        for left in self.left:
            relation = matrix[add][left]
            if (relation.relation() != AlphaRelationType.NF):
                return False
        return True

    def can_add_right(self, add:str, 
        matrix:Dict[str,Dict[str,AlphaRelation]]) -> bool:
        "Checks if we can add new output transition"
        # check that add is unseen
        if (add in self.right):
            return False
        # check for cd between old lefts to new right
        for left in self.left:
            relation = matrix[left][add]
            if (relation.relation() != AlphaRelationType.CD):
                return False
        # check for nf between add and old rights
        for right in self.right:
            relation = matrix[add][right]
            if (relation.relation() != AlphaRelationType.NF):
                return False
        return True

    def expand_left(self, add:str) -> 'AlphaPair':
        "Creates new pair with expanded left, using given add."
        new_left = deepcopy(self.left)
        new_left.add(add)
        new_right = deepcopy(self.right)
        return AlphaPair(new_left, new_right)

    def expand_right(self, add:str) -> 'AlphaPair':
        "Creates new pair with expanded right, using given add."
        new_left = deepcopy(self.left)
        new_right = deepcopy(self.right)
        new_right.add(add)
        return AlphaPair(new_left, new_right)

    def issubset(self, other:'AlphaPair') -> bool:
        "Checks if other implies this pair"
        if (not self.left.issubset(other.left)):
            return False 
        if (not self.right.issubset(other.right)):
            return False 
        return True

    def __hash__(self) -> int:
        return self.__hash

    def __repr__(self) -> str:
        ord_left = sorted([l for l in self.left])
        ord_right = sorted([r for r in self.right])
        left_str = "{" + str(ord_left)[1:-1] + "}"
        right_str = "{" + str(ord_right)[1:-1] + "}"
        return f"({left_str},{right_str})"

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, AlphaPair)):
            return __o.__hash__() == self.__hash__()
        return False

class AlphaPlace():
    """
    Data class helper for managing places generated from alpha miner.
    """

    def __init__(self, suffix:str, incoming:Set[str], 
        outgoing:Set[str]) -> None:
        self.name = "P_"+suffix
        self.incoming = deepcopy(incoming)
        self.outgoing = deepcopy(outgoing)
        self.__hash = hash(
            tuple(inc for inc in sorted(list(self.incoming)))
            + tuple(out for out in sorted(list(self.outgoing)))
        )
    
    def __hash__(self) -> int:
        return self.__hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, AlphaPlace)):
            return __o.__hash__() == self.__hash__()
        return False 

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

class AlphaStartPlace(AlphaPlace):
    """
    Special case for starting place in alpha miner.
    """

    ALPHA_START_HASH = "THISISTHEINITIALPLACE"

    def __init__(self) -> None:
        super().__init__("initial", set(), set())

    def __hash__(self) -> int:
        return hash(tuple(self.ALPHA_START_HASH))

class AlphaSinkPlace(AlphaPlace):
    """
    Special case for sink place in alpha miner.
    """

    ALPHA_END_HASH = "THISISTHESINKPLACE"

    def __init__(self) -> None:
        super().__init__("sink", set(), set())

    def __hash__(self) -> int:
        return hash(tuple(self.ALPHA_END_HASH))

class AlphaTransition():
    """
    Data class helper for managing transitions generated from
    alpha miner.
    """

    def __init__(self,name:str) -> None:
        self.name = name
        self.__hash = hash(tuple(name))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return self.__hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, AlphaTransition)):
            return self.__hash__() == __o.__hash__()
        return False
    
class AlphaFlowRelation():
    """
    Data class helper for managing flow relations generated
    from alpha miner.
    """

    def __init__(self,suffix:str, 
        src:Union[AlphaPlace,AlphaTransition],
        tar:Union[AlphaPlace,AlphaTransition]) -> None:
        self.name = "F_"+suffix
        self.src = src 
        self.tar = tar 
        self.__hash = hash(tuple([src,tar]))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.src} -> {self.tar}"

    def __hash__(self) -> int:
        return self.__hash

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, AlphaFlowRelation)):
            return self.__hash__() == __o.__hash__()
        return False

class AlphaMinerInstance():
    """
    This is a helper for the alpha miner using the same 
    parameters. The alpha miner consists of several steps,
    which each steps finds a finite set defined by an event 
    log. The alpha miner algorithm returns the components 
    needed to defined a Petri net, i.e. a set of places, a 
    set of transitions, and a set of flow relations.
    \n
    step one: find the set of transitions (process activities)\n
    step two: find the set of start activities\n
    step three: find the set of end activities\n
    step four: determine all possible places for the net\n
    step five: determine the maximal pairs for the net\n
    step six: \n
    step seven: \n
    \n
    The alpha miner has the following parameters:\n
    Parameters
    ----------    
    min_inst:`int=1`(default)\n
    The minimum number of times a relation must be seen to
    be counted as a alpha relation.
    """

    def __init__(self, min_inst:int=1):
        self._min_inst = min_inst
        self._matrix = None

    def mine_footprint_matrix(self, log:EventLog) -> Dict[
        str,Dict[str,AlphaRelation]]:
        """
        Mines the footprint matrix of the alpha miner relations
        between process activities.
        """
        self._matrix = dict()
        TL = self._step_one(log)
        # set up matrix 
        for src in TL:
            self._matrix[src] = dict()
            for target in TL:
                self._matrix[src][target] = AlphaRelation(
                    src=src,target=target
                )
        # find directly flows lang
        flang = log.directly_follow_relations()
        # update relations
        for col in self._matrix.values():
            for relation in col.values():
                src = relation.src
                target = relation.target
                # test flow relation from src to target
                pair = DirectlyFollowPair(src, target, 1)
                if (flang.contains(pair)):
                    fpair = flang.find(pair)
                    if fpair.frequency() >= self._min_inst:
                        # print(f"adding follows ({src},{target}) to {relation}")
                        relation.add_follows(src, target)
                # test flow relation from target to src
                pair = DirectlyFollowPair(target, src, 1)
                if (flang.contains(pair)):
                    fpair = flang.find(pair)
                    if fpair.frequency() >= self._min_inst:
                        # print(f"adding follows ({target},{src}) to {relation}")
                        relation.add_follows(target, src)
        # make new copy
        out = dict()
        for src in TL:
            out[src] = deepcopy(self._matrix[src])
        return deepcopy(self._matrix)

    def mine_model(self, log:EventLog) -> Tuple[Set,Set,Set]:
        """
        Mines a petri net based on the given event log, using
        the alpha miner discovery technique.

        Returns a Petri net, i.e. a set of places, a set of 
        transitions and a set of flow relations.
        """
        self._matrix = None
        # find the essential elements 
        matrix = self.mine_footprint_matrix(log)
        ### the set of transitions
        TL = self._step_one(log)
        # others 
        TI = self._step_two(log)
        TO = self._step_three(log)
        XL = self._step_four(log)
        YL = self._step_five(log, XL)
        # find the petri net components 
        ### the set of places
        PL = self._step_six(log, YL) 
        ### the set of flow relations
        FL = self._step_seven(log, PL, TI, TO) 
        TL = set([ AlphaTransition(t) for t in TL])
        self._matrix = None
        return (PL, TL, FL)

    def _step_one(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all process activities seen in the 
        event log.
        """
        return log.seen_activities()

    def _step_two(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all start process activities seen in 
        the event log.
        """
        return log.seen_start_activities()

    def _step_three(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all end process activities seen in 
        the event log.
        """
        return log.seen_end_activities()

    def _step_four(self, log:EventLog) -> Set:
        """
        Returns a set of pairs, where each pair describes a 
        set of transitions that have a causal dependency (->) 
        with all the transitions in the second set. Futhermore, 
        each member of each set, is never seen follows (#) 
        another member from their set.
        """
        if (self._matrix == None):
            self._matrix = self.mine_footprint_matrix(log)
        pairs:Set[AlphaPair] = set()
        # build all pair iteratively, start within |A| = 1
        TL = self._step_one(log)
        for src in TL:
            col = self._matrix[src]
            # check that src has never follows with itself
            if (col[src].relation() != AlphaRelationType.NF):
                continue
            for tar in TL:
                relation = col[tar]
                # check for casual dependency
                if (relation.relation() == AlphaRelationType.CD):
                    # add to base
                    pairs.add( 
                        AlphaPair(set([src]),set([tar]))
                    )
        # keep expanding until pairs does not grow
        last_size = 0
        next_size = len(pairs)
        while last_size != next_size:
            last_size = len(pairs)
            # to expand we do the following for each pair in pairs
            # we check for adding a new left for each pair
            # then check for adding a new right for each pair
            new_pairs = deepcopy(pairs)
            for t in TL:
                for pair in pairs:
                    if (pair.can_add_left(t, self._matrix)):
                        new_pairs.add(pair.expand_left(t))
                    if (pair.can_add_right(t, self._matrix)):
                        new_pairs.add(pair.expand_right(t))
            pairs.update(new_pairs)
            # update end condition
            next_size = len(pairs)
        return pairs

    def _step_five(self, log:EventLog, XL:Set) -> Set:
        """
        Returns all maximal pairs from XL, reducing the number
        of places in the Petri net.
        """
        maximal_pairs = set()
        for pair in XL:
            issubset = False
            for opair in XL:
                if pair == opair:
                    continue 
                issubset = issubset or pair.issubset(opair)
                if (issubset):
                    break
            if (not issubset):
                maximal_pairs.add(deepcopy(pair))
        return maximal_pairs 

    def _step_six(self, log:EventLog, YL:Set[AlphaPair]) -> Set:
        """
        Returns a set of alpha places for the Petri net, including 
        an initial place and a sink place.
        """
        places = set()
        for y in YL:
            places.add(AlphaPlace(str(y), y.left, y.right))
        places.add(AlphaStartPlace())
        places.add(AlphaSinkPlace())
        return places

    def _step_seven(self, log:EventLog, PL:Set[AlphaPlace], 
        TI:Set[str], TO:Set[str]) -> Set:
        """
        Returns a set of alpha flow relations, which are directed
        arcs from source to some target.
        """
        flows = set()
        for place in PL:
            if isinstance(place, AlphaSinkPlace):
                for out in TO:
                    flows.add(AlphaFlowRelation(str(len(flows)+1), 
                        AlphaTransition(out),
                        place
                    )) 
            elif isinstance(place, AlphaStartPlace):
                for inc in TI:
                    flows.add(AlphaFlowRelation(str(len(flows)+1), 
                        place,
                        AlphaTransition(inc)
                    )) 
            else:
                for inc in place.incoming:
                    flows.add(AlphaFlowRelation(str(len(flows)+1),
                        AlphaTransition(inc),
                        place 
                    ))
                for out in place.outgoing:
                    flows.add(AlphaFlowRelation(str(len(flows)+1),
                        place, 
                        AlphaTransition(out)
                    ))
        return flows

    