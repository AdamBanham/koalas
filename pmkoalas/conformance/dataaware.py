"""
This modules provides ways to conformance data-aware process conformance.

Implemented techniques include:
    - guard-recall 
    - guard-precision
"""
from pmkoalas.complex import ComplexEventLog
from pmkoalas.models.petrinet import PetriNetWithData
from pmkoalas.models.guards import GuardOutcomes
from pmkoalas.models.transitiontree import TransitionTreeGuardFlow
from pmkoalas.models.transitiontree import TransitionTree
from pmkoalas.conformance.matching import ManyMatching,EqualPathWeighter
from pmkoalas.conformance.matching import construct_many_matching, _computation_many_matching
from pmkoalas.conformance.matching import ExpontentialPathWeighter
from pmkoalas.models.transitiontree import construct_from_model
from pmkoalas._logging import info, enable_logging, InfoQueueProcessor
from pmkoalas._logging import InfoIteratorProcessor

from joblib import Parallel, delayed

def compute_directed_bookkeeping(flow:TransitionTreeGuardFlow, 
    matcher:ManyMatching, log:ComplexEventLog, outcome=GuardOutcomes.TRUE) \
    -> float:
    """
    Computes the many directed bookkeeping on any flow for any given outcome.
    """
    bookkeeping = 0
    for trace, instances in log:
        weighter = ExpontentialPathWeighter(matcher[trace])
        paths = matcher[trace]
        for path in paths:
            for step,i in zip(path, range(1, len(path)+1)):
                if step == flow: 
                    i_w = 0
                    for instance in instances:
                        irveson = flow.guard().check(
                            instance.get_state_as_of(i-1)
                        ) == outcome
                        i_w += weighter(path, trace) if irveson else 0
                    bookkeeping += i_w
                    break
    return bookkeeping

def compute_general_bookkeeping(flow:TransitionTreeGuardFlow, 
    matcher:ManyMatching, log:ComplexEventLog, outcome=GuardOutcomes.TRUE) \
    -> float:
    """
    Computes the many general bookkeeping on any flow for any given outcome.
    """
    bookkeeping = 0
    for trace, instances in log:
        weighter = ExpontentialPathWeighter(matcher[trace])
        paths = matcher[trace]
        for path in paths:
            for step,i in zip(path, range(1, len(path)+1)):
                if step.offering() == flow.offering(): 
                    i_w = 0
                    for instance in instances:
                        irveson = flow.guard().check(
                            instance.get_state_as_of(i-1)
                        ) == outcome
                        i_w += weighter(path, trace) if irveson else 0
                    bookkeeping += i_w
                    break
    return bookkeeping

def compute_total_weight(flow:TransitionTreeGuardFlow, 
    matcher:ManyMatching, log:ComplexEventLog) -> float:
    """
    Computes the total weight on a flow, regradless of outcome.
    """
    weight = 0.0
    for trace, instances in log:
        paths = matcher[trace]
        for path in paths:
            for step in path:
                if step == flow: 
                    weight += (1/len(paths)) * len(instances)
                    break
    return weight

def _computation_guard_recall(tree:TransitionTree, matching:ManyMatching, 
    log:ComplexEventLog) -> float:
    """
    The actual computation of guard-recall using the structures.
    """
    flow_weight = set( 
        (flow, compute_total_weight(flow, matching, log))
        for flow
        in InfoIteratorProcessor("computing total weight", tree.flows(), 
                                 stack=4)
    )
    inner_sum = 0.0
    t_w = 0.0
    for flow,total_weight in InfoIteratorProcessor("computing flow weight", 
                                                   flow_weight):
        inner_sum += \
            compute_directed_bookkeeping(flow, matching, log)
        t_w += total_weight
    info(f"computed weights :: flow - {inner_sum:.2f} total - {t_w:.2f}")
    return (inner_sum/t_w)

def _optimised_guard_recall(log:ComplexEventLog, tree:TransitionTree) -> float:
    """
    The computation of guard recall, whereby we only loop over the log once.
    """
    from pmkoalas.models.transitiontree import TransitionTreeGuardFlow
    from pmkoalas.models.guards import GuardOutcomes
    total_weight = 0
    flow_weight = 0
    # partial worker 
    pool = Parallel(n_jobs=-2)
    def partial(trace, instances, path, inst_w) -> float:
        flow_weight = 0
        total_weight = 0
        instance_weight = inst_w(path, trace)
        for step,i in zip(path, range(1, len(path)+1)):
                    if isinstance(step, TransitionTreeGuardFlow):
                        for instance in instances:
                            irveson = step.guard().check(
                                    instance.get_state_as_of(i-1)
                                ) == GuardOutcomes.TRUE
                            flow_weight += instance_weight * int(irveson)
        total_weight += inst_w.share * len(path.noskips) * len(instances)
        return flow_weight, total_weight
    # worker for inputs
    def params(trace, instances, tree):
        _,candidates = _computation_many_matching(trace,tree)
        return trace, instances, candidates
    # computation of work
    inputs = list(pool( 
        delayed(params)
        (trace, instances, tree)
        for trace,instances 
        in log 
    ))
    inputs = [
        (trace, instances, path, ExpontentialPathWeighter(matching))
        for trace, instances, matching
        in inputs 
        for path 
        in matching
    ]
    weights = pool( 
        delayed(partial)
        (traces, instances, path, inst_w)
        for traces, instances, path, inst_w 
        in InfoIteratorProcessor("processing variant-paths for guard-recall", 
            inputs,
            stack=8
        )
    )
    info("completed processing.")
    info(f"computed weights across flows (flow,total) :: {weights}")
    flow_weight += sum(
        f 
        for f,t 
        in weights
    )
    total_weight += sum( 
        t 
        for f,t 
        in weights
    )
    recall = flow_weight / total_weight
    info(f"computed guard recall of {recall:.3f}")
    return recall

@enable_logging
def compute_guard_recall(log:ComplexEventLog, model:PetriNetWithData, 
    optimised:bool=True) -> float: 
    """
    Quanitfies the quality between an event log and a data-aware process model 
    using guard-recall, where a data-aware process model is a Petri net with 
    data.
    """
    # find longest observed trace
    long = None
    for trace,_ in log:
        if long == None:
            long = trace 
        elif len(trace) > len(long):
            long = trace 
    long = len(long)
    # prepare model
    tree = construct_from_model(model, longest_playout=long)
    if (optimised):
        return _optimised_guard_recall(log, tree)
    else:
        info("creating matchings between all traces")
        matching = construct_many_matching(log, tree)
        # compute the measure 
        return _computation_guard_recall(tree, matching, log)

def _computation_guard_precision(tree:TransitionTree, matching:ManyMatching,
    log:ComplexEventLog) -> float:
    """
    The actual computation of guard-precision using the structures.
    """
    upper_sum = 0.0
    lower_sum = 0.0
    for flow in InfoIteratorProcessor(
        "processing flows",
        tree.flows()):
        upper_sum += compute_directed_bookkeeping(flow, matching, log)
        lower_sum += compute_general_bookkeeping(flow, matching, log)
    prec = (1 + upper_sum) / (1 + lower_sum) 
    info(f"computed guard precision : {prec:.3f}")
    return prec

def _optimised_guard_precision(log:ComplexEventLog, tree:TransitionTree):
    """
    The computation of guard recall, whereby we only loop over the log once.
    """
    from pmkoalas.models.transitiontree import TransitionTreeGuardFlow
    from pmkoalas.models.guards import GuardOutcomes
    # partial worker 
    pool = Parallel(n_jobs=-2)
    def partial(tree, trace, instances, path, inst_w) -> float:
        upper_sum = 0.0
        lower_sum = 0.0
        instance_weight = inst_w(path, trace)
        for step,i in zip(path, range(1, len(path)+1)):
                    if isinstance(step, TransitionTreeGuardFlow):
                        other_flows = step.offering().outgoing(tree.flows())
                        other_flows = other_flows.difference(set([step]))
                        for instance in instances:
                            irveson = step.guard().check(
                                    instance.get_state_as_of(i-1)
                                ) == GuardOutcomes.TRUE
                            upper_sum += instance_weight * int(irveson)
                            lower_sum += inst_w.share * int(irveson)
                            for lflow in other_flows:
                                irveson = lflow.guard().check(
                                    instance.get_state_as_of(i-1)
                                ) == GuardOutcomes.TRUE
                                lower_sum += inst_w.share  * int(irveson)
        return upper_sum, lower_sum
    # worker for inputs
    info("preparing work")
    def params(trace, instances, tree):
        _,candidates = _computation_many_matching(trace,tree)
        return tree, trace, instances, candidates
    # computation of work
    inputs = list(pool( 
        delayed(params)
        (trace, instances, tree)
        for trace,instances 
        in log 
    ))
    inputs = [
        (tree, trace, instances, path, ExpontentialPathWeighter(matching))
        for tree, trace, instances, matching
        in inputs 
        for path 
        in matching
    ]
    weights = pool( 
        delayed(partial)
        (tree, traces, instances, path, inst_w)
        for tree, traces, instances, path, inst_w 
        in InfoIteratorProcessor("processing variant-paths for guard-precision", 
            inputs,
            stack=8
        )
    )
    info("completed processing.")
    info(f"computed weights across flows (upper,lower) :: {weights}")
    upper_sum = sum(
        up 
        for up,low 
        in weights
    )
    lower_sum = sum( 
        low 
        for up,low 
        in weights
    )
    prec = (1 + upper_sum) / (1 + lower_sum)
    info(f"computed guard recall of {prec:.3f}")
    return prec

def compute_guard_precision(log:ComplexEventLog, model:PetriNetWithData,
    optimised:bool=True ) -> float:
    """
    Quanitfies the quality between an event log and a data-aware process model 
    using guard-precision, where a data-aware process model is a Petri net with 
    data.
    """
    # find longest observed trace
    long = None
    for trace,_ in log:
        if long == None:
            long = trace 
        elif len(trace) > len(long):
            long = trace 
    long = len(long)
    # prepare model
    tree = construct_from_model(model, longest_playout=long)
    if optimised:
        return _optimised_guard_precision(log, tree)
    else:
        matching = construct_many_matching(log, tree)
        # compute measure
        return _computation_guard_precision(tree, matching, log)
