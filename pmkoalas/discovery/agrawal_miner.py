"""
This module is a implementation of the miner present by R. Argrawal in 1997.

See the following article for more information about the argrawal miner:\n
R. Agrawal, D. Gunopulos, and F. Leymann, “Mining process models from workflow
logs,” in EDBT, ser. Lecture Notes in Computer Science, vol. 1377, 
Springer, 1998, pp. 469–483
"""
from dataclasses import dataclass, field
from typing import Set, Optional, List, Tuple
from copy import deepcopy
from itertools import product

from pmkoalas.discovery.meta import DiscoveryTechnique
from pmkoalas.simple import Trace
from pmkoalas.simple import EventLog
from pmkoalas._logging import debug

@dataclass
class DependencyNode():
    """
    Helper
    """

    label:str

    def __hash__(self) -> int:
        return hash(self.label)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, type(self)) :
            return self.__hash__() == value.__hash__()
        else:
            False


@dataclass
class DependencyEdge():
    """
    Helper
    """

    source:DependencyNode
    target:DependencyNode

    def __hash__(self) -> int:
        return hash((self.source.label,self.target.label))
    
@dataclass
class DependencyWalk():

    walk:List[DependencyNode] = field(default_factory=list)


    def step(self, edge:DependencyEdge) -> 'DependencyWalk':
        last = self.walk[-1]

        if (edge.source == last):
            contains = [ n for n in self.walk if n == edge.target] 
        else:
            raise ValueError("Passed a edge that is not from the last node.")


class DependencyGraph():
    """
    TODO
    """

    def __init__(self, vertices:Set[DependencyNode], edges:Set[DependencyEdge]) -> None:
        self._vertices = deepcopy(vertices)
        self._acts = set([ v.label for v in self._vertices])
        self._edges = deepcopy(edges)

    def induce_subgraph(self, trace:Trace) -> Optional['DependencyGraph']:
        """
        Returns the induced subgraph of the dependency graph for the given
        trace.

        May return None if the trace's activities are not
        """

        if trace.seen_activities().issubset(self._acts):
            new_vectices = set([ 
                DependencyNode(l) for l in trace.seen_activities()
            ]) 
            new_edges = set([ 
                edge 
                for edge 
                in self._edges
                if edge.source in new_vectices and edge.target in new_vectices
            ])
            return DependencyGraph(
                new_vectices, new_edges
            )
        else:
            return None
        
    def isconnected(self) -> bool:
        """
        TODO
        """
        return False
    
    def path_between(self, from_node:DependencyNode, to_node:DependencyNode
                    ) -> bool:
        """
        TODO
        """
        visited = set()
        paths = []
        

        return False
    


def execution_is_consistent(trace:Trace, graph:DependencyGraph) -> bool:
    """
    Determines if the trace is consistent with the given graph, as described
    by definition 6 in R. Agrawal, D. Gunopulos, and F. Leymann, “Mining 
    process models from workflow logs”.
    """
    sub = graph.induce_subgraph(trace)

    if (sub != None):
        if (sub.isconnected()):
            return True

    return False

class ArgrawalMinerInstance(DiscoveryTechnique):
    """
    Mines a graph from an simplified event log using the proposed 
    approach by R. Argrawal D. Gunopulos and F. Leymann in 1998.

    The resulting graph aims to have the following properties:
    - completeness, the graph preserves all dependencies between activities
      presented in the event log.
    - irredundancy, the graph should not introduce spurious dependencies 
    - mimimality, the graph should have miminal edges.

    The resulting graph represents the constraints between activities rather
    than a system that executes to produce traces.
    """

    def __init__(self) -> None:
        pass

    def discover(self, slog:EventLog) -> DependencyGraph:
        """
        Discovers the dependency graph from the given simplifed event log, 
        using the proposed approach by R. Argrawal D. Gunopulos and F. 
        Leymann in 1998.
        """
        pass

    def _check_follows_for(self, trace:Trace, actB:str, actA:str) -> bool:
        """
        Returns True if the first instance of activity A occurs before 
        the first instance activity B in the given trace.
        """
        first_a = -1
        first_b = -1
        for id,act in enumerate(trace.__iter__()):
            if act == actA:
                first_a = id
            if act == actB:
                first_b = id
            if first_a != -1 and first_b != -1:
                break
        debug(f"checking :: {trace} for {actA} -> {actB} :: {first_a} < {first_b}")
        return first_a < first_b

    def compute_follows_relations(self, slog:EventLog) -> Set[Tuple[str,str]]:
        """
        Returns the set of follows relations for the given trace based on
        def.3 and def.4 in Argrawal et al. 1998.

        An acitivty B follows activity A if B starts after A in each 
        trace that both B and A appear in, 
        OR,
        there exists an activity C such that C follows A and B follows C.
        """
        debug(slog)
        acts = slog.seen_activities()
        debug(acts)
        follows = set()
        # iterate over all traces and compute case 1
        for actB,actA in product(acts,acts):
            if actA == actB:
                continue
            debug(f"checking {actB} -> {actA}")
            # collect all executions where both acts occur
            traces = [ 
                trace 
                for trace,_ 
                in slog.__iter__() 
                if 
                    actA in trace.seen_activities() 
                    and 
                    actB in trace.seen_activities()
            ]
            if (len(traces) == 0):
                continue
            # check if B follow A in all traces
            debug(traces)
            traces = [
                1 if self._check_follows_for(t,actB,actA) else 0
                for t 
                in traces
            ]
            debug(traces)
            if (sum(traces) == len(traces)):
                follows.add((actB,actA))
        # adjust follows based on case 2
        for actB,actC in zip(acts,acts):
            if actB == actC:
                continue
            for actA in acts:
                pass
        debug(follows)
        return follows

