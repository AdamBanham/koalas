"""
This modules provides ways to conformance data-aware process conformance.

Implemented techniques include:
    - guard-recall 
    - guard-precision
"""

from pmkoalas.complex import ComplexEventLog
from pmkoalas.models.petrinet import LabelledPetriNet
from pmkoalas.models.transitiontree import TransitionTreeGuardFlow
from pmkoalas.conformance.matching import ManyMatching,EqualPathWeighter
from pmkoalas.conformance.matching import construct_many_matching,ExpontentialPathWeighter
from pmkoalas.models.transitiontree import construct_from_model

def compute_directed_bookkeeping(flow:TransitionTreeGuardFlow, 
    matcher:ManyMatching, log:ComplexEventLog, outcome=True) -> float:
    """
    Computes the many directed bookkeeping on any flow for any given outcome.
    """
    bookkeeping = 0
    for trace, instances in log:
        weighter = EqualPathWeighter(matcher[trace])
        for instance in instances:
            paths = matcher[trace]
            for path in paths:
                for step,i in zip(path, range(1, len(path)+1)):
                    if step == flow: 
                        irveson = flow.guard().check(
                            instance.get_state_as_of(i-1)
                        ) == outcome
                        bookkeeping += weighter(path, trace) * int(irveson)
    return bookkeeping

def compute_general_bookkeeping(flow:TransitionTreeGuardFlow, 
    matcher:ManyMatching, log:ComplexEventLog, outcome=True) -> float:
    """
    Computes the many general bookkeeping on any flow for any given outcome.
    """
    bookkeeping = 0
    for trace, instances in log:
        weighter = ExpontentialPathWeighter(matcher[trace])
        for instance in instances:
            paths = matcher[trace]
            for path in paths:
                for step,i in zip(path, range(1, len(path)+1)):
                    if ( not isinstance(step, TransitionTreeGuardFlow)):
                        continue
                    if step.offering() == flow.offering(): 
                        irveson = flow.guard().check(
                            instance.get_state_as_of(i-1)
                        ) == outcome
                        bookkeeping += weighter(path, trace) * int(irveson)
    return bookkeeping

def compute_total_weight(flow:TransitionTreeGuardFlow, 
    matcher:ManyMatching, log:ComplexEventLog) -> float:
    """
    Computes the total weight on a flow, regradless of outcome.
    """
    weight = 0.0
    for trace, instances in log:
        weighter = EqualPathWeighter(matcher[trace])
        paths = matcher[trace]
        print(f"{trace=} with {len(paths)=}")
        for path in paths:
            print(f"{str(path)=}")
            for step in path:
                if step == flow: 
                    weight += weighter(path, trace) * len(instances)
    return weight

def compute_guard_recall(log:ComplexEventLog, model:LabelledPetriNet) \
    -> float: 
    """
    Computes guard-recall of a data-aware process model, i.e. a Petri net with 
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
    matching = construct_many_matching(log, tree)
    flow_weight = set( 
        (flow, compute_total_weight(flow, matching, log))
        for flow
        in tree.flows()
    )
    flow_weight = set( 
        (f,w)
        for f,w 
        in flow_weight
        if w > 0.0
    )
    print(f"{len(flow_weight)=}")
    recall = 1.0/ len(flow_weight)
    print(f"{recall=}")
    inner_sum = 0.0
    print(f"{inner_sum=}")
    for flow,total_weight in flow_weight:
        inner_sum += \
            compute_directed_bookkeeping(flow, matching, log) / total_weight
        print(f"{inner_sum=}")
    return recall * inner_sum

def compute_guard_precision(log:ComplexEventLog, model:LabelledPetriNet) \
    -> float:
    """
    Computes guard-precision of a data-aware process model, i.e a Petri net with
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
    matching = construct_many_matching(log, tree)
    flow_weight = set( 
        (flow, compute_total_weight(flow,matching, log))
        for flow
        in tree.flows()
    )
    flow_weight = set( 
        (f,w)
        for f,w 
        in flow_weight
        if w > 0.0
    )
    prec = 1./ len(flow_weight)
    inner_sum = 0.0
    for flow,_ in flow_weight:
        inner_sum += \
            compute_directed_bookkeeping(flow, matching, log) \
            / compute_general_bookkeeping(flow, matching, log)
    return prec * inner_sum 
