"""
This module focuses on providing ways to produce a log from models in the class
of Petri nets.
"""
from copy import deepcopy
from typing import Dict, Iterable, Mapping,Set,List

from pmkoalas import __version__
from pmkoalas.complex import ComplexEventLog, ComplexTrace, ComplexEvent
from pmkoalas.simple import Trace

#typing imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pmkoalas.models.transitiontree import TransitionTreeGuard
    from pmkoalas.models.petrinet import LabelledPetriNet, Place, Transition

class PetriNetMarking():
    """
    Data structure for a marking in a petri net, i.e. a multiset of places.
    """
    
    def __init__(self, model:'LabelledPetriNet', marking:Dict['Place',int]) -> None:
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

    def enabled(self) -> Set['Transition']:
        """
        returns the set of transitions that are enabled at this marking.
        """
        ret = set()
        for trans in self._net.transitions:
            enabled = True
            for place in self._incoming[trans]:
                enabled = enabled and self._mark[place] > 0
            if (enabled):
                ret.add(trans)
        return ret

    def can_fire(self) -> Set['Transition']:
        """
        returns the set of transitions that can fire from this marking.
        """
        return self.enabled()
    
    def remark(self, firing:'Transition') -> 'PetriNetMarking':
        """
        Returns a new marking, that is one step from this marking by firing
        the given transition.
        """
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
    """
    A data structure for a sequence of fired transitions.
    """

    def __init__(self, marking:'PetriNetMarking', fired:List['Transition'],
        final_marking:PetriNetMarking) -> None:
        self._final = final_marking
        self._mark = deepcopy(marking)
        self._seq = deepcopy(fired)

    def next(self) -> Set['Transition']:
        """
        Returns the set of transitions that can be seen as a possible next
        """
        # return nothing if we are at final
        if (self.reached_final()):
            return set()
        # remove previous linked silence from choices
        previous_silence = dict()
        for last in self._seq[-1::-1]:
            if last.silent:
                if last in previous_silence:
                    previous_silence[last] = previous_silence[last] + 1
                else:
                    previous_silence[last] = 1
            else:
                break
        drops = set()
        for silent in previous_silence:
            if previous_silence[silent] > 1:
                drops.add(silent)
        # present choices
        choices = self._mark.can_fire().difference(drops)
        return choices
    
    def fire(self, firing:'Transition') -> 'PetriNetFiringSequence':
        """
        Returns a new firing sequence, that is one step from this sequence
        by firing the given transition.
        """
        new_mark = self._mark.remark(firing)
        new_seq = self._seq + [firing]
        return PetriNetFiringSequence(
            new_mark, new_seq, self._final
        )
    
    def fired(self) -> List['Transition']:
        """
        Returns a sequence of transitions that have been fired. 
        """
        return deepcopy(self._seq)

    def reached_final(self) -> bool:
        """
        Returns true if the firing sequence reaches the final marking.
        """
        return self._mark == self._final
    
    def __len__(self) -> int:
        halted = 1 if self.reached_final() else 0
        return len([ f for f in self._seq if not f.silent]) + halted
    
    def __hash__(self) -> int:
        return hash( tuple(self._seq + [self.reached_final()]))


class PlayoutEvent(ComplexEvent):
    """
    An abstraction for playout events.
    """

    def __init__(self, activity: str, guard:object) -> None:
        super().__init__(activity, {'guard' : guard})

    @property
    def guard(self) -> object:
        return self.data()['guard']
    
class PlayoutEnd(PlayoutEvent):
    """
    Dummy class to signal halting in playout.
    """

    def __init__(self) -> None:
        from pmkoalas.models.transitiontree import TransitionTreeGuard
        super().__init__("halt", TransitionTreeGuard())
    


class PlayoutTrace(ComplexTrace):
    """
    An abstraction for playout traces, with cuts and projections.
    """

    def __init__(self, 
                 events: Iterable[PlayoutEvent], 
                 data: Mapping[str, object] = None) -> None:
        super().__init__(events, data)

    def acut(self, i:int) -> 'Trace':
        """
        Returns the cut of activity sequence of this playout up to the
        i-th element (if it exists).
        """
        seq = self.simplify().sequence
        ret = []
        while i > 0 and len(seq) > 0:
            head = seq.pop(0)
            ret.append(head)
            i -= 1
        return Trace(ret)
    
    def act(self, i:int) -> str:
        """
        Returns the activity of the i-th event.
        """
        return self[i].activity()
    
    def guard(self, i:int) -> 'TransitionTreeGuard':
        return self[i].guard

def construct_playout_log(model:'LabelledPetriNet', max_length:int, 
        initial_marking:'PetriNetMarking', final_marking:'PetriNetMarking') \
        -> ComplexEventLog:
    """ 
    Constructs a log of play-out traces from a model with a length of 
    max_length + 1.
    """
    # importing here to remove circular dependencies.
    from pmkoalas.models.transitiontree import TransitionTreeMerge
    from pmkoalas.models.transitiontree import TransitionTreeGuard

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
                    leftover_guard = None
                trace_seq.append(
                    PlayoutEvent(fired.name, guard)
                )
        # add halt symbol if required
        if comp.reached_final():
            trace_seq.append(PlayoutEnd())
        # construct trace and store
        playout_traces.append(
            PlayoutTrace(
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