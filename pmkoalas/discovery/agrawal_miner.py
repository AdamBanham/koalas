"""
This module is a implementation of the miner present by R. Argrawal in 1997.

See the following article for more information about the argrawal miner:\n
R. Agrawal, D. Gunopulos, and F. Leymann, “Mining process models from workflow
logs,” in EDBT, ser. Lecture Notes in Computer Science, vol. 1377, 
Springer, 1998, pp. 469–483
"""
from dataclasses import dataclass, field
from typing import Set, Optional, List
from copy import deepcopy

from pmkoalas.simple import Trace

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

class ArgrawalMinerInstance():
    """
    TODO
    """

    def __init__(self) -> None:
        pass

