'''
This modules provides ways to enhance labelled Petri nets with guards, 
creating data Petri nets (DPNs).

To dervie the guards, we deduce classification problems from the given net
and then populate examples of these problems using alignments. In order to
do these steps, we rely on third-party libraries, such as pm4py and 
scikit-learn. These are not included as dependencies of this package, as 
in future we hope to implement our version of these functionalities. 

To get started on deriving guards for transitions and adding write constraints 
to form a DPN, use the following function:
    -`mine_guards_for_lpn(lpn: LabelledPetriNet, log: ComplexEventLog)`
'''

from pmkoalas.complex import ComplexEventLog
from pmkoalas.models.petrinet import LabelledPetriNet, PetriNetWithData
from pmkoalas.models.petrinet import GuardedTransition, Arc, Place
from pmkoalas.models.petrinet import PetriNetWithDataVariableType
from pmkoalas.models.petrinet import PetriNetWithDataVariable
from pmkoalas.models.petrinet import export_net_to_pnml
from pmkoalas.models.guards import Guard
from pmkoalas._logging import info,debug

from pmkoalas.enhancement.alignments import AlignmentMapping
from pmkoalas.enhancement.alignments import AlignmentMoveType, Alignment
from pmkoalas.enhancement.alignments import find_alignments_for_variants
from pmkoalas.enhancement.classification_problems import find_classification_problems

from typing import Set, Union, Literal, Tuple
from copy import deepcopy

def __find_new_place(dpn: PetriNetWithData) -> Place:
    pid = 1
    names = set([p.name for p in dpn.places])
    pids = set([p.pid for p in dpn.places])
    new_place = Place(f"p{pid}", pid)
    while new_place.name in names or new_place.pid in pids:
        pid += 1
        new_place = Place(f"p{pid}", pid)
    return new_place

def __find_new_tau(dpn: PetriNetWithData) -> GuardedTransition:
    tid = 1
    names = set([t.name for t in dpn.transitions])
    tids = set([t.tid for t in dpn.transitions])
    new_tau = GuardedTransition(
        f"tau{tid}",
        Guard("true"),
        tid,
        True
    )
    while new_tau.name in names or new_tau.tid in tids:
        tid += 1
        new_tau = GuardedTransition(
            f"tau{tid}",
            Guard("true"),
            tid,
            True
        )
    return new_tau

def __expand_by_adding_dummy_for_transition(dpn: PetriNetWithData,
        variables:Set[PetriNetWithDataVariable], t: GuardedTransition) \
    -> Tuple[PetriNetWithData, GuardedTransition]:
    """
    Expands the dpn with a silent transition to ensure that the given
    variables are free before the firing of the given transition.
    """
    new_place = __find_new_place(dpn)
    new_tau = __find_new_tau(dpn)
    ## determine what flows need to be moved
    input_flows = set([
        f 
        for f in dpn.arcs
        if f.to_node == t
    ])
    ## redirect flows to new tau 
    ## direct new place to old transition
    new_places = set(dpn.places)
    new_places.add(new_place)
    new_transitions = set(dpn.transitions)
    new_transitions.add(new_tau)
    new_flows = set()
    for f in dpn.arcs:
        if f in input_flows:
            new_flows.add(
                Arc(
                    f.from_node,
                    new_tau
                )
            )
        else:
            new_flows.add(f)
    new_flows.add(
        Arc(
            new_tau,
            new_place
        )
    )
    new_flows.add(
        Arc(
            new_place,
            t
        )
    )
    ## construct the new dpn
    new_dpn = PetriNetWithData(
        new_places, new_transitions, new_flows, dpn.name
    )
    new_dpn.set_initial_marking(dpn.initial_marking._mark)
    new_dpn.set_final_marking(dpn.final_marking._mark)
    new_dpn._detect_read_constraints(
        dict( (v.name, v.type) 
             for v in dpn.variables
            )
    )
    ### add the new write constraints
    for v in variables:
        new_dpn.add_write(new_tau, v)
    ### add old write constraints
    for t in dpn.transitions:
        for v in dpn.writes(t):
            new_dpn.add_write(t, v)
    return new_dpn, new_tau

def __expand_by_adding_dummy_from_src(dpn: PetriNetWithData, 
        variables:Set[PetriNetWithDataVariable]) -> \
        Tuple[PetriNetWithData, GuardedTransition]:
    """
    Expands the dpn with a silent transition from the source place to a new
    place with a guard that includes all variables in the given set.
    """
    # add a silent transition before source to acount for write constraints
    ## construct a new place and tau for writes
    new_place = __find_new_place(dpn)
    new_tau = __find_new_tau(dpn)
    ## find src 
    src = None
    for p in dpn.places:
        if dpn.initial_marking.contains(p):
            src = p
            break
    ## determine what flows need to be moved
    postset_of_src = dpn.initial_marking.enabled()
    postset_flows = set([
        f 
        for f in dpn.arcs
        if f.from_node == src
        and f.to_node in postset_of_src
    ])
    ## update flows with new arcs for tau 
    ## and existing pointing to the alt src place
    new_places = set(dpn.places)
    new_places.add(new_place)
    new_transitions = set(dpn.transitions)
    new_transitions.add(new_tau)
    new_flows = set()
    for f in dpn.arcs:
        if f in postset_flows:
            new_flows.add(
                Arc(
                    new_place,
                    f.to_node
                )
            )
        else:
            new_flows.add(f)
    new_flows.add(
        Arc(
            src,
            new_tau
        )
    )
    new_flows.add(
        Arc(
            new_tau,
            new_place
        )
    )
    ## construct the new dpn
    new_dpn = PetriNetWithData(
        new_places, new_transitions, new_flows, dpn.name
    )
    new_dpn.set_initial_marking(dpn.initial_marking._mark)
    new_dpn.set_final_marking(dpn.final_marking._mark)
    new_dpn._detect_read_constraints(
        dict( (v.name, v.type) 
             for v in dpn.variables
            )
    )
    ### add the new write constraints
    for v in variables:
        new_dpn.add_write(new_tau, v)
    ### add old write constraints
    for t in dpn.transitions:
        for v in dpn.writes(t):
            new_dpn.add_write(t, v)
    return new_dpn, new_tau


def _expand_dpn_for_writes(dpn: PetriNetWithData,
        ali:Alignment,
        ) -> PetriNetWithData:
    """
    Given a dpn without write constraints, this function returns a new dpn
    with write constraints added as silent transitions as needed to ensure
    that the yielded dpn is relaxed data-sound.

    Assumes that the given dpn control-flow is a workflow net, i.e. there is
    one place with an empty preset (src), and one place with an empty postset 
    (sink). The intial marking only marks the src place, and the final 
    marking only marks the sink place.
    """
    expansion = 1 
    debug_file_format = "dpn_expansion_{expansion:03d}.pnml"
    # case one : if no variables are used then return the dpn as is 
    if len(dpn.variables) == 0:
        info("expanding dpn for write constraints using case 1")
        return dpn 
    # case two : variables are used but there are no common variables between
    # transitions
    no_shared_vars = True
    seen = set()
    for t in dpn.transitions:
        if len(t.guard.variables().intersection(seen)) > 0:
            no_shared_vars = False
            break 
        seen = seen.union(t.guard.variables())
    if no_shared_vars:
        info("expanding dpn for write constraints using case 2")
        # add a silent transition before source to acount for write constraints
        ret_dpn, _ = __expand_by_adding_dummy_from_src(dpn, dpn.variables)
        export_net_to_pnml(ret_dpn, 
            debug_file_format.format(expansion=expansion),
            include_prom_bits=True
        )
        return ret_dpn 
    # case three : variables are used and there are shared variables between
    # transitions
    history = []
    info("expanding dpn for write constraints using case 3")
    ret_dpn, nt = __expand_by_adding_dummy_from_src(dpn, dpn.variables)
    history.append(nt)
    export_net_to_pnml(ret_dpn, 
            debug_file_format.format(expansion=expansion),
            include_prom_bits=True
    )
    expansion += 1
    # using the given path, travese the dpn and add constraints as needed
    path = ali.projected_path()
    debug(f"length of path used for expansion :: {path}")
    ## now traverse the path and add write constraints via silent
    ## transitions as needed, i.e. when a variable is required but
    ## does not have a free write available
    seen = set()
    free = set(ret_dpn.variables) 
    name_to_var = deepcopy(ret_dpn._variables) 
    # traverse path
    for t in path:
        curr_mark = ret_dpn.initial_marking
        for ot in history:
            assert ot in curr_mark.enabled(), f"transition was {ot} not enabled at marking {curr_mark._mark} in expanded dpn :: firable was {curr_mark.enabled()}"
            curr_mark = curr_mark.remark(ot)
        firable = curr_mark.enabled()
        firable_ids = set([t.tid for t in firable])
        assert t.tid in firable_ids, f"transition was {t.tid} not enabled at marking {curr_mark._mark} in expanded dpn :: firable was {firable}"
        fired = set( ot for ot in ret_dpn.transitions if t.tid == ot.tid)
        fired = fired.pop()
        fired_vars = ret_dpn.reads(fired)
        if len(fired_vars) > 0:
            if len(fired_vars.intersection(free)) != len(fired_vars):
                debug("expansion needed due to over overlap")
                ret_dpn, nt = __expand_by_adding_dummy_for_transition(
                    ret_dpn, fired_vars, fired
                ) 
                history.append(nt)
        # remove used variables from firing
        free = free.difference(fired_vars)       
        history.append(fired)
        # debug out expansion
        export_net_to_pnml(ret_dpn, 
            debug_file_format.format(expansion=expansion),
            include_prom_bits=True
        )
        expansion += 1
    # check that the path is still traversable
    curr_mark = ret_dpn.initial_marking
    for ot in history:
        assert ot in curr_mark.enabled() , f"transition {ot} is not firabled in expanded dpn"
        curr_mark = curr_mark.remark(ot)
    assert curr_mark.reached_final(), "final marking not reached in expanded dpn"
    return ret_dpn

DM_IGNORED_ATTRS = set(["time:", "lifecycle:"])

def mine_guards_for_lpn(lpn: LabelledPetriNet, log: ComplexEventLog,
    classification:Literal["single-bag","postset","marking","regions"]="postset",
    alignment:AlignmentMapping=None, expand_on_writes:bool=True,
    ignored_attrs:Set[str]=DM_IGNORED_ATTRS) \
    -> PetriNetWithData:
    """
    Performs decision mining on the given lpn using diagonstic information
    from alignments to annoate guards on transitions in the lpn.

    Note that the returned dpn may contain further silent transitions 
    to model write constraints by default. However, the visible language of
    the net will be the same as the given lpn.
    """
    if alignment is None:
        ali = find_alignments_for_variants(log, lpn, "pm4py")
    else:
        ali = alignment
    # obtain the classification problems
    problems = find_classification_problems(lpn, classification)
    for prob in problems:
        info(f"found problem ::\n\t{prob}")
    for trace, instances in log.__iter__():
        debug(f"{trace}")
        alignment = ali[trace]
        debug(f"{alignment}")
        i = 0
        for inst in instances:
            debug(f"contextulising on :: {inst}")
            context = alignment.contextualise(inst)
            for move in context:
                debug(f"{move}")
                if move.type == AlignmentMoveType.LOG:
                    continue
                for prob in problems:
                    if prob.reached(move.marking):
                        debug(f"adding to problem :: {prob}")
                        data = dict()
                        if move.state is not None: 
                            for k,v in move.state.data().items():
                                ignored = False
                                for ignore in ignored_attrs:
                                    if k.startswith(ignore):
                                        ignored = True 
                                        break
                                if ignored:
                                    continue
                                data[k] = v
                        prob.add_example(
                            move.transition,
                            data
                        )
            i += 1
            if i % 25 == 0 and i != 0:
                info(f"handled {i}/{len(instances)} instances...")
        for prob in problems:
            info(prob.describe())
    # solve the classification problems
    resulting = dict()
    resulting_types = dict()
    for prob in problems:
        print(prob.describe())
        mapping,var_types = prob.solve()
        # translate the solution into guards for transitions
        for k,v in mapping.items():
            # dont add trivial guards
            if v.trivial():
                continue
            # add the guard to the mapping
            if k not in resulting:
                resulting[k] = v
            else:
                resulting[k] = Guard( 
                    f"({str(resulting[k])}) || ({str(v)})"
                )
        # consider the variables across problems
        # these variables should have consistent types across problems
        for k,v in var_types.items():
            if k not in resulting_types.keys():
                resulting_types[k] = v
            else:
                past = resulting_types[k]
                if past != v:
                    raise Exception(
                        "variable type inconsistent over problems :: " \
                        + f"{k} :: {past} != {v}"                                    
                    )
    # translate the mined guards to the dpn
    mapping_trans = dict()
    for t in lpn.transitions:
        if (t in resulting.keys()):
            mapping_trans[t] = GuardedTransition(
                t.name,
                resulting[t],
                t.tid,
                t.silent
            )
        else:
             mapping_trans[t] = GuardedTransition(
                t.name,
                Guard("true"),
                t.tid,
                t.silent
            )
    new_flows = set()
    for f in lpn.arcs:
        new_src = f.from_node
        new_dest = f.to_node
        if new_src in mapping_trans.keys():
            new_src = mapping_trans[new_src]
        if new_dest in mapping_trans.keys():
            new_dest = mapping_trans[new_dest]
        new_flows.add(
            Arc(
                new_src,
                new_dest
            )
        )
    dpn = PetriNetWithData(
        lpn.places,
        [ 
            mapping_trans[t]
            for t 
            in lpn.transitions
        ],
        new_flows,
        "Decision mined net of :: "+lpn.name
    )
    dpn.set_final_marking(lpn.final_marking._mark)
    dpn.set_initial_marking(lpn.initial_marking._mark)
    # handle adding read constraints
    mapping = dict()
    for k,v in resulting_types.items():
        if v == str: 
            mapping[k] = PetriNetWithDataVariableType.CATEGORICAL
        elif v == int:
            mapping[k] = PetriNetWithDataVariableType.NUMERIC
        elif v == float:
            mapping[k] = PetriNetWithDataVariableType.NUMERIC
        else:
            raise Exception(f"unsupported variable type :: {v} for variable {k}")
    dpn._detect_read_constraints(
        mapping
    )
    # expand the dpn to include write constraints
    export_net_to_pnml(dpn, 'dpn_expansion_000.pnml', 
                       include_prom_bits=True)
    if (expand_on_writes):
        # find the alignment with the longest projected path
        longest = -1
        long = None
        for ali in ali._storage.values():
            path = ali.projected_path()
            if len(path) > longest:
                long = ali 
                longest = len(path)
        # expand using the longest projected path
        dpn = _expand_dpn_for_writes(dpn, ali=long)
    return dpn
