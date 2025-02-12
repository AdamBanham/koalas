from pmkoalas.simple import Trace, EventLog
from pmkoalas.complex import ComplexEvent,ComplexTrace,ComplexEventLog
from pmkoalas.models.petrinet import LabelledPetriNet,Transition, PetriNetMarking
from pmkoalas._logging import debug, info

from enum import Enum
from typing import Any, Literal, List, Union, Dict
from copy import deepcopy
from dataclasses import dataclass

class AlignmentMoveType(Enum):
    """
    Enum to represent the type of move in an alignment.
    """
    SYNC = 1
    MODEL = 2
    LOG = 3

@dataclass(frozen=True)
class AlignmentMove():
    """
    Helper class to represent a move in an alignment.
    """
    type:AlignmentMoveType
    transition:Transition
    activity:str
    marking:PetriNetMarking
    state:ComplexEvent=None

    def __str__(self) -> str:
        return f"<{self.type}" \
            + f"\{self.activity}\{self.transition}"\
            + f"\{self.marking}"\
            + (f"\{self.state}>" if self.state is not None else ">")
    
    def is_sync(self) -> bool:
        return self.type == AlignmentMoveType.SYNC
    
    def is_model(self) -> bool:
        return self.type == AlignmentMoveType.MODEL
    
    def is_log(self) -> bool:
        return self.type == AlignmentMoveType.LOG
    
    def get_event(self) -> ComplexEvent:
        if (self.is_model()):
            raise ValueError("Model moves do not have events.")
        if self.state is not None:
            return self.state
        return ComplexEvent(self.activity, dict())
    
    def get_transition(self) -> Transition:
        if (self.is_log()):
            raise ValueError("Log moves do not have transitions.")
        return self.transition
    
    # data functions 
    def __repr__(self) -> str:
        return f"AlignmentMove( "\
            +f"{repr(self.type)},{repr(self.transition)}, "\
            +f"{repr(self.activity)},{repr(self.marking)},{repr(self.state)})"""
    

class Alignment():
    """
    Helper class to represent an alignment between a trace and a petri net.
    Stores the marking for each step, the transition fired, and can be used 
    to iterate through the datastates before each firing.
    """

    def __init__(self, moves:List[AlignmentMove]) -> None:
        self._sequence = deepcopy(moves)

    def moves(self) -> List[AlignmentMove]:
        """
        Returns the sequence of moves in this alignment.
        """
        return deepcopy(self._sequence)

    def contextualise(self, trace:Union[Trace,ComplexTrace]) \
        -> List[AlignmentMove]:
        """
        Given a trace, returns moves of this alignment with the context of
        the given trace.
        """
        ret = []
        trace_type = isinstance(trace, ComplexTrace)
        state = ComplexEvent("I", dict())
        eid = 0 
        for move in self.moves():
            debug(move)
            if move.is_sync():
                if trace_type:
                    assert move.activity == trace[eid].activity()
                else:
                    assert move.activity == trace[eid]
                if trace_type:
                    state = ComplexEvent(
                        trace[eid].activity(), state.data()
                    )
                else:
                    state = ComplexEvent(
                        trace[eid], state.data()
                    )
                ret.append(
                    AlignmentMove(
                        move.type,
                        move.transition,
                        move.activity,
                        move.marking,
                        state 
                    )
                )
                if trace_type:
                    data = state.data()
                    data.update(trace[eid].data())
                    state = ComplexEvent(
                        trace[eid].activity(), data
                    )
                eid += 1
            elif move.is_model():
                state = ComplexEvent(
                    "missing", state.data()
                )
                ret.append( 
                    AlignmentMove(
                        move.type,
                        move.transition,
                        move.activity,
                        move.marking,
                        state
                    )
                )
            elif move.is_log():
                debug(f"move {move.activity} trace {trace[eid]}")
                if trace_type:
                    state = ComplexEvent(
                        trace[eid].activity(), state.data()
                    )
                else:
                    state = ComplexEvent(
                        trace[eid], state.data()
                    )
                if trace_type:
                    assert move.activity == trace[eid].activity()
                else:
                    assert move.activity == trace[eid]
                ret.append(
                    AlignmentMove(
                        move.type,
                        move.transition,
                        move.activity,
                        move.marking,
                        state
                    )
                )
                if trace_type:
                    data = state.data()
                    data.update(trace[eid].data())
                    state = ComplexEvent(
                        trace[eid].activity(), data
                    )
                eid += 1
            else:
                raise ValueError(f"Unknown move type {move.type}")
        assert eid == len(trace)
        assert len(ret) == len(self._sequence)
        assert ret[-1].marking.remark(ret[-1].transition).reached_final() == True
        return ret
    
    def projected_path(self) -> List[Transition]:
        """
        Returns the sequence of transitions in this alignment.
        """
        ret = [] 
        for move in self._sequence:
            if not move.is_log():
                ret.append(move.transition)
        return ret 
    
    def projected_trace(self) -> List[str]:
        """
        Returns the sequence of activities in this alignment.
        """
        ret = [] 
        for move in self.moves():
            if not move.is_model():
                ret.append(move.activity)
        return ret
    
    # data model functions
    def __str__(self) -> str:
        return "|"+"-->".join( str(m.type) for m in self.moves() )+"|"
    
    def __repr__(self) -> str:
        return f"Alignment({repr(self.moves())})"

class AlignmentMapping():
    """
    Helper class to handle the retrival of an optimal alignment for a given
    variant.
    """

    def __init__(self, init:Dict[Trace, Alignment]=None) -> None:
        self._locked = False
        if init is None:
            self._storage:Dict[Trace, Alignment] = dict()
        else:
            self._storage = init

    def lock(self) -> None:
        self._locked = True

    def __setitem__(self, variant: Trace, ali: Alignment) -> None:
        if (not self._locked):
            if not isinstance(variant, Trace):
                raise ValueError("Variant must be a Trace object.")
            if not isinstance(ali, Alignment):
                raise ValueError("Ali must be an Alignment object.")
            self._storage[variant] = ali
        else:
            raise ValueError("Mapping is locked, cannot add new items.")

    def __getitem__(self,variant:Trace) -> Alignment:
        if isinstance(variant, Trace):
            return self._storage[variant]
        
    # data model functions
    def __repr__(self):
        return f"AlignmentMapping(\n\t{repr(self._storage)}\n)"

def find_alignments_for_variants(log:Union[EventLog, ComplexEventLog], lpn:LabelledPetriNet, 
        engine:Literal["pm4py"]) -> AlignmentMapping:
    """
    Constructs a mapping from the variants of the log to an optimal 
    alignment through the given lpn. 
    
    By default attempts to use pm4py alignment techniques.
    """
    if isinstance(log, ComplexEventLog):
        log = EventLog(log.simple_language())
    else:
        log = EventLog(log.language())

    if engine == "pm4py":
        return find_alignments_for_variants_pm4py(log, lpn)
    else:
        raise ValueError(f"Engine {engine} not supported.")
    
def find_alignments_for_variants_pm4py(log:EventLog, lpn:LabelledPetriNet) \
    -> AlignmentMapping:
    """
    Using pm4py alignments implementions, finds the equivalent runs through
    the given lpn in pmkoalas format.
    """
    from importlib.util import find_spec
    ret = AlignmentMapping()

    if find_spec("pm4py"): 
        from pm4py.objects.log.importer.xes import importer as xes_importer
        from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
        from pm4py import read_pnml

        from pmkoalas.export import export_to_xes_simple
        from pmkoalas.models.petrinet import export_net_to_pnml, parse_pnml_into_lpn

        from tempfile import TemporaryDirectory
        from os.path import join

        with TemporaryDirectory() as dir:
            log_file = join(dir, "log.xes")
            net_file = join(dir, "net.pnml")
            export_to_xes_simple(log_file, log)
            export_net_to_pnml(lpn, net_file, True)
            # pass net and log to pm4py
            net, im, fm = read_pnml(net_file, auto_guess_final_marking=True)
            debug(fm)
            debug(im)
            knet = parse_pnml_into_lpn(net_file, use_localnode_id=False)
            export_net_to_pnml(knet, "dummy.pnml", True)
            plog = xes_importer.apply(log_file)
            # call the dogs breakfeast of alignment tuples from pm4py
            aligned_traces = alignments.apply(plog, net, im, fm, 
                variant=alignments.Variants.VERSION_DIJKSTRA_LESS_MEMORY, 
                parameters={"ret_tuple_as_trans_desc": True})
            # manually translate between pm4py and pmkoalas nets
            mapping = dict()
            for index, trace in enumerate(plog):
                debug("****")
                aligned_trace = aligned_traces[index]
                variant = [ ev["concept:name"] for ev in trace ]
                marking = knet.initial_marking
                debug(f"starting marking :: {marking}")
                tlen = 0
                debug(f"{variant}")
                evariant = []
                moves = []
                for step in aligned_trace['alignment']:
                    explict_step = step[0]
                    implicit_step = step[1]
                    tid = None
                    tname = None
                    ename = None
                    alitype = None
                    if (">>" not in explict_step):
                        debug(f"sync move")
                        tid = explict_step[1]
                        ename = implicit_step[0]
                        tname = implicit_step[1]
                        alitype = AlignmentMoveType.SYNC
                        tlen += 1
                        assert tid is not None, f"Expected either tid or tname to be set, got {tid} {tname}"
                    elif (">>" in explict_step):
                        if ">>" == explict_step[0]:
                            tid = explict_step[1]
                            tname = implicit_step[1]
                            alitype = AlignmentMoveType.MODEL
                            debug(f"model move")
                            assert tid is not None, f"Expected either tid or tname to be set, got {tid} {tname}"
                        else:
                            debug(f"log move")
                            ename = implicit_step[0]
                            alitype = AlignmentMoveType.LOG
                            tlen += 1
                    if ename is not None:
                        evariant.append(ename)

                    fire = None
                    if tid is not None:
                        debug(f"looking for :: {tid} {tname} {ename}")
                        firable = marking.can_fire()
                        debug(f"{firable}")
                        for trans in firable:
                            if trans.nodeId == tid:
                                fire = trans
                                break 
                            if trans.name == tname:
                                fire = trans
                                break
                        if (fire is not None):
                            debug(f"firing :: {fire}")
                        
                    debug(f"{step}")
                    move = AlignmentMove(
                        alitype,
                        fire,
                        ename,
                        marking,
                        None
                    )
                    if fire is not None:
                        marking = marking.remark(fire)
                    debug(f"next marking :: {marking}")
                    moves.append(move)
                debug(evariant, tlen)
                assert tlen == len(variant)
                assert Trace(evariant) == Trace(variant)
                assert marking.reached_final() == True, f"Should have reached final marking, expected {lpn.final_marking}, got {marking}"
                debug("****")
                debug(moves)
                debug("****")
                ret[Trace(variant)] = Alignment(moves)
    else:
        raise ImportError("pm4py (~2.7) is required for this engine to function.")

    ret.lock()
    return ret