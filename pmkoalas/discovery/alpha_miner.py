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

from pmkoalas.simple import EventLog
from pmkoalas._logging import info,debug
from pmkoalas.directly import DirectlyFollowPair
from pmkoalas.models.petrinets.pn import LabelledPetriNet, Arc
from pmkoalas.models.petrinets.pn import PetriNetMarking, AcceptingPetriNet
from pmkoalas.discovery.meta import DiscoveryTechnique

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
        formatter = 'AlphaRelation(src="{src}",target="{target}",follows={follows})'
        return formatter.format(src=self.src, target=self.target,
            follows=repr(self._follows)
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
        self.left = deepcopy(left) 
        self.right = deepcopy(right)

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
        ord_left = sorted(list([l for l in self.left]))
        ord_right = sorted(list([r for r in self.right]))
        return hash(
            tuple(["left:"]+[l for l in ord_left]+["right:"]+[r for r in ord_right])
        )

    def __repr__(self) -> str:
        ord_left = sorted([l for l in self.left])
        ord_right = sorted([r for r in self.right])
        left_str = "{" + str(ord_left)[1:-1] + "}"
        right_str = "{" + str(ord_right)[1:-1] + "}"
        return f"AlphaPair({left_str},{right_str})"
    
    def __str__(self) -> str:
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

class AlphaMinerInstance(DiscoveryTechnique):
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

    def __init__(self, min_inst:int=1, optimised:bool=False) -> None:
        self._min_inst = min_inst
        self._matrix = None
        self._opt = optimised

    def mine_footprint_matrix(self, log:EventLog) -> Dict[
        str,Dict[str,AlphaRelation]]:
        """
        Mines the footprint matrix of the alpha miner relations
        between process activities.
        """
        info("Mining footprint matrix...")
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
        info("Footprint matrix mined.")
        return deepcopy(self._matrix)

    def discover(self, log:EventLog) -> AcceptingPetriNet:
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
        info("Discovering Petri net...")
        info("Step one: finding transitions")
        TL = self._step_one(log)
        info("Step one: completed")
        # others 
        info("Step two: finding start activities")
        TI = self._step_two(log)
        info("Step two: completed")
        info("Step three: finding end activities")
        TO = self._step_three(log)
        info("Step three: completed")
        info("Step four: finding pairs")
        XL = self._step_four(log)
        info("Step four: completed")
        info("Step five: finding maximal pairs")
        YL = self._step_five(log, XL)
        info("Step five: completed")
        # find the petri net components 
        ### the set of places
        info("Step six: finding places")
        PL = self._step_six(log, YL) 
        info("Step six: completed")
        ### the set of flow relations
        info("Step seven: finding flow relations")
        FL = self._step_seven(log, PL, TI, TO) 
        info("Step seven: completed")
        info("Petri net discovered.")
        TL = set([ AlphaTransition(t) for t in TL])
        self._matrix = None
        info("Alpha Miner Returning Petri Net")
        from pmkoalas.models.petrinets.pn import Place, Transition, Arc
        places = dict()
        transitions = dict()
        for place in PL:
            places[place.name] = Place(place.name)
        for transition in TL:
            transitions[transition.name] = Transition(transition.name)
        net = LabelledPetriNet(
            set( p for p in places.values()), 
            set(t for t in transitions.values()),
            [Arc(
                places[f.src.name] if 
                isinstance(f.src, AlphaPlace) 
                else transitions[f.src.name],
                places[f.tar.name] if 
                isinstance(f.tar, AlphaPlace) 
                else transitions[f.tar.name],
            )
            for f in FL])
        imark = {}
        fmark = {}
        for place in net.places:
            inc_arcs = set(
                arc 
                for arc in net.arcs 
                if arc.to_node == place
            )
            out_arcs = set(
                arc 
                for arc in net.arcs 
                if arc.from_node == place
            )
            if len(inc_arcs) == 0:
                imark[place] = 1
            if len(out_arcs) == 0:
                fmark[place] = 1
        imark = PetriNetMarking(imark)
        fmark = PetriNetMarking(fmark)
        anet = AcceptingPetriNet(net, imark, [fmark])
        return anet

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
        from joblib import Parallel, delayed
        pool = Parallel(n_jobs=-3,return_as='generator_unordered')
        while last_size != next_size:
            last_size = len(pairs)
            # to expand we do the following for each pair in pairs
            # we check for adding a new left for each pair
            # then check for adding a new right for each pair

            if (self._opt):
                ## optimised path
                # define work for workers
                def work(t:str, pairs:Set[AlphaPair], matrix) -> Set[AlphaPair]:
                    from pmkoalas.discovery.alpha_miner import AlphaPair
                    new_pairs = set()
                    pairs= eval(pairs)
                    for pair in pairs:
                        if (pair.can_add_left(t, matrix)):
                            gen = pair.expand_left(t)
                            if gen not in pairs:
                                new_pairs.add(gen)
                        if (pair.can_add_right(t, matrix)):
                            gen = pair.expand_right(t)
                            if gen not in pairs:
                                new_pairs.add(gen)
                    return repr(new_pairs)
                # expand pairs
                repred_pairs = repr(pairs)
                pool_of_pairs = pool(
                    delayed(work)(t, repred_pairs, self._matrix)
                    for t in TL
                )
                for sync_pairs in pool_of_pairs:
                    info("worker finished expanding...")
                    pairs.update(eval(sync_pairs))
            else:
                new_pairs = set()
                for t in TL:
                    for pair in pairs:
                        if (pair.can_add_left(t, self._matrix)):
                            new_pairs.add(pair.expand_left(t))
                        if (pair.can_add_right(t, self._matrix)):
                            new_pairs.add(pair.expand_right(t))
                pairs.update(new_pairs)
            # update end condition
            next_size = len(pairs)
            info(f"Pairs expanded this round: {next_size - last_size}...")
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

### ------------------- Alpha Miner Plus ------------------- ###

class AlphaPlusRelation(AlphaRelation):
    """
    A helper class to determine the ordering relations that captures
    length-two loops.

    Follows the work of the following article: Alves De Medeiros, A. K., 
    Dongen, van, B. F., Aalst, van der, W. M. P., & Weijters, A. J. M. M. 
    (2004). Process mining : extending the alpha-algorithm to mine short 
    loops.

    The ordering relations are described in Defintion 3.3. of the article.
    """

    def __init__(self, src: str, target: str, follows: List[Tuple[str]] = None) -> None:
        super().__init__(src, target, follows)
        self._two_step_follows = set()
    
    def add_two_step_follows(self, src: str, follow: str) -> None:
        if (src in self._AlphaRelation__members):
            self._two_step_follows.add((src, follow))

    def relation(self) -> AlphaRelationType:
        # check for length two loop relations e.g. aba or bab 
        # check for ab-? then check for aba 
        loop_delta_a = False
        if ((self.src,self.target) in self._follows):
            if (self.target,self.src) in self._two_step_follows:
                loop_delta_a = True
        # check for ba-? then check for bab 
        loop_delta_b = False
        if ((self.target,self.src) in self._follows):
            if (self.src,self.target) in self._two_step_follows:
                loop_delta_b = True
        
        looping = loop_delta_b and loop_delta_a
        # return one of the original alpha relations
        if ((self.src,self.target) in self._follows and 
            (self.target,self.src) in self._follows and
            not looping
        ):
            return AlphaRelationType.PD 
        elif ((self.src,self.target) in self._follows and 
              (
                    (self.target,self.src) not in self._follows
                    or 
                    looping
             )
        ):
            return AlphaRelationType.CD 
        elif ( (self.src,self.target) in self._follows):
            return AlphaRelationType.DF
        return AlphaRelationType.NF

class AlphaMinerPlusInstance(DiscoveryTechnique):
    """
    Mines a Petri net using the alpha miner plus algorithm as presented in
    Alves De Medeiros, A. K., 
    Dongen, van, B. F., Aalst, van der, W. M. P., & Weijters, A. J. M. M. 
    (2004). Process mining : extending the alpha-algorithm to mine short 
    loops.

    The alpha miner plus algorithm is an extension of the alpha miner,
    whereby preprocessing the given log and adjusting the ordering relations
    the alpha-plus miner can mine petri nets with short loops.
    """

    def __init__(self, min_inst:int=1 ,optimised:bool=False) -> None:
        super().__init__()
        self._opt = optimised
        self._min_inst = min_inst

    def mine_footprint_matrix(self, log:EventLog) -> Dict[
        str,Dict[str,AlphaPlusRelation]]:
        """
        Mines the footprint matrix of the alpha miner relations
        between process activities.
        """
        info("Mining footprint matrix...")
        self._matrix = dict()
        TL = self._step_one(log)
        # set up matrix 
        for src in TL:
            self._matrix[src] = dict()
            for target in TL:
                self._matrix[src][target] = AlphaPlusRelation(
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
                        # check for aba in proceeding
                        if src in fpair.proceeding():
                            relation.add_two_step_follows(src, target)
                # test flow relation from target to src
                pair = DirectlyFollowPair(target, src, 1)
                if (flang.contains(pair)):
                    fpair = flang.find(pair)
                    if fpair.frequency() >= self._min_inst:
                        # print(f"adding follows ({target},{src}) to {relation}")
                        relation.add_follows(target, src)
                        # check for bab in proceeding
                        if target in fpair.proceeding():
                            relation.add_two_step_follows(target, src)
        # make new copy
        out = dict()
        for src in TL:
            out[src] = deepcopy(self._matrix[src])
        info("Footprint matrix mined.")
        return deepcopy(self._matrix)
    
    def discover(self, log:EventLog) -> LabelledPetriNet:
        """
        Computes a Petri net to represent the given event log, assuming that
        the event log is a loop-complete workflow log (def 3.1.).

        The algorithm consists of nine steps where the alpha miner alogrithm
        is called but mines ordering relations that capture length-two loops,
        as described in Def. 4.4 of the article.
        """
        from pmkoalas.models.petrinets.pn import Transition,Arc, Place
        self._matrix = None
        _ = self.mine_footprint_matrix(log)
        #step one 
        acts = self._step_one(log)
        #step two 
        doubles = self._step_two(log)
        #step three 
        nots = self._step_three(acts, doubles)
        #step four 
        fdoubles = self._step_four(doubles, nots)
        #step five
        wlog = self._step_five(log, doubles)
        #step six
        net = self._step_six(wlog)
        # return net 
        places = net.places 
        transitions = net.transitions
        ntransitions = set()
        # the ids of the places need to match with the transitions
        # for fun downstream stuff...
        swaps = dict()
        missing = set()
        for f in fdoubles:
            if isinstance(f.from_node,Place) and f.from_node.name not in swaps:
                options = set( 
                    p 
                    for p in places 
                    if p.name == f.from_node.name
                )
                if (len(options) > 0):
                    swaps[f.from_node.name] = options.pop()
                else:
                    missing.add(f.from_node)
            elif isinstance(f.from_node, Transition):
                ntransitions.add(
                    f.from_node
                )
            if isinstance(f.to_node,Place) and f.to_node not in swaps:
                options = set( 
                    p 
                    for p in places 
                    if p.name == f.to_node.name
                )
                if (len(options) > 0):
                    swaps[f.to_node.name] = options.pop()
                else:
                    missing.add(f.to_node)
            elif isinstance(f.to_node, Transition):
                ntransitions.add(
                    f.to_node
                )
        nfdoubles = set()
        for f in fdoubles:
            nfdoubles.add(
                Arc(
                    swaps[f.from_node.name] if f.from_node.name in swaps.keys() 
                    else f.from_node,
                    swaps[f.to_node.name] if f.to_node.name in swaps.keys()
                    else f.to_node
                )
            )
        # now we union the flows
        transitions = transitions.union(ntransitions)
        flows = net.arcs.union(nfdoubles)
        places = places.union(missing)
        net = LabelledPetriNet(
            places, transitions, flows
        )
        imark = {}
        fmark = {}
        for place in net.places:
            inc_arcs = set(
                arc 
                for arc in net.arcs 
                if arc.to_node == place
            )
            out_arcs = set(
                arc 
                for arc in net.arcs 
                if arc.from_node == place
            )
            if len(inc_arcs) == 0:
                imark[place] = 1
            if len(out_arcs) == 0:
                fmark[place] = 1
        net = AcceptingPetriNet(
            net,
            PetriNetMarking(imark),
            [PetriNetMarking(fmark)]
        )
        return net 
    
    def _step_one(self, log:EventLog) -> Set[str]:
        """
        Returns a set of all process activities seen in the 
        event log.
        """
        return log.seen_activities()
    
    def _step_two(self, log:EventLog) -> Set[str]:
        """
        Returns a set of process activities seen in the event, such that there
        exists a trace in the log where ...aa... is seen.
        """
        doubles = set()
        for trace in log.language():
            for i in range(1,len(trace)):
                if (trace[i-1] == trace[i]):
                    doubles.add(trace[i])
        return doubles
    
    def _step_three(self, acts: Set[str], doubles: Set[str]) -> Set[str]:
        """
        Simply returns the set of activities that are not in one-length loops.
        """
        return acts.difference(doubles)
    
    def _step_four(self, doubles:Set[str], nots: set[str]) -> Set['Arc']:
        """
        Returns a set of flow relations that capture the ordering relations
        that capture length-one loops.
        """
        from pmkoalas.models.petrinets.pn import Place,Transition,Arc
        flows = set()
        for t in doubles:
            places_A = set(
                a 
                for a in nots 
                if self._matrix[a][t].relation() == AlphaRelationType.CD
            )
            places_B = set(
                b 
                for b in nots 
                if self._matrix[t][b].relation() == AlphaRelationType.CD
            )
            trans = Transition(t)
            if len(places_A) == 0 and len(places_B) == 0:
                place = AlphaStartPlace()
            else:
                pair = AlphaPair(places_A.difference(places_B), 
                                places_B.difference(places_A)
                )
                place = AlphaPlace(str(pair), pair.left, pair.right)
            place = Place(place.name)
            flows.add(Arc(trans, place))
            flows.add(Arc(place, trans))
        return flows
    
    def _step_five(self, log:EventLog, doubles: set[str]) -> EventLog:
        """
        Returns a new event log where all traces have been processed to remove
        activities that were identified in one-length loops.
        """
        from pmkoalas.simple import Trace
        new_traces = []
        for trace, freq in log.__iter__():
            new_trace = []
            for act in trace:
                if act not in doubles:
                    new_trace.append(act)
            for i in range(freq):
                new_traces.append(Trace(new_trace))
        return EventLog(new_traces)
    
    def _step_six(self, log:EventLog) -> LabelledPetriNet:
        """
        Returns the Petri net discovered by the alpha miner using the alpha
        plus relations.
        """
        miner = AlphaMinerInstance(min_inst=self._min_inst,optimised=self._opt)
        miner.mine_footprint_matrix = self.mine_footprint_matrix
        return miner.discover(log).net
        
    

