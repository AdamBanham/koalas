"""
This module contains an alignment like process for transition trees, called 
matchings.
"""
from typing import Any, Union, Dict, List, Set, Iterable, Tuple
from copy import deepcopy

from joblib import Parallel, delayed

from pmkoalas.models.transitiontree import TransitionTreeFlow
from pmkoalas.models.transitiontree import TransitionTree
from pmkoalas.models.transitiontree import TransitionTreeVertex
from pmkoalas.simple import Trace, EventLog
from pmkoalas.complex import ComplexEventLog
from pmkoalas._logging import info, InfoIteratorProcessor,InfoQueueProcessor
from pmkoalas._logging import debug

class Skipper():
    """
    A dummy class for the skip symbol in matchings, i.e. ">>"
    """

    def __str__(self) -> str:
        return ">>"
    
    def __repr__(self) -> str:
        return "Skipper()"
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: object) -> bool:
        return type(self) == type(other)

class Path():
    """
    A sequence of interconnected flows and/or skips within a tree. 
    """

    def __init__(self, sequence:List[Union[Skipper,'TransitionTreeFlow']]) \
        -> None:
        self._seq = deepcopy(sequence)

    @property
    def sequence(self) -> List[Union[Skipper,'TransitionTreeFlow']]:
        return deepcopy(self._seq)
    
    @property
    def noskips(self) -> List['TransitionTreeFlow']:
        ret = []
        for p in self._seq:
            if not isinstance(p, Skipper):
                ret.append(deepcopy(p))
        return ret
    
    def __iter__(self) -> Iterable[Union[Skipper, TransitionTreeFlow]]:
        for s in self._seq:
            yield s
    
    def __str__(self) -> str:
        ret = "< "
        for s in self.sequence:
            add = ""
            if (isinstance(s,TransitionTreeFlow)):
                add = s.activity()
            else:
                add = str(s)
            ret += add + ","
        return ret[:-1] + " >"
    
    def __hash__(self) -> int:
        return hash(tuple(self.sequence))
    
    def __eq__(self, other: object) -> bool:
        if (type(self) == type(other)):
            return self.__hash__() == other.__hash__()
        return False
    
    def __len__(self) -> int:
        return len(self._seq)

class Matching():
    """
    A mapping data structure, which maps variants to a path in a tree.
    """

    def __init__(self, mapping:Dict[Trace,Path]):
        self._map = deepcopy(mapping) 

    def add_to_map(self, trace:Trace, path:Path) -> None:
        """
        Either adds a new variant to the mapping or swaps an existing mapping
        with the given trace and path.
        """
        self._map[trace] = path

    def __getitem__(self, trace:Trace) -> Union[Path,None]:
        if trace in self._map:
            return deepcopy(self._map[trace])
        else:
            return None
        
class ManyMatching(Matching):
    """
    A mapping data structure, which maps traces to a set of paths in a tree.
    """

    def __init__(self, mapping:Dict[Trace,Set[Path]]):
        super().__init__(mapping)

    def add_to_map(self, trace:Trace, paths:Union[Path,Set[Path]]) -> None:
        """
        Either introduces a new trace into the mapping or updates the existing
        mapping to a trace with given path/s.
        """
        if (trace not in self._map):
            self._map[trace] = set()
            if isinstance(paths, Path):
                self._map[trace].add(paths)
            else:
                self._map[trace] = paths 
        else:
            old_set = self._map[trace]
            if isinstance(paths, Path):
                old_set.add(paths)
            else:
                old_set = old_set.union(paths)

    def __getitem__(self, trace: Trace) -> Union[Set[Path], None]:
        return super().__getitem__(trace)
    
def find_path_in_tree(tree:TransitionTree, tgt:TransitionTreeVertex)\
    -> Path:
    """
    Constructs a path from the root to the given node in a tree.
    """
    seq = []
    breakdown = Trace([])
    goal = tgt.sigma_sequence().sequence
    while breakdown != tgt.sigma_sequence():
        step = Trace(breakdown.sequence + [goal.pop(0)])
        found = False
        for flow in tree.flows():
            if flow.offering().sigma_sequence() == breakdown:
                if flow.next().sigma_sequence() == step:
                    seq.append(flow)
                    breakdown = step 
                    found = True 
                    break 
        if (not found):
            raise ValueError("Unable to find a interconnected "\
                             +"sequence of flows.")
    return Path(seq)

def mutate_path_with_skips(path:Path, k:int) -> Set[Path]:
    """
    Constructs all mutations of the path with additional skips of at most
    length k.
    """
    
    if (len(path) > k):
        return set()
    elif len(path) == k:
        return set([path])
    else:
        ret = set()
        adding = set([path])
        log_que = InfoQueueProcessor("mutation size",1)
        while len(adding) > 0:
            mutaters = adding
            ret = ret.union(adding)
            adding = set()
            for muter in mutaters:
                info(f"mutating :: {muter}")
                for i in range(len(muter)+1):
                    spath = muter.sequence[:i] + [Skipper()] + muter.sequence[i:]
                    spath = Path(spath)
                    if (len(spath) <= k) and spath not in ret:
                        adding.add(spath)
                        info(f"adding new path to mutations :: {spath}")
                        log_que.extent(1)
                log_que.update(1)
        return ret

def find_all_paths(tree:TransitionTree, k:int) -> Set[Path]:
    """
    Finds all paths through or in the tree, for a given length.
    """
    seen_paths = set()
    # construct all paths to nodes of at most length k
    nodes = [ v for v in tree.vertices() if len(v.sigma_sequence()) <= k]
    complete_paths = [ find_path_in_tree(tree,n) for n in nodes]
    seen_paths = seen_paths.union(set(complete_paths))
    # constuct all paths with skips 
    for path in InfoIteratorProcessor("computing all mutations", 
                                      [ path for path in complete_paths ]):
        mutate = mutate_path_with_skips(path, k)
        seen_paths = seen_paths.union(mutate)
    return seen_paths

def cost_of_path(path:Path, trace:Trace, root_is_terminal:bool=False) -> int:
    """
    Computes of the cost of the path in the context of the given trace.
    An optimal path for a trace has a cost of zero, while a non-optimal
    path has a cost greater than zero.
    """
    len_cost = abs(len(trace) - len(path.noskips))
    act_cost = 0
    for act, actf in zip(trace, path):
        if isinstance(actf, Skipper):
            act_cost += 1
        else:
            act_cost += 0 if act == actf.activity() else 1
    if (len(path.noskips) > 0 ):
        term_cost = 0 if path.noskips[-1].next().terminal() else 1
    else:
        term_cost = 0 if root_is_terminal else 1
    return len_cost + act_cost + term_cost

def find_least_costy_paths(paths:Set[Path], trace:Trace, 
        root_is_terminal:bool=False) -> set[Path]:
    """
    Finds the subset of the given paths that are least costy.
    """
    ret = set()
    costing = dict( 
        (path, cost_of_path(path, trace, root_is_terminal=root_is_terminal))
        for path 
        in paths
    )
    ideal = -1
    while len(ret) == 0:
        ideal += 1
        ret = set()
        for path,cost in costing.items():
            if cost == ideal:
                ret.add(path) 
    return ret 
    
class ExpontentialPathWeighter():
    """
    A weighting function, that weights candidates with exponential offset for,
    non-optimal paths, between a path and a trace.
    """
    # offset cost
    kappa = 0.9

    def __init__(self, candidates:Set[Path]) -> None:
        self._cands = deepcopy(candidates)
        self._size = len(self._cands)

    def __call__(self, path:Path, trace:Trace) -> float:
        debug(f"computing weight for path {path} and trace {trace}")
        if path in self._cands:
            cost = cost_of_path(path, trace)
            debug(f"cost of path was {cost}")
            share = 1 / self.size
            offset = self.kappa ** cost
            debug(f"offset was {offset}, return {share * offset}")
            return share * offset
        else:
            return 0
    
    @property
    def size(self) -> int:
        return self._size
    
    @property
    def share(self) -> float:
        """
        The maximum share that a path can be given
        """
        return 1 / self.size
        
def _computation_many_matching(trace, tree, allcads) -> Tuple[Trace,Set[Path]]:
    """
    The individual work for a given trace, to find a matching.
    """
    # noskips = find_non_skipping_candidates(tree, trace)
    # skippings = find_skipping_candidates(tree,trace)
    # terminals = find_terminal_candidates(tree,trace)
    if len(allcads) > 0:
        least_costy = find_least_costy_paths(
            allcads,
            trace,
            root_is_terminal=tree.root() in tree.terminals()
        )
    else: 
        raise Exception(f"Unable to find any candidates for :: {trace}")
    cost = 0
    for path in least_costy:
        cost = cost_of_path(path, trace)
        break
    info(f"for trace {trace}, we found {len(least_costy)} paths of cost={cost}")
    return (trace, least_costy)

def construct_many_matching(log:Union[EventLog,ComplexEventLog], 
                            tree:TransitionTree) \
     -> ManyMatching:
    """
    Constructs a set of likely cadidate paths for each trace in the log,
    then constructs a map from traces to these sets.
    """
    mapping = ManyMatching(dict())
    max_length = max(
        [len(trace) for trace,_ in log]
    )
    allcads = find_all_paths(tree, max_length+1)
    rets = Parallel(n_jobs=-2)(
        delayed(_computation_many_matching)(trace,tree,allcads)
        for trace,allcads
        in InfoIteratorProcessor(
            "matchings", 
            [ (trace,set([ cad for cad in allcads if len(cad) <= len(trace)]))
             for trace,_ in log ]
            ,stack=8)
    )
    for trace,least_costy in rets:
        info(f"no. of matching generated for {trace} was {len(least_costy)}")
        mapping.add_to_map(trace, least_costy)
    return mapping

