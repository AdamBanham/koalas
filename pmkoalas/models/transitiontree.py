"""
This module outlines a data structure for transitions tree as proposed by Hidders, J.,
 Dumas, M., van der Aalst, W.M.P., ter Hofstede, A.H.M., Verelst, J.: When are two
 workflows the same? In: CATS. ACS (2005); These trees can be modified for future work.
"""

from typing import Set, List, Tuple, Union
from copy import deepcopy
from dataclasses import dataclass

from pmkoalas.simple import Trace, EventLog
from pmkoalas.complex import ComplexEvent, ComplexEventLog

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
            if (f.offering() == self):
                out.add(f)
        return out
    
    # data model functions
    def __str__(self) -> str:
        return self.id()

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
    
    # data model functions
    def __str__(self):
        return f"{self.offering()} -> {self.activity()} -> {self.next()}"

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, TransitionTreeFlow)):
            if (self.offering() == __o.offering()):
                if (self.next() == __o.next()):
                    return True
        return False
    
    def __hash__(self) -> int:
        return hash(tuple([ self.offering(), self.activity(), self.next()]))
    


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
    
    def __str__(self):
        return "(" + super().__str__() + f")^{len(self._pop)}"
    
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

    def __hash__(self):
        return hash((self.sigma.__hash__(), tuple(self.activity)))

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
            out.add(Offer(vertex.sigma_sequence(), set(acts)))
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
        out = set()
        flows = self.flows()
        for vertex in self.strict_vertices():
            acts = set()
            for flow in vertex.outgoing(flows):
                acts.add(flow.activity())
            out.add(Offer(vertex.sigma_sequence(), set(acts)))
        return out

    # utility functions

    # comparision functions

def construct_from_log(log:Union['EventLog','ComplexEventLog']) -> TransitionTree:
    """ Constructs a transition tree from an event log. """
    if (isinstance(log, EventLog)):
        return construct_from_simple_log(log)
    elif (isinstance(log, ComplexEventLog)):
        return construct_from_complex_log(log)
    else:
        raise ValueError("Was expecting a simple or complex event log, but was "+
                         f"given {type(log)}.")

def construct_from_simple_log(log:'EventLog') -> TransitionTree:
    """ Constructs a transition tree using a simple event log. """ 
    vroot = TransitionTreeRoot()
    vid = 1
    verts = dict( [(Trace([]), vroot)])
    flows = set()
    for trace,freq in log:
        pseq = []
        for act in trace:
            offering = verts[Trace(pseq)]
            if Trace(pseq + [act]) in verts.keys():
                next = verts[Trace(pseq + [act])]
            else:
                vid += 1
                last = len(Trace(pseq + [act])) == len(trace)
                next = TransitionTreeVertex(
                    vid,
                    Trace(pseq + [act]),
                    end=last 
                )
                verts[Trace(pseq + [act])] = next
            flow = TransitionTreePopulationFlow( 
                offering,
                act,
                next,
                [ComplexEvent(act, dict())] * freq
            )
            flows.add(flow)
            pseq.append(act)
    # handle back
    verts = set([ v for v in verts.values()])
    return TransitionTree(verts, vroot, flows)

def construct_from_complex_log(log:'ComplexEventLog') -> TransitionTree:
    """ Constructs a transition tree using a complex event log. """
    vroot = TransitionTreeRoot()
    vid = 1
    verts = dict( [(Trace([]), vroot)])
    flows = set()
    for trace,instances in log:
        pseq = []
        for id in range(0,len(trace)):
            act = trace[id]
            offering = verts[Trace(pseq)]
            if Trace(pseq + [act]) in verts.keys():
                next = verts[Trace(pseq + [act])]
            else:
                vid += 1
                last = len(Trace(pseq + [act])) == len(trace)
                next = TransitionTreeVertex(
                    vid,
                    Trace(pseq + [act]),
                    end=last 
                )
                verts[Trace(pseq + [act])] = next
            flow = TransitionTreePopulationFlow( 
                offering,
                act,
                next,
                list()
            )
            # build population from instances
            pops = [ i[id] for i in instances ] 
            # check for existing population and update population
            if flow in flows:
                old_flow = [ f for f in flows if f == flow][0]
                pops = pops + old_flow.population()
                flows.remove(flow)
            flow = TransitionTreePopulationFlow( 
                offering,
                act,
                next,
                pops
            )
            flows.add(flow)
            pseq.append(act)
    # handle back
    verts = set([ v for v in verts.values()])
    return TransitionTree(verts, vroot, flows)