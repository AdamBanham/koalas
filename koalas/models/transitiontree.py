"""
This module outlines a data structure for transitions tree as proposed by Hidders, J.,
 Dumas, M., van der Aalst, W.M.P., ter Hofstede, A.H.M., Verelst, J.: When are two
 workflows the same? In: CATS. ACS (2005); These trees can be modified for future work.
"""

from typing import Set, List, Tuple, Union
from copy import deepcopy
from dataclasses import dataclass

from koalas.simple import Trace
from koalas.complex import ComplexEvent

class TranstionTreeEarlyComplete():
    """
    Place holder for a option to early complete
    """

    def __init__(self) -> None:
        pass

class TransitionTreeVertex():
    """
    Data class for a vertex in a transition tree.
    """

    VERTEX_FORMAT = "v_{id}"

    def __init__(self, id:int, partial_trace:Trace, end:bool=False) -> None:
        self._label = self.VERTEX_FORMAT.format(id=id)
        self._partial = deepcopy(partial_trace)
        self._end = end
    
    # properties
    def id(self) -> str:
        " returns a identifier for this vertex."
        return self._label
    
    def sigma_sequence(self) -> Trace:
        " returns the unique partial trace from root to this vertex."
        return deepcopy(self._partial)
    
    def is_root(self) -> bool:
        " returns a boolean to say if this vertex is the root."
        return False
    
    def end(self) -> bool:
        """ 
        returns a boolean to say if this vertex is signals the end of the 
        process execution.
        """
        return self._end
    
    # utility functions
    def outgoing(self, flows:Set['TransitionTreeFlow']) -> Set['TransitionTreeFlow']:
        " returns the set of flows that are outgoing from this vertex."
        out = set()
        for f in flows:
            if (f.source() == self):
                out.add(f)
        return out
    
    # data model functions
    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, TransitionTreeVertex)):
            return self.sigma_sequence() == __o.sigma_sequence()
        return False
    
    def __hash__(self) -> int:
        return hash((self.sigma_sequence().__hash__()))
    

class TransitionTreeRoot(TransitionTreeVertex):
    """
    Data class for the root of a transition tree.
    """

    def __init__(self, id=1) -> None:
        super().__init__(id, Trace([]))

    def is_root(self) -> bool:
        return True

class TransitionTreeFlow():
    """
    Template for a flow between two vertices in a transition tree.
    """

    def __init__(self, source:TransitionTreeVertex, 
                 act:Union[str,TranstionTreeEarlyComplete], 
                 target:TransitionTreeVertex) -> None:
        self._source = source
        self._act = act 
        self._target = target

    def offering(self) -> TransitionTreeVertex:
        " returns the vertex that offers this flow."
        return self._source
    
    def next(self) -> TransitionTreeVertex:
        " returns the vertex that this flow is directed towards."
        return self._target
    
    def activity(self) -> Union[str,TranstionTreeEarlyComplete]:
        " returns the process activity related to this flow."
        return self._act
    
    def label(self) -> object:
        " returns the actual label of the flow, varys depending on implementation."
        return self.activity()
    
    def attributes(self) -> Set[str]:
        """ 
        returns the associated attributes with this flow, varys depending on 
        implementation. 
        """
        return set()

class TransitionTreeInformationFlow(TransitionTreeFlow):
    """
    A implementation for a flow with abstracted information.
    """

    def __init__(self, source:TransitionTreeVertex, 
                 act:Union[str,TranstionTreeEarlyComplete], 
                 target:TransitionTreeVertex,
                 information:object) -> None:
        super().__init__(source, act, target)
        self._info = deepcopy(information)

    def label(self) -> Tuple[str, object]:
        return (self.activity(), deepcopy(self._info))

class TransitionTreePopulationFlow(TransitionTreeFlow):
    """
    A implementation for a flow with an exact population of data attribute mappings.
    """

    def __init__(self, source:TransitionTreeVertex, 
                 act:Union[str,TranstionTreeEarlyComplete], 
                 target:TransitionTreeVertex, 
                 population:List[ComplexEvent]) -> None:
        super().__init__(source, act, target)
        self._pop = deepcopy(population)
        self._attrs = set()
        for ev in self._pop:
            for attr in ev.data().keys():
                self._attrs.add(attr)

    def label(self) -> Tuple[str, List[ComplexEvent]]:
        return (self.activity(), deepcopy(self._pop))
    
    def attributes(self) -> Set[str]:
        return self._attrs
    
    def population(self) -> List[ComplexEvent]:
        " returns the associated population of data attribute mappings."
        return deepcopy(self._pop)
    
class TransitionTreeGuard():
    """
    A template for semantic of a guard from the system.
    """

    def __init__(self) -> None:
        pass

    def check(self, data:ComplexEvent) -> bool:
        " return whether the given data is supported by this guard."
        return False
    
    def required(self) -> Set[str]:
        " returns the required data attributes for this guard."
        return set()
    
    def enabling(self, population:Set[ComplexEvent]) -> Set[ComplexEvent]:
        " returns the subset of the population that this guard supports."
        return set([ p for p in population if self.check(p)])

class TransitionTreeGuardFlow(TransitionTreeFlow):
    """
    A implemenatiton for a flow with an implicit population using a guard function.
    """

    def __init__(self, source:TransitionTreeVertex, 
                 act:Union[str,TranstionTreeEarlyComplete], 
                 target:TransitionTreeVertex, 
                 guard:TransitionTreeGuard) -> None:
        super().__init__(source, act, target)
        self._guard = deepcopy(guard)

    def label(self) -> Tuple[str, TransitionTreeGuard]:
        return (self.activity(), deepcopy(self._guard))
    
    def attributes(self) -> Set[str]:
        return self._guard.required()
    
    def guard(self) -> TransitionTreeGuard:
        return self._guard
    
@dataclass
class Offer():
    """ A data container for an offer from a transition tree. """

    sigma:Trace
    activity:Set[Union[str,TranstionTreeEarlyComplete]]

class TransitionTree():
    """
    A transition tree is a connected, rooted, edge-labeled and directioned graph
    without cycles. See 'When are two  workflows the same?' In: CATS. ACS (2005).
    """

    def __init__(self, 
                 vertices:Set[TransitionTreeVertex], 
                 root:TransitionTreeRoot,
                 flows:Set[TransitionTreeFlow]) -> None:
        # check types and input
        if not (isinstance(vertices, set)) or vertices == None:
            raise ValueError(f"Unexpected vertices, was expecting a set but got"+
                             f" {type(vertices)}.")
        elif not (isinstance(root, TransitionTreeRoot)) or root == None:
            raise ValueError(f"Unexpected root, was expecting a "+
                             f"`TransitionTreeRoot` but got {type(root)}.")
        elif not (isinstance(flows, set)) or flows == None:
            raise ValueError("Unexpected flows, was expecting a set but got "+
                             f"{type(flows)}")
        # create copies
        self._vertices = deepcopy(vertices)
        self._root = deepcopy(root) 
        self._flows = deepcopy(flows)
        # precompute
        self._attrs = set([ a for f in self._flows for a in f.attributes() ])
        self._pops = [ 
            f.population() 
            for f 
            in self._flows 
            if isinstance(f, TransitionTreePopulationFlow)
        ]
        self._guards = set([
            f.guard()
            for f 
            in self._flows
            if isinstance(f, TransitionTreeGuardFlow)
        ])

    # properties
    def vertices(self) -> Set[TransitionTreeVertex]:
        """
        returns the full set of vertices that are defined by this transition tree.
        """ 
        return deepcopy(self._vertices)

    def root(self) -> TransitionTreeRoot:
        """
        returns the root vertex of this transition tree.
        """ 
        return deepcopy(self._root)

    def flows(self) -> Set[TransitionTreeFlow]:
        """
        returns the full set of flows that are defined by this transition tree.
        """
        return deepcopy(self._flows)

    def strict_vertices(self) -> Set[TransitionTreeVertex]:
        """
        returns the partial set of vertices that have at least two outgoing flows.
        """
        out = set()
        flows = self.flows()
        for vertex in self.vertices():
            if len(vertex.outgoing(flows)) > 1:
                out.add(vertex)
        return out

    def offers(self) -> Set[Offer]:
        """
        returns the full set of offers that could happen based on this transition tree.
        """ 
        out = set()
        flows = self.flows()
        for vertex in self.vertices():
            acts = set()
            for flow in vertex.outgoing(flows):
                acts.add(flow.activity())
            out.add(Offer(vertex.sigma_sequence(), acts))
        return out

    def attributes(self) -> Set[str]:
        """
        returns a set of attribute names that are used within the information attached to flows.
        """ 
        return deepcopy(self._attrs)

    def populations(self) -> List[Set[ComplexEvent]]:
        """
        returns the set of explicit polutations of data attribute mappings.
        """
        return deepcopy(self._pops)

    def guards(self) -> Set:
        """
        returns the set of guards used in flows, that imply a population of data 
        attribute mappings.
        """
        return deepcopy(self._guards)

    def choices(self) -> Set:
        """
        returns a strict set of offerings, where we only consider offers from 
        vertices with many outgoing flows.
        """
        offers = self.offers()
        strict_vertices = self.strict_vertices()
        def check_for(offer:Offer):
            for v in strict_vertices:
                if (v.sigma_sequence() == offer.sigma):
                    return True
            return False
        return set([ o for o in offers if check_for(o) ])

    # utility functions

    # comparision functions

