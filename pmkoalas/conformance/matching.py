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
from pmkoalas._logging import info, InfoIteratorProcessor

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
    A mapping data structure, which maps traces to a path in a tree.
    """

    def __init__(self, mapping:Dict[Trace,Path]):
        self._map = deepcopy(mapping) 

    def add_to_map(self, trace:Trace, path:Path) -> None:
        """
        Either adds a new trace to the mapping or swaps an existing mapping
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

    
def find_non_skipping_candidates(tree:TransitionTree, trace:Trace)\
    -> Set[Path]:
    """
    Constructs all possible paths that are the same length of the given trace.
    """
    return set( 
        find_path_in_tree(tree, node)
        for node in tree.vertices()
        if len(node.sigma_sequence()) == len(trace)
    )

def mutate_path_with_skip(path:Path) -> Set[Path]:
    """
    Constructs all mutations of the given path with one skip inserted.
    The last step in the path is not seen in mutations.
    """
    pseq = path.sequence
    mutations = set()
    for i in range(1, len(path)+1):
        head = pseq[:i-1]
        mid = [Skipper()]
        tail = pseq[i-1:-1]
        mutations.add(Path(head+mid+tail))
    return mutations

def find_skipping_candidates(tree:TransitionTree, trace:Trace) -> Set[Path]:
    """
    Constructs all possible paths with one skip, that are shorter than the
    given trace.
    """
    return set( 
        skipper
        for node in tree.vertices()
        if 1 <= len(node.sigma_sequence()) <= len(trace)
        for skipper
        in mutate_path_with_skip(
            find_path_in_tree(tree, node)
        )
    )

def find_terminal_candidates(tree:TransitionTree, trace:Trace) -> Set[Path]:
    """
    Constructs all possible paths from terminal nodes for the given trace.
    """
    exact_terms = set(
        find_path_in_tree(tree, node)
        for node 
        in tree.terminals()
        if len(node.sigma_sequence()) == len(trace)
    )
    non_exact_terms = set( 
        skipper 
        for node 
        in tree.terminals()
        if len(node.sigma_sequence()) < len(trace)
        for skipper 
        in mutate_path_with_skip(
            Path( 
            find_path_in_tree(tree, node).sequence + [Skipper()]
            )
        )
    )
    return exact_terms.union(non_exact_terms)

def cost_of_path(path:Path, trace:Trace, root_is_terminal:bool=False) -> int:
    """
    Computes of the cost of the path in the context of the given trace.
    An optimal path for a trace has a cost of zero, while a non-optimal
    path has a cost greater than zero.
    """
    len_cost = len(trace) - len(path.noskips)
    act_cost = 0
    for act, actf in zip(trace, path):
        if isinstance(actf, Skipper):
            act_cost += 1
        else:
            act_cost += 0 if act == actf.activity() else 1
    if (len(path.noskips) > 0 ):
        term_cost = 0 if path.noskips[-1].next().terminal() else 1
    else:
        term_cost = 1 if root_is_terminal else 0
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

class EqualPathWeighter():
    """
    A weighting function, that equally weights candidates,
    between a path and a trace.
    """

    def __init__(self, candidates:Set[Path]) -> None:
        self._cands = deepcopy(candidates)

    def __call__(self, path:Path, trace:Trace) -> float:
        if path in self._cands:
            return 1.0 / len(self._cands)
        else:
            return 0.0
    
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
        if path in self._cands:
            cost = cost_of_path(path, trace)
            share = 1 / self.size
            offset = self.kappa ** cost
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
        
def _computation_many_matching(trace, tree) -> Tuple[Trace,Set[Path]]:
    """
    The individual work for a given trace, to find a matching.
    """
    noskips = find_non_skipping_candidates(tree, trace)
    skippings = find_skipping_candidates(tree,trace)
    terminals = find_terminal_candidates(tree,trace)
    allcads = noskips.union(skippings).union(terminals)
    if len(allcads) > 0:
        least_costy = find_least_costy_paths(
            noskips.union(skippings).union(terminals),
            trace,
            root_is_terminal=tree.root() in tree.terminals()
        )
    else: 
        raise Exception(f"Unable to find any candidates for :: {trace}")
    return (trace, least_costy)

def construct_many_matching(log:EventLog, tree:TransitionTree) \
     -> ManyMatching:
    """
    Constructs a set of likely cadidate paths for each trace in the log,
    then constructs a map from traces to these sets.
    """
    mapping = ManyMatching(dict())
    rets = Parallel(n_jobs=-2)(
        delayed(_computation_many_matching)(trace,tree)
        for trace
        in InfoIteratorProcessor("matchings", [ trace for trace,_ in log ]
                                 ,stack=8)
    )
    for trace,least_costy in rets:
        info(f"no. of matching generated for {trace} was {len(least_costy)}")
        mapping.add_to_map(trace, least_costy)
    return mapping

