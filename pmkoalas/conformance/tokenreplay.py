"""
This module focuses on providing ways to produce a log from models in the class
of Petri nets.
"""
from copy import deepcopy
from typing import Dict, Iterable, Mapping,Set,List,Tuple

from pmkoalas import __version__
from pmkoalas.complex import ComplexEventLog, ComplexTrace, ComplexEvent
from pmkoalas.simple import Trace, EventLog
from pmkoalas.models.transitiontree import TransitionTreeGuard
from pmkoalas._logging import info, debug, InfoQueueProcessor, InfoIteratorProcessor
from pmkoalas.models.petrinets.pn import LabelledPetriNet, PetriNetMarking
from pmkoalas.models.petrinets.pn import AcceptingPetriNet, PetriNetSemantics
from pmkoalas.models.petrinets.pn import Transition
from pmkoalas.models.petrinets.guards import Guard, GuardOutcomes
from pmkoalas.models.petrinets.dpn import AcceptingDataPetriNet
from pmkoalas.models.petrinets.dpn import get_execution_semantics

class PlayoutTransitionGuard(TransitionTreeGuard):
    """
    Template for taking a guard off a transition in a petri net and converting
    it into the semantics for a transition tree.
    """

    def __init__(self, guard:'Guard', id:str=None) -> None:
        super().__init__()
        self._guard = guard
        self._id = 1 if id == None else id
        
    def check(self, data: ComplexEvent) -> 'GuardOutcomes':
        return self._guard.evaluate_data(data)
    
    def html_label(self) -> str:
        return f"g<sub>{self._id}</sub>"
    
    def expanded_html_label(self) -> str:
        return f"{self._guard}"
    
    def __hash__(self) -> int:
        return hash(self.expanded_html_label())

class PetriNetFiringSequence():
    """
    A data structure for a sequence of fired transitions.
    """

    def __init__(self, sem:PetriNetSemantics, fired:List['Transition'],
        final_marking:PetriNetMarking) -> None:
        self._final = final_marking
        self._mark = deepcopy(sem)
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
        return len([ f for f in self._seq if not f.silent])
    
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
        i-th step (if it exists).
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
        Returns the activity of the i-th step.
        """
        return self[i].activity()
    
    def guard(self, i:int) -> PlayoutTransitionGuard:
        """
        Returns the guard of the i-th step.
        """
        return self[i].guard
    
def generate_traces_from_lpn(
        model:'LabelledPetriNet', max_length:int,
        strict:bool=False, updates_on:int=1000) \
    -> EventLog:
    """
    Generates a simple log of a sample traces from a model with a length 
    of max_length. By default returns traces that did not reach the final
    marking. If strict is set to True, only traces that reach the final
    marking are returned.
    """
    inprogress:List[Tuple[Trace,PetriNetMarking]] = [ 
        (Trace([]), deepcopy(model.initial_marking)) ]
    completed = []
    pcount = 0
    while len(inprogress) > 0:
        trace, mark = inprogress.pop(0)
        debug(f"processing trace {str(trace)} with marking {str(mark)}")
        if len(trace) == max_length:
            if strict:
                if mark.reached_final():
                    completed.append(trace)
            else:
                completed.append(trace)
        else:
            if mark.reached_final():
                completed.append(trace)
            else:
                firable = mark.can_fire()
                for t in firable:
                    new_mark = mark.remark(t)
                    new_trace = Trace(trace.sequence + [t.name])
                    inprogress.append((new_trace, new_mark))
        pcount += 1
        if (pcount % updates_on == 0):
            info(f"processing {len(inprogress)} partial executions of the lpn")
            info(f"shortest trace :: {len(inprogress[0][0])}")
            info(f"longest trace :: {len(inprogress[-1][0])}")
            pcount = 0
    return EventLog(completed, f"Generated traces from LPN ({model.name})")


def construct_playout_log(model:AcceptingDataPetriNet, max_length:int, 
        initial_marking:PetriNetMarking, final_marking:PetriNetMarking) \
        -> ComplexEventLog:
    """ 
    Constructs a log of play-out traces from a model with a length of 
    max_length + 1.
    """
    # importing here to remove circular dependencies.
    from pmkoalas.models.transitiontree import TransitionTreeMerge
    exec_model = get_execution_semantics(model)
    playout_traces = list()
    completed:Set[PetriNetFiringSequence] = set()
    incomplete = [ 
        PetriNetFiringSequence(exec_model.semantics, list(), final_marking)
    ]
    seen = set()
    pbar = InfoQueueProcessor(itername="processed partials",
                                 starting_size=len(incomplete)
    )
    while len(incomplete) > 0:
        select = incomplete.pop(0)
        if (len(select) > 0):
            completed.add(select)
        seen.add(select)
        potentials = list()
        for firing in select.next():
            potentials.append(select.fire(firing))
        for pot in potentials:
            if pot not in seen and len(pot) <= max_length:
                incomplete.append(pot)
                pbar.extent(1)
        pbar.update()        
    # now for each completed trace, we need to produce a complex trace
    trace_id = 1
    guard_id = 1
    guard_ids = {}
    for comp in InfoIteratorProcessor("play-out traces", completed):
        trace_map = {
            "concept:name" : f"play-out trace {trace_id}"
        }
        trace_seq = list()
        leftover_guard = None 
        # build sequence of fired transitions
        ## but profilerate guards on silence, without recording them
        for fired in comp.fired():
            if fired.guard not in guard_ids:
                guard_ids[fired.guard] = guard_id
                guard_id += 1
            if fired.silent:
                if leftover_guard == None:
                    leftover_guard = PlayoutTransitionGuard(
                        fired.guard,
                        guard_ids[fired.guard]
                    )
                else:
                    leftover_guard = TransitionTreeMerge(
                        leftover_guard, 
                        PlayoutTransitionGuard(fired.guard, guard_ids[fired.guard])
                    )
            else:
                guard = PlayoutTransitionGuard(fired.guard, guard_ids[fired.guard])
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
    info("made playout log")
    return ComplexEventLog(playout_traces, dict({
        "meta:generated:by" : "pmkoalas",
        "meta:generator:version" : __version__
        }), 
        f"playout log for {model.net._name}"
    )