'''
This modules provides ways to enhance labelled Petri nets with guards, 
creating data Petri nets (DPNs).

To dervie the guards, we deduce classification problems from the given net
and then populate examples of these problems using alignments. In order to
do these steps, we rely on third-party libraries, such as pm4py and 
scikit-learn. These are not included as dependencies of this package. 
In future we hope to implement our version of these functionalities. 

To get started on deriving guards for transitions and adding write constraints 
to form a DPN, use the following function:
    -`mine_guards_for_lpn(lpn: LabelledPetriNet, log: ComplexEventLog)`
        - if you would like to include write constraints, set the parameter
          `expand_on_writes` to True.
        - Several expansion strategies are available, and the default is to
          an earnst expansion strategy, others can be selected using the 
          `expansion` parameter.
'''

from pmkoalas.complex import ComplexEventLog
from pmkoalas.models.petrinet import LabelledPetriNet, PetriNetWithData
from pmkoalas.models.petrinet import GuardedTransition, Arc, Place
from pmkoalas.models.petrinet import PetriNetWithDataVariableType
from pmkoalas.models.petrinet import PetriNetWithDataVariable
from pmkoalas.models.petrinet import PetriNetMarking
from pmkoalas.models.petrinet import export_net_to_pnml
from pmkoalas.models.petrinet import preset_of_transition, postset_of_transition
from pmkoalas.models.guards import Guard
from pmkoalas._logging import info,debug, InfoIteratorProcessor
from pmkoalas._struct import Stack

from pmkoalas.conformance.alignments import AlignmentMapping, AlignmentMove
from pmkoalas.conformance.alignments import AlignmentMoveType, Alignment
from pmkoalas.conformance.alignments import find_alignments_for_variants
from pmkoalas.enhancement.classification_problems import find_classification_problems
from pmkoalas.enhancement.classification_problems import ClassificationProblem
from joblib import Parallel, delayed


from typing import Set, Union, Literal, Tuple, Dict, List
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

def __dup_trans(trans:Set[GuardedTransition], t:GuardedTransition) -> GuardedTransition:
    tid = 1
    tids = set([t.tid for t in trans])
    new_trans = GuardedTransition(
        t.name,
        Guard("true"),
        tid,
        t.silent
    )
    while new_trans.tid in tids:
        tid += 1
        new_trans = GuardedTransition(
            t.name,
            Guard("true"),
            tid,
            t.silent
        )
    return new_trans

def __find_new_tau(dpn: PetriNetWithData) -> GuardedTransition:
    tid = 1
    names = set([t.name for t in dpn.transitions])
    tids = set([t.tid for t in dpn.transitions])
    new_tau = GuardedTransition(
        f"tau_{tid}",
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

def __rebuild_net(old:PetriNetWithData, 
                  places:Set[Place], 
                  transitions:Set[GuardedTransition], 
                  flows:Set[Arc], 
    ) -> PetriNetWithData:
    """
    Rebuilds a PetriNetWithData object from the given sets of places, 
    transitions, and flows. 
    """
    ret = PetriNetWithData(
        places, transitions, flows, old.name
    )
    ret.set_initial_marking(old.initial_marking._mark)
    ret.set_final_marking(old.final_marking._mark)
    ret._detect_read_constraints(
        dict( (v.name, v.type) 
             for v in old.variables
            )
    )
    for t in old.transitions:
        for v in old.writes(t):
            ret.add_write(t, v)
    return ret

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
            if src is not None:
                raise Exception("multiple source places detected, expected"
                                + " a workflow net with one input place.")
            src = p
    ## add new tau and new src to old src
    new_places = set(dpn.places)
    new_places.add(new_place)
    new_transitions = set(dpn.transitions)
    new_transitions.add(new_tau)
    new_flows = set(dpn.arcs)
    new_flows.add(
        Arc(
            new_place,
            new_tau
        )
    )
    new_flows.add(
        Arc(
            new_tau,
            src
        )
    )
    ## construct the new dpn
    new_dpn = __rebuild_net(dpn, new_places, new_transitions, new_flows)
    new_dpn.set_initial_marking({new_place:1})
    ### add the new write constraints
    for v in variables:
        new_dpn.add_write(new_tau, v)
    return new_dpn, new_tau

def __prefix_expansion(N:PetriNetWithData, f:GuardedTransition,
                       ) -> PetriNetWithData:
    """
    Expands the given net N by adding a silent transition and a new place,
    the silent transition has all writes needed for f to be satisfied, and 
    the new place is swapped with a place from the preset of f. 
    """
    new_place = __find_new_place(N)
    new_tau = __find_new_tau(N)
    ## select a place from the preset of f
    swap = list(preset_of_transition(N, f)).pop()
    vars = N.reads(f)
    ## construct the new net
    new_places = set(N.places)
    new_places.add(new_place)
    new_transitions = set(N.transitions)
    new_transitions.add(new_tau)
    new_flows = set(N.arcs).difference(set( 
        [Arc(swap, f)]
    ))
    new_flows.add(
        Arc(
            swap,
            new_tau
        )
    )
    new_flows.add(
        Arc(
            new_tau,
            new_place
        )
    )
    new_flows.add(
        Arc(
            new_place,
            f
        )
    )
    ## construct the new dpn
    ret = __rebuild_net(N, new_places, new_transitions, new_flows)
    ### add the new write constraints
    for v in N.reads(f):
        ret.add_write(new_tau, v)
    return ret, new_tau

def __add_expansion(N:PetriNetWithData, f:GuardedTransition, 
                    vars:Set[PetriNetWithDataVariable]) \
    -> PetriNetWithData:
    """
    Adds all variables as write constraints to the transition f for the 
    given net N. 
    """
    for var in vars:
        N.add_write(f, var)
    return N

def __crashout(fired:GuardedTransition, 
               N:PetriNetWithData,
               M:PetriNetMarking,
               history:List[GuardedTransition],):
    if (fired not in M.enabled()):
        info("crashout triggered")
        export_net_to_pnml(N, "reset_crash_expansion.pnml", include_prom_bits=True)
        with open("reset_crash_expansion_history.stderr", "w") as f:
            f.write(repr(history))
            f.write("\nFired::\n")
            f.write(repr(fired))
            f.write("\nMarkings::\n")
            f.write(str(M))
            f.write("\n")
            f.write(repr(M))
            f.write("\n")
            f.write(repr(M.enabled()))


def _earnst_expansion(dpn: PetriNetWithData,
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
        return ret_dpn 
    # case three : variables are used and there are shared variables between
    # transitions
    history = []
    info("expanding dpn for write constraints using case 3")
    # add silient initialising transition for variables
    ret_dpn, nt = __expand_by_adding_dummy_from_src(dpn, dpn.variables)
    expansion += 1
    # using the given path, travese the dpn and add constraints as needed
    path = ali.projected_path()
    # add new tau to path
    path = Stack(path[::-1])
    path.push(nt)
    info(f"length of path used for expansion :: {path}")
    ## now traverse the path and add write constraints via silent
    ## transitions as needed, i.e. when a variable is required but
    ## does not have a free write available
    seen = set()
    f = None
    N = ret_dpn
    M = N.initial_marking
    free:Set[PetriNetWithDataVariable]= set()
    visited:Dict[PetriNetMarking, Set] = dict() 
    prefixed:Dict[PetriNetMarking, Dict[GuardedTransition,GuardedTransition]] = dict()
    # helpers
    def find(old, N:PetriNetWithData) -> GuardedTransition:
        for t in N.transitions:
            if t.tid == old.tid:
                return t
        raise Exception(f"transition {old} not found in net")
    def clr(free:Set,f:GuardedTransition, N:PetriNetWithData) -> Set:
        return (free.difference(N.reads(f))).union(N.writes(f))
    def psh(visited:dict, M:PetriNetMarking, free:Set) -> None:
        visited[M] = deepcopy(free)
    def fire(M:PetriNetMarking, f:GuardedTransition) -> PetriNetMarking:
        return M.remark(f)
    def reset(N:PetriNetWithData, history) -> PetriNetMarking:
        ret = N.initial_marking
        for fired in history:
            if (fired not in ret.enabled()):
                __crashout(fired, N, ret, history)
                assert fired in ret.enabled(), f"transition {repr(fired)} not firable in marking {repr(ret)}, expected one of the following: {repr(ret.enabled())}"
            ret = ret.remark(fired)
        return ret
    # traverse path
    while not path.is_empty():
        f = find(path.pop(),N)
        info(f"working on transition:: {repr(f)}")
        debug(f"current marking:: {M}")
        debug(f"current free variables:: {free}")
        debug(f"set of firable: {M.enabled()}")
        if (f not in M.enabled()):
            if str(M) in prefixed.keys():
                path.push(f)
                pre = prefixed[str(M)][f]
                path.push(pre)
                info(f"transition {f} was prefixed berfore firing {pre}")
                continue
            __crashout(f, N, M, history)
        assert f in M.enabled(), f"transition {f} not firable in marking {M}"
        debug(f"next possible marking:: {M.remark(f)}")
        
        # case 1: if we dont need any, and we have not visited next; or
        # if we dont need any, and we are revisiting, but after firing 
        # visted matches free.
        M_prime = M.remark(f)
        need = len(N.reads(f)) > 0
        visiting = M_prime in visited
        vmatchfree = visited[M_prime].issubset(clr(free,f,N)) if visiting else False
        if (
            (not need and not visiting) 
            or
            (not need and visiting and vmatchfree)
        ):
            # trigger continue 
            info("triggered continue")
            psh(visited, M, free)
            M = fire(M, f)
            free = clr(free, f, N)
            history.append(f)
            continue 
        # case 2:  if we dont need any, and we are revisiting, but 
        # after firing visited wont match free; or we are revisiting,
        # and have f is satfied by free, but after firing visisted wont 
        # match free.
        fsat = N.reads(f).issubset(free)
        if (
            (not need and visiting and not vmatchfree)
            or 
            (visiting and fsat and not vmatchfree)
        ):
            # trigger add expansion
            expansion += 1
            info(f"triggered add expansion ({expansion})")
            N = __add_expansion(N, f, visited[M_prime])
            psh(visited, M, free)
            M = fire(M, f)
            free = clr(free, f, N)
            history.append(f)
            continue
        # case 3: if we are not revisiting, and f is satisfied by free; or,
        # if we are revisiting, and f is satisfied by free, and after 
        # firing visited will match free.
        if (
            (not visiting and fsat)
            or 
            (visiting and fsat and vmatchfree)
        ):
            # trigger continue 
            info("triggered continue")
            psh(visited, M, free)
            M = fire(M, f)
            free = clr(free, f, N)
            history.append(f)
            continue
        # otherwise, trigger prefix expansion
        expansion += 1
        info(f"triggered prefix expansion ({expansion})")
        N, nt = __prefix_expansion(N, f)
        if not (str(M) in prefixed):
            prefixed[str(M)] = {}
        prefixed[str(M)][f] = nt
        M = reset(N,history)
        # readd f and add new tau to path
        path.push(f)
        path.push(nt)
    # set ret as the last copy of N
    ret_dpn = N
    # check that the path is still traversable
    curr_mark = ret_dpn.initial_marking
    debug(f"final path :: {history}")
    debug(f"initial marking :: {curr_mark}")
    for ot in history:
        assert ot in curr_mark.enabled() , f"transition {ot} is not firable in expanded dpn"
        curr_mark = curr_mark.remark(ot)
        debug(f"transition {ot} fired :: {curr_mark}")
    debug(f"final marking :: {curr_mark}")
    assert curr_mark.reached_final(), "final marking not reached in expanded dpn"
    return ret_dpn

def _shortcut_expansion(dpn:PetriNetWithData,) -> PetriNetWithData:
    """
    This a cheaters approach to expansion to ensure that the net is relaxed
    data-sound. It simply adds a silent transition from the source place to
    sink place. The silent transition has a naively true guard, and no write
    constraints.
    """
    ret = None 
    ## find src 
    src = None
    for p in dpn.places:
        if dpn.initial_marking.contains(p):
            if src is not None:
                raise Exception("multiple source places detected, expected"
                                + " a workflow net with one input place.")
            src = p
    ## find sink
    sink = None
    for p in dpn.places:
        if dpn.final_marking.contains(p):
            if sink is not None:
                raise Exception("multiple sink places detected, expected"
                                + " a workflow net with one output place.")
            sink = p
    ## add new tau and new src to old src
    new_tau = __find_new_tau(dpn)
    new_flows = set(dpn.arcs)
    new_flows.add(
        Arc(
            src,
            new_tau
        )
    )
    new_flows.add(
        Arc(
            new_tau,
            sink,
        )
    )
    new_places = set(dpn.places)
    new_transitions = set(dpn.transitions)
    new_transitions.add(new_tau)
    ## construct the new dpn
    ret = __rebuild_net(dpn, new_places, new_transitions, new_flows)
    assert ret is not None, "shortcut expansion not implemented"
    return ret 

def _duplicate_expansion(dpn:PetriNetWithData,) -> PetriNetWithData:
    """
    This a cheaters approach to expansion to ensure that the net is relaxed
    data-sound. This approach duplicates transitions with non-trivial guards,
    where the duplicated trannsitions have a trivial guard and no write 
    contraints.
    """
    ret = None
    new_flows = set(dpn.arcs)
    new_transitions = set(dpn.transitions)
    for t in dpn.transitions:
        if t.guard.trivial():
            continue
        new_tau = __dup_trans(new_transitions, t)
        for pre in preset_of_transition(dpn, t):
            new_flows.add(
                Arc(
                    pre,
                    new_tau
                )
            )
        for post in postset_of_transition(dpn, t):
            new_flows.add(
                Arc(
                    new_tau,
                    post
                )
            )
        new_transitions.add(new_tau)
    # build new dpn
    ret = __rebuild_net(dpn, dpn.places, new_transitions, new_flows)
    assert ret is not None, "duplicate expansion not implemented"
    return ret

DM_IGNORED_ATTRS = set(["time:", "lifecycle:"])

def _identify_problems(lpn:LabelledPetriNet,
    identification:Literal["single-bag","postset","marking","regions"]
    ) -> Set[ClassificationProblem]:
    """
    step one: deduce classification problems from the net.
    """
    return find_classification_problems(lpn, identification)

def _old_populate_problems(log:ComplexEventLog,
                       alignment:AlignmentMapping, 
                       problems:Set[ClassificationProblem],
                       ignored_attrs:Set[str]
                    ) -> Set[ClassificationProblem]:
    for trace,instances in InfoIteratorProcessor('processed variants', log):
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
    return problems

def _populate_problems(log:ComplexEventLog,
                       alignment:AlignmentMapping, 
                       problems:Set[ClassificationProblem],
                       ignored_attrs:Set[str]
                    ) -> Set[ClassificationProblem]:
    """
    step two: populate the classification problems with examples from
    alignments.
    """
    pool = Parallel(n_jobs=6, verbose=10, return_as='generator_unordered',
                    batch_size=1, backend='loky')
    # TODO: this for loop could be parallelised for a speedup
    # the work of the outer loop
    def work(contexters, problems, problem_places):
        ret = dict(
            (prob, [])
            for prob in problems
        )
        from joblib import Parallel, delayed, parallel_backend
        # the work of the inner loop
        def iwork(context:List[AlignmentMove],
                  problem_places:Dict[ClassificationProblem, List[int]]):
            iret = dict(
                (prob, [])
                for prob in problems
            )
            for prob in problem_places.keys():
                temp = []
                positions = problem_places[prob]
                for pos in positions:
                    data = dict()
                    move = context[pos]
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
                        temp.append(
                            (move.transition, data)
                        )
                iret[prob] += temp
            return iret
        # decide whether to run the pool or not
        if (len(contexters) > 60):
            with parallel_backend("loky", inner_max_num_threads=6):
                # decide on workload pattern
                if (len(contexters) > 240):
                        extracts = Parallel(n_jobs=6, verbose=5,
                                            pre_dispatch='3*n_jobs',
                                            batch_size=25,
                                            return_as='generator_unordered')(
                            delayed(iwork)(context, problem_places)
                            for context in contexters
                        )
                else:
                    batchsize = int(len(contexters)/6)
                    extracts = Parallel(n_jobs=6, verbose=5,
                                        pre_dispatch='2 * n_jobs',
                                        batch_size=batchsize,
                                        return_as='generator_unordered')(
                        delayed(iwork)(context, problem_places)
                        for context in contexters
                    )
                # sync the work
                for extract in extracts:
                    for prob in problems:
                        ret[prob] += extract[prob]
        else:
            for context in contexters:
                for prob in problems:
                    temp = []
                    positions = problem_places[prob]
                    for pos in positions:
                        data = dict()
                        move = context[pos]
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
                            temp.append(
                                (move.transition, data)
                            )
                    ret[prob] += temp
        return ret
    # step one preload contextulised alignment
    def contextulise(instances, alignment:Alignment, 
                     problems:Set[ClassificationProblem]):
        "preps the work for the outer loop"
        def find_problem_places(problems:Set[ClassificationProblem], 
                                alignment:Alignment):
            ret = dict(
                (prob, [])
                for prob in problems
            )
            for pos,move in enumerate(alignment.moves()):
                if move.type == AlignmentMoveType.LOG:
                        continue
                for prob in problems:
                    if prob.reached(move.marking) \
                        and move.transition in prob.targets:
                            ret[prob].append(pos)
            return ret
        # contextualise and add problem places
        return ([
            alignment.contextualise(inst)
            for inst in instances
        ], find_problem_places(problems, alignment))
    # the work of step one
    orderwork = sorted(
        [ (trace,instances) for trace,instances in log],
        key=lambda x: len(x[1]),
        reverse=True)
    contexts = Parallel(n_jobs=-1, verbose=5,)(
        delayed(contextulise)(instances, alignment[trace], problems)
        for trace,instances in InfoIteratorProcessor(
            'processing alignments', orderwork, stack=11, 
            size=log.get_nvariants()
        )
    )
    # step two launch the outer loop in parallel
    # the work of step 2
    results = pool(delayed(work)
        (contexters, problems, problem_places)
        for contexters, problem_places in InfoIteratorProcessor(
            '#variants processing', contexts, 
            stack=13, size=log.get_nvariants()
        )
    )
    # step four sync the work with the problems
    i = 1
    for extract in results:
        for prob in problems:
            prob.add_examples(extract[prob])
        info(f"finished processing variant :: {i}/{log.get_nvariants()}")
        i += 1
    info(f"finished processing all ({log.get_nvariants()}) variants...")
    # return the populated problems
    return problems
    

def mine_guards_for_lpn(lpn: LabelledPetriNet, log: ComplexEventLog,
    alignment:AlignmentMapping=None, 
    identification:Literal["single-bag","postset","marking","regions"]="postset",
    problems:Set[ClassificationProblem]=None,
    populated:bool=False,
    expand_on_writes:bool=True,
    expansion:Literal["earnest","shortcut","duplicate"]="earnest",
    ignored_attrs:Set[str]=DM_IGNORED_ATTRS) \
    -> PetriNetWithData:
    """
    Performs decision mining on the given lpn using diagonstic information
    from alignments to annoate guards on transitions in the lpn.

    Note that the returned dpn may contain further silent transitions 
    to model write constraints by default. However, the visible language of
    the net will be the same as the given lpn.
    """
    # step zero: check if we need to find alignments
    if alignment is None:
        ali = find_alignments_for_variants(log, lpn, "pm4py")
    else:
        ali = alignment
    info("step zero finished, found alignments...")
    # step one: deduce classification problems from the net.
    # obtain the classification problems
    if problems is None:
        problems = _identify_problems(lpn, identification)
    info("step one finished, identified classification problems...")
    for prob in problems:
        info(f"found problem ::\n\t{prob}")
    info("step two, populating classification problems...")
    if (not populated):
        problems = _populate_problems(log, ali, problems, ignored_attrs) 
    info("step two finished, populated classification problems...")
    # solve the classification problems
    resulting = dict()
    resulting_types = dict()
    info("step three, solving classification problems...")
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
    info("step three-b, translating mined guards to dpn...")
    mapping_trans = dict()
    for t in lpn.transitions:
        if (t in resulting.keys()):
            mapping_trans[t] = GuardedTransition(
                t.name,
                resulting[t],
                t.tid,
                t.silent
            )
            info(f"adding guard :: {resulting[t]} to transition :: {t}")
        else:
            mapping_trans[t] = GuardedTransition(
                t.name,
                Guard("true"),
                t.tid,
                t.silent
            )
            info(f"adding guard :: true to transition :: {t}")
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
    info("step three finished, construct dpn without write constraints...")
    # expand the dpn to include write constraints
    if (expand_on_writes):
        info("step four, expanding dpn for write constraints...")
        if (expansion == "earnest"):
            # find the alignment with the longest projected path
            longest = -1
            long = None
            for ali in ali._storage.values():
                path = ali.projected_path()
                if len(path) > longest:
                    long = ali 
                    longest = len(path)
            # expand using the longest projected path
            info(f"longest path :: {longest}")
            info(f"longest alignment being used for expansion :: {repr(long)}")
            dpn = _earnst_expansion(dpn, long)
        elif (expansion == "shortcut"):
            dpn = _shortcut_expansion(dpn)
        elif (expansion == "duplicate"):
            dpn = _duplicate_expansion(dpn)
        else:
            raise Exception(f"unsupported expansion strategy :: {expansion}")
        info("step four finished, expansion complete...")
    info("finished mining guards for lpn")
    return dpn
