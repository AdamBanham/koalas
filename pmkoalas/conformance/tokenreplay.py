"""
This module focuses on providing ways to produce a log from models in the class
of Petri nets.
"""
from copy import deepcopy
from typing import Dict,Set,List

from pmkoalas import __version__
from pmkoalas.models.petrinet import LabelledPetriNet, Place, Transition
from pmkoalas.complex import ComplexEventLog, ComplexTrace, ComplexEvent

class PetriNetMarking():
    """
    Data structure for a marking in a petri net, i.e. a multiset of places.
    """

    def __init__(self, model:LabelledPetriNet, marking:Dict[Place,int]) -> None:
        self._net = model
        self._mark = deepcopy(marking)
        # for each transition compute the incoming and outcoming places
        self._incoming:Dict[Transition,Set[Place]] = dict()
        self._outcoming:Dict[Transition,Set[Place]] = dict()
        for trans in self._net.transitions:
            arcs = self._net.arcs
            incoming = [ arc for arc in arcs if  arc.to_node == trans ]
            outcoming = [ arc for arc in arcs if arc.from_node == trans ]
            self._incoming[trans] = [ arc.from_node for arc in incoming ]
            self._outcoming[trans] = [ arc.to_node for arc in outcoming ]

    def enabled(self) -> Set[Transition]:
        ret = set()
        for trans in self._net.transitions:
            enabled = True
            for place in self._incoming[trans]:
                enabled = enabled and self._mark[place] > 0
            if (enabled):
                ret.add(trans)
        return ret

    def can_fire(self) -> Set[Transition]:
        return self.enabled()
    
    def remark(self, firing:Transition) -> 'PetriNetMarking':
        if firing not in self.can_fire():
            raise ValueError("Given transition cannot fire from this marking.")
        next_mark = deepcopy(self._mark)
        for incoming in self._incoming[firing]:
            next_mark[incoming] = next_mark[incoming] - 1
        for outcoming in self._outcoming[firing]:
            next_mark[outcoming] = next_mark[outcoming] + 1
        return PetriNetMarking(self._net, next_mark)
    
    # data-model functions
    def __eq__(self, other: object) -> bool:
        if (isinstance(other, PetriNetMarking)):
            return self._mark == other._mark
        return False
    
class PetriNetFiringSequence():

    def __init__(self, marking:PetriNetMarking, fired:List[Transition],
        final_marking:PetriNetMarking) -> None:
        self._final = final_marking
        self._mark = deepcopy(marking)
        self._seq = deepcopy(fired)

    def next(self) -> Set[Transition]:
        # return nothing if we are at final
        if (self.reached_final()):
            return set()
        # remove previous linked silence from choices
        previous_silence = set()
        for last in self._seq[-1::-1]:
            if last.silent:
                previous_silence.add(last)
            else:
                break
        # present choices
        choices = self._mark.can_fire().difference(previous_silence)
        return choices
    
    def fire(self, firing:Transition) -> 'PetriNetFiringSequence':
        new_mark = self._mark.remark(firing)
        new_seq = self._seq + [firing]
        return PetriNetFiringSequence(
            new_mark, new_seq, self._final
        )
    
    def fired(self) -> List[Transition]:
        return deepcopy(self._seq)

    def reached_final(self) -> bool:
        return self._mark == self._final
    
    def __len__(self) -> int:
        halted = 1 if self.reached_final() else 0
        return len([ f for f in self._seq if not f.silent]) + halted
    
    def __hash__(self) -> int:
        return hash( tuple(self._seq + [self.reached_final()]))
    

class PlayoutEnd(ComplexEvent):
    """
    Dummy class to signal halting in playout.
    """

def construct_playout_log(model:LabelledPetriNet, max_length:int, 
        initial_marking:PetriNetMarking, final_marking:PetriNetMarking) \
        -> ComplexEventLog:
    """ 
    Constructs a log of play-out traces from a model with a length of 
    max_length + 1.
    """
    from pmkoalas.models.transitiontree import TransitionTreeMerge

    playout_traces = list()
    completed:List[PetriNetFiringSequence] = set()
    incomplete = [ 
        PetriNetFiringSequence(initial_marking, list(), final_marking)
    ]
    seen = set()
    while len(incomplete) > 0:
        select = incomplete.pop(0)
        seen.add(select)
        potentials = list()
        for firing in select.next():
            potentials.append(select.fire(firing))
        for pot in potentials:
            if (pot.reached_final() and len(pot) <= max_length + 1):
                completed.add(pot)
            elif (len(pot) == max_length + 1):
                completed.add(pot)
            else:
                if pot not in seen and len(pot) < max_length + 1:
                    incomplete.append(pot)
            
    # now for each completed trace, we need to produce a complex trace
    trace_id = 1
    for comp in completed:
        trace_map = {
            "concept:name" : f"play-out trace {trace_id}"
        }
        trace_seq = list()
        leftover_guard = None 
        # build sequence of fired transitions
        ## but profilerate guards on silence, without recording them
        for fired in comp.fired():
            if fired.silent:
                if leftover_guard == None:
                    leftover_guard = fired.guard
                else:
                    leftover_guard = TransitionTreeMerge(leftover_guard, 
                                                         fired.guard)
            else:
                guard = fired.guard 
                if leftover_guard != None:
                    guard = TransitionTreeMerge(leftover_guard, guard)
                event_map = {
                    'guard' : guard
                }
                trace_seq.append(
                    ComplexEvent(fired.name, event_map)
                )
        # add halt symbol if required
        if comp.reached_final():
            trace_seq.append(PlayoutEnd("halt", dict()))
        # construct trace and store
        playout_traces.append(ComplexTrace(
                trace_seq,
                trace_map
            )
        )
        trace_id += 1
    return ComplexEventLog(playout_traces, dict({
        "meta:generated:by" : "pmkoalas",
        "meta:generator:version" : __version__
        }), 
        f"playout log for {model._name}"
    )