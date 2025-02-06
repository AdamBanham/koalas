'''
This module provide a data structure for representing a transition system.

Transition systems are useful for understanding the marking system of a
Petri net. The module provides a function to find the marking system,
though the function `generate_marking_system` given a `LabelledPetriNet`.
'''

from pmkoalas.models.petrinet import LabelledPetriNet, PetriNetMarking
from pmkoalas._logging import debug

from typing import Set, Tuple, Union, Iterable,List
from copy import deepcopy
from dataclasses import dataclass, field
from itertools import permutations

@dataclass(frozen=True)
class TSState():
    name: str
    src: object=None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"TSState(name={repr(self.name)})"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TSState):
            return False
        return self.name == value.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
@dataclass(unsafe_hash=True, frozen=True)
class TSEvent():    
    name: str

    def __str__(self) -> str:
        return self.name if type(self.name) == str else str(self.name)

    def __repr__(self) -> str:
        return f"TSEvent(name={repr(self.name)})"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TSEvent):
            return False
        return self.name == value.name
    
@dataclass(unsafe_hash=True, frozen=True)
class TSTransition():
    source: TSState
    event: TSEvent
    target: TSState

    def __str__(self) -> str:
        return f"{self.source} --{self.event}--> {self.target}"

    def __repr__(self) -> str:
        return f"TSTransition(source={repr(self.source)}," +\
            f"event={repr(self.event)}, target={repr(self.target)})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TSTransition):
            return False
        return (self.source == value.source and 
                self.event == value.event and 
                self.target == value.target)

@dataclass(frozen=True) 
class TSRegion():
    states: Set[TSState]
    colour: str = "red"

    def __str__(self) -> str:
        return f"States: {self.states}"

    def __repr__(self) -> str:
        return f"TSRegion(states={repr(self.states)})"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TSRegion):
            return False
        return (self.states == value.states)
    
    def __hash__(self) -> int:
        return hash(frozenset(self.states))

class TransitionSystem:
    """
    A transition system consiting of states and transitions.
    Transitions are labelled with an event.
    """

    def __init__(self, states:Iterable[TSState] , events:Iterable[TSEvent], 
                 transitions:Iterable[TSTransition]) -> None:
        self._states = set(s for s in states)
        self._events = set(e for e in events)
        self._transitions = set(t for t in transitions)

    @property
    def states(self) -> Set[TSState]:
        return deepcopy(self._states)

    @property
    def events(self) -> Set[TSEvent]:
        return deepcopy(self._events)

    @property
    def transitions(self) -> Set[TSTransition]:
        return deepcopy(self._transitions)
    
    def is_region(self, region: TSRegion) -> bool:
        """Return True if the region is a subset of the transition system."""
        return is_region(region, self.subgraph_of_region(region))
    
    def postset(self, other: Union[TSState,TSRegion]) -> Set[TSTransition]:
        """Return the set of transitions that are postset to a state."""
        if isinstance(other, TSState):
            return set([ 
                t.target for t in self.transitions if t.source == other ])
        elif isinstance(other, TSRegion):
            return set([ 
                t.target for t in self.transitions 
                if t.source in other.states and t.target not in other.states 
            ])
        else:
            raise TypeError("Expected TSState or TSRegion, but was given :: "
                            + f"{type(other)}")
        
    def preset(self, other: Union[TSState,TSRegion]) -> Set[TSTransition]:
        """Return the set of transitions that are preset to a state."""
        if isinstance(other, TSState):
            return set([ 
                t.source for t in self.transitions if t.target == other ])
        elif isinstance(other, TSRegion):
            return set([ 
                t.source for t in self.transitions 
                if t.source not in other.states and t.target in other.states 
            ])
        else:
            raise TypeError("Expected TSState or TSRegion, but was given :: "
                            + f"{type(other)}")
        
    def dotform(self, regions:List[TSRegion]=[]) -> str:
        """Return a string representation of the transition system in DOT format."""
        return create_dot_representation(self,regions)
    
    def initial_states(self) -> Set[TSState]:
        """Return the set of initial states."""
        return set([ s for s in self.states if len(self.preset(s)) == 0 ])
    
    def final_states(self) -> Set[TSState]:
        """Return the set of final states."""
        return set([ s for s in self.states if len(self.postset(s)) == 0 ])

    def subgraph_of_region(self, region: TSRegion) -> 'TransitionSystem':
        """Return a subgraph of the transition system within a region."""
        states = set([ s for s in self.states if s in region.states ])
        transitions = set([ t for t in self.transitions 
                           if t.source in states or t.target in states ])
        events = [ t.event for t in transitions ]
        return TransitionSystem(states, events, transitions)  


    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TransitionSystem):
            return False
        return (self._states == value._states and 
                self._events == value._events and 
                self._transitions == value._transitions)

    def __hash__(self) -> int:
        return hash((frozenset(self._states), 
                     frozenset(self._events), 
                     frozenset(self._transitions)))
    
    def __str__(self) -> str:
        return (f"TransitionSystem(states={str(self._states)}, "+ 
                f"events={str(self._events)}, transitions={str(self._transitions)})")

    def __repr__(self) -> str:
        return (f"TransitionSystem(states={repr(self._states)}, "+
                f"events={repr(self._events)}, transitions={repr(self._transitions)})")

def is_internal(event: TSEvent, region: TSRegion, ts:TransitionSystem) -> bool:
    """Return True if the event internal to a region."""
    pos = set([ t for t in ts.transitions if t.event == event ])
    pos = set([ t for t in pos 
               if t.source in region.states and t.target in region.states 
    ])
    return len(pos) > 0

def is_external(event: TSEvent, region: TSRegion, ts:TransitionSystem) -> bool:
    """Return True if the event external to a region."""
    pos = set([ t for t in ts.transitions if t.event == event ])
    pos = set([ t for t in pos 
               if t.source not in region.states and t.target not in region.states 
    ])
    return len(pos) > 0

def is_entering(event: TSEvent, region: TSRegion, ts:TransitionSystem) -> bool:
    """Return True if the event is entering a region."""
    pos = set([ t for t in ts.transitions if t.event == event ])
    pos = set([ t for t in pos 
               if t.source not in region.states and t.target in region.states 
    ])
    return len(pos) > 0

def is_exiting(event: TSEvent, region: TSRegion, ts:TransitionSystem) -> bool:
    """Return True if the event is exiting a region."""
    pos = set([ t for t in ts.transitions if t.event == event ])
    pos = set([ t for t in pos 
               if t.source in region.states and t.target not in region.states 
    ])
    return len(pos) > 0

def is_region(region: TSRegion, ts:TransitionSystem) -> bool:
    """Return True if the region is a subset of the transition system."""
    debug(f"checking region :: {region}")
    for event in ts.events:
        entering = is_entering(event, region, ts)
        exiting = is_exiting(event, region, ts)
        debug(event, entering, exiting)
        if entering and exiting:
            return False
        elif entering:
            internal = is_internal(event, region, ts)
            external = is_external(event, region, ts)
            debug(internal, external)
            if (internal or external or exiting):
                return False
        elif exiting:
            internal = is_internal(event, region, ts)
            external = is_external(event, region, ts)
            debug(internal, external)
            if (internal or external or entering):
                return False
        else:
            continue
    return True

def conv_marking_to_str(marking:PetriNetMarking) -> str:
        ret = "["
        order = sorted(marking.keys(), key=lambda x: x.name)
        for p in order:
            freq = marking[p]
            if freq == 0:
                continue
            elif freq == 1:
                ret += f"{p.name},"
            else:
                ret += f"{p.name}^{freq},"
        return ret[:-1] + "]"

def generate_marking_system(net:LabelledPetriNet,
                            use_trans_id=False) -> TransitionSystem:
    """
    Generates a transition system for the markings of a Petri net.
    """

    working = [net.initial_marking]
    done = []
    seen = set()
    final = []
    while len(working) > 0:
        debug(f"{len(working)=} {len(done)=}")
        marking = working.pop(0)
        firable = marking.can_fire()
        if (len(firable) == 0):
            final.append(deepcopy(marking))
        for t in firable:
            new_marking = marking.remark(t)
            done.append(
                (
                 marking,
                 t.tid if use_trans_id else t.name,
                 new_marking
                )
            )
            debug(new_marking, seen)
            if new_marking in seen:
                continue
            working.append(new_marking)
        seen.add(marking)

    S = set( 
        TSState(conv_marking_to_str(mark._mark), mark)
        for mark in seen
    )
    T = [
        TSTransition(
            TSState(conv_marking_to_str(src._mark), src), 
            TSEvent(event), 
            TSState(conv_marking_to_str(tgt._mark), tgt)
        )
        for src, event, tgt 
        in done
    ]
    E = set(
        TSEvent(event)
        for _, event, _ in done
    )
    return TransitionSystem(S, E, T)

@dataclass
class DebugHistoryState:
    selected: TSRegion
    step: str
    candidates: set=None
    keepers: set=None
    growths: set=None
    maximal_growths: set=None
    level: int=0

    def get_regions(self) -> List[TSRegion]:
        regions = [TSRegion(self.selected.states, "gray")]
        if self.candidates:
            regions.append(TSRegion(self.candidates, "blue"))
        if self.keepers:
            regions.extend([TSRegion(keeper, "green") for keeper in self.keepers])
        if self.growths:
            regions.extend([TSRegion(growth.states, "red") for growth in self.growths])
        if self.maximal_growths:
            regions.extend([TSRegion(growth.states, "orange") for growth in self.maximal_growths])
        return regions

@dataclass
class DebugHistory:
    states: List[DebugHistoryState]=field(default_factory=list)

    def start(self, selected: TSRegion):
        self.states.append(DebugHistoryState(selected, "init"))

    def insert(self, selected, step, candidates=None, keepers=None, 
               growths=None, maximal_growths=None, level=None):
        self.states.append(DebugHistoryState(selected, step, candidates, 
            keepers, growths, maximal_growths, level))
    
    @property
    def curr(self) -> DebugHistoryState:
        return self.states[-1] if self.states else None

    @property
    def step(self) -> str:
        return self.curr.step if self.curr else None

    @property
    def candidates(self) -> set:
        return self.curr.candidates if self.curr else None

    @property
    def keepers(self) -> set:
        return self.curr.keepers if self.curr else None

    @property
    def growths(self) -> set:
        return self.curr.growths if self.curr else None

    @property
    def maximal_growths(self) -> set:
        return self.curr.maximal_growths if self.curr else None

    @property
    def level(self) -> int:
        return self.curr.level if self.curr else None
    
    def is_started(self) -> bool:
        return len(self.states) > 0
    
    def __str__(self): 
        return "\n".join(str(state) for state in self.states)

def grow_region(selected: TSRegion, ts: TransitionSystem, 
                prev: Set[TSState]=set(),
                CONTROLLER=None) -> TSRegion:
    """
    Iteratively grows a possible candidate region.
    """
    if CONTROLLER is None:
        CONTROLLER = DebugHistory()
    if (not CONTROLLER.is_started()):
        CONTROLLER.start(selected)
    else:
        CONTROLLER.insert(selected, "recurse", level=CONTROLLER.level+1)
    level = CONTROLLER.level
    # case 1: check for a single selected
    debug("C1")
    if len(selected.states) == 1:
        # get the postset of the selected state
        postset = ts.postset(selected)
        # STOP if postset contains one option
        if (len(postset) <= 1):
            debug("STOP C1")
            return deepcopy(selected)
    # otherwise, continue to grow using the postset
    candidates = set()
    for state in selected.states:
        candidates = candidates.union(ts.postset(state))
    candidates = candidates.difference(selected.states)
    candidates = candidates.difference(prev)
    if (len(candidates) <= 1):
        debug("STOP C1")
        return deepcopy(selected)
    CONTROLLER.insert(selected, "C1", candidates=candidates, level=level)
    debug("C1 | ", candidates)
    if (len(candidates) == 0):
        debug("STOP C1")
        return selected
    # case 2: check the union of selected and candidates is a region
    debug("C2")
    if ts.is_region(TSRegion(selected.states.union(candidates))):
        # recurse on grow with the new selected
        debug("C2 | reursing on union")
        r = grow_region(TSRegion(selected.states.union(candidates)), ts, prev.union(candidates))
        CONTROLLER.insert(r, "ret C2", candidates=candidates, level=level)
        return r
    # case 3: check if there is an non-empty subset of candidates that is a region
    debug("C3")
    max_l = min(1,len(candidates)-1)
    keepers = set()
    while max_l > 0:
        powerset = set(p for p in permutations(candidates, max_l))
        debug("C3 | ", powerset)
        for subset in powerset:
            if ts.is_region(TSRegion(selected.states.union(subset))):
                # recurse on grow with the new selected
                debug("C3 | keeping ", subset)
                keepers.add(subset)
        max_l -= 1
    # stop if no subset can grow the region
    CONTROLLER.insert(selected, "C3-keppers", 
        keepers= keepers, 
    level=level)
    if len(keepers) < 1:
        debug("STOP C3")
        CONTROLLER.insert(selected, "ret C3", level=level)
        return deepcopy(selected)
    # case 4: recurse on the candidates that can grow the region
    debug("C4")
    debug("C4 | keppers :: ", keepers)
    growths = set( 
        grow_region(TSRegion(selected.states.union(subset)), ts, prev.union(candidates)) 
        for subset in keepers 
    )
    debug("C4 | growths :: ", growths)
    maximal_growths = set(
        growth for growth in growths 
        if not any(growth.states.issubset(other.states) 
                   for other in growths if other != growth)
    )
    CONTROLLER.insert(selected, f"C4 (max={len(maximal_growths)})", 
        growths=growths, maximal_growths=maximal_growths, level=level)
    debug("C4 | maximals :: ", maximal_growths)
    if (len(maximal_growths) == 1):
        debug("STOP C4")
        r = list(maximal_growths).pop()
        CONTROLLER.insert(r, "ret C4 | a", level=level)
        return r
    # else consider the union of growths
    big_growth = set()
    for growth in maximal_growths:
        debug("C4 | unioning ", growth)
        big_growth = big_growth.union(growth.states)
    if ts.is_region(TSRegion(big_growth)):
        debug("STOP C4 | union")
        r = TSRegion(big_growth)
        CONTROLLER.insert(r, "ret C4 | b", level=level)
        return r
    # else return one of the largest growths
    biggest = max(maximal_growths, key=lambda x: len(x.states))
    big_growths = set(g for g in maximal_growths if len(g.states) == len(biggest.states))
    debug("STOP C4 | choice")
    r = list(big_growths).pop()
    CONTROLLER.insert(r, "ret C4 | d", level=level)
    return r

def find_regions(start_state: TSState, ts: TransitionSystem) -> List[TSRegion]:
    colours = ["orange", "purple", "darkblue", "darkgreen", "blue", 
           "darkgoldenrod", "aquamarine4", "burlywood4", "cadetblue",]
    ret = []
    used = set([start_state])
    ret.append(TSRegion({start_state}, "red"))
    growth = grow_region(TSRegion({start_state}), ts)
    c = colours.pop(0)
    ret.append(TSRegion(growth.states, c))
    colours = colours + [c]
    unused_postset = ts.postset(start_state).difference(growth.states)
    used = used.union(growth.states)
    while len(unused_postset) > 0:
        options = [ 
            (state, sum([
                1 
                for r in ret 
                if state in ts.postset(r)
            ]))
            for state in unused_postset
        ]
        options.sort(key=lambda x: x[1])
        state = options.pop()[0]
        ret.append(TSRegion({state}, "red"))
        growth = grow_region(TSRegion({state}), ts, used)
        c = colours.pop(0)
        ret.append(TSRegion(growth.states, c))
        colours = colours + [c]
        unused_postset = unused_postset.difference(growth.states)
        used = used.union(growth.states)
    # now look for the next unused state 
    missing = ts.states.difference(used)
    while len(missing) > 0:
        options = [ 
            (state, sum([
                1 
                for r in ret 
                if state in ts.postset(r)
            ]))
            for state in missing
        ]
        options.sort(key=lambda x: x[1])
        state = options.pop()[0]
        ret.append(TSRegion({state}, "red"))
        growth = grow_region(TSRegion({state}), ts, used)
        c = colours.pop(0)
        ret.append(TSRegion(growth.states, c))
        colours = colours + [c]
        used = used.union(growth.states)
        missing = missing.difference(used)
    return ret

def create_dot_representation(ts:TransitionSystem, regions:List[TSRegion]=[]) -> str:
    """
    Return a string representation of the transition system in DOT format.
    Will use the given regions to highlight states in the graph.
    """
    dot = "digraph G {\n"
    dot += """
    rankdir="LR";
    node[fontcolor="white", width=1, fontsize=14, fontname="arial bold",shape=circle,fillcolor=black,style="filled"];
    bgcolor="none";
    edge[fontsize=16, fontname="arial bold", penwidth=4];
""" 
    # walk states from initial to final 
    seen = list()
    todo = list(ts.initial_states())
    while len(todo) > 0:
        state = todo.pop(0)
        if state in seen:
            continue
        seen.append(state)
        regs = [region for region in regions if state in region.states]
        if len(regs) > 0:
            colourlist = ""
            step = 1 / len(regs)
            r = regs.pop()
            colourlist += f'{r.colour}'
            while len(regs) > 0:
                r = regs.pop()
                colourlist += f';{step}:{r.colour}'
            dot += f'\t"{state}" [fillcolor="{colourlist}"];\n'
        else:
            dot += f'\t"{state}";\n'
        todo.extend(ts.postset(state))
    assert set(seen) == ts.states

    checked = set()
    for s in seen:
        for transition in [t for t in ts.transitions if t.source == s]:
            if transition.target in checked:
                dot += f'\t"{transition.target}" -> "{transition.source}" [label="{transition.event}", color="gray", dir="back"];\n'
            else:
                dot += f'\t"{transition.source}" -> "{transition.target}" [label="{transition.event}"];\n'
        checked.add(s)
    return dot + "}\n"