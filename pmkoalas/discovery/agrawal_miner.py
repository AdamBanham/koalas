"""
This module is a implementation of the miner present by R. Argrawal in 1997.

See the following article for more information about the argrawal miner:\n
R. Agrawal, D. Gunopulos, and F. Leymann, “Mining process models from workflow
logs,” in EDBT, ser. Lecture Notes in Computer Science, vol. 1377, 
Springer, 1998, pp. 469–483.
"""
from dataclasses import dataclass, field
from typing import Set, Optional, List, Tuple, Dict
from copy import deepcopy
from itertools import product
from logging import DEBUG, INFO
from warnings import warn

from pmkoalas.discovery.meta import DiscoveryTechnique
from pmkoalas.simple import Trace
from pmkoalas.simple import EventLog
from pmkoalas._logging import debug, enable_logging, info, get_logger

@dataclass
class DependencyNode():
    """
    Helper
    """

    label:str

    def __hash__(self) -> int:
        return hash(self.label)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, type(self)) :
            return self.__hash__() == value.__hash__()
        else:
            False


@dataclass
class DependencyEdge():
    """
    Helper
    """

    source:DependencyNode
    target:DependencyNode
    counter:int=1

    def increment(self) -> None:
        self.counter += 1

    def __hash__(self) -> int:
        return hash((self.source.label,self.target.label))
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, type(self)) :
            return self.__hash__() == value.__hash__()
        else:
            return False
    
@dataclass
class DependencyWalk():

    walk:List[DependencyNode] = field(default_factory=list)


    def step(self, edge:DependencyEdge) -> 'DependencyWalk':
        last = self.walk[-1]

        if (edge.source == last):
            contains = [ n for n in self.walk if n == edge.target] 
        else:
            raise ValueError("Passed a edge that is not from the last node.")


class DependencyGraph():
    """
    This graph represents the concept of a dependency graph,
    that is, a graph that represents all the dependencies found in the log,
    as described by R. Agrawal et al. in 1998 in def. 5.

    The vertices of the graph are the seen activities in the log, 
    and the edges denote that activity v depends on activity u (def. 4).

    The graph contains one starting vertex and one ending vertex.
    """

    def __init__(self, 
                 vertices:Set[DependencyNode], edges:Set[DependencyEdge],
                 _reachability:Dict[DependencyNode,Dict[DependencyNode,bool]]=None,
                 ignore_start_end:bool=False,
                ) -> None:
        if (len(vertices) == 0 and len(edges) != 0):
            raise ValueError("Cannot have edges without vertices.")
        self._vertices = set()
        self._edges = set()
        self._start = None
        self._end = None 
        self._inedges = dict()
        self._outedges = dict()
        if _reachability == None:
            self._reachability = dict()
        else:
            self._reachability = deepcopy(_reachability)
        # check that each vertex is in at least one edge
        remove = set()
        for v in vertices:
            vedges = [ e for e in edges 
                      if e.source == v or e.target == v]
            if len(vedges) == 0:
                warn("DependencyGraph was given a vertex without edges, " 
                     +"removing.")
                continue
            # find start and end vertices
            tgt = [e for e in edges if e.target == v]
            src = [e for e in edges if e.source == v]
            self._inedges[v] = set(tgt)
            self._outedges[v] = set(src)
            if (v not in self._reachability):
                self._reachability[v] = dict()
            if len(tgt) == 0:
                if (self._start != None):
                    if (not ignore_start_end):
                        raise ValueError("Cannot have multiple start vertices.")
                self._start = v
            if len(src) == 0:
                if (self._end != None):
                    if (not ignore_start_end):
                        raise ValueError("Cannot have multiple end vertices.")
                self._end = v
            # store vertex and edges
            self._vertices.add(deepcopy(v))
            for e in vedges:
                self._edges.add(deepcopy(e))
        # query observed activities 
        self._acts = set([ v.label for v in self._vertices])
        # only keep the ordered walk of vertices
        # walkv = self.walk_vertices()
        # walke = self.walk_edges()
        if (self._start == None):
            raise ValueError("Missing start vertex.")
        if (self._end == None):
            raise ValueError("Missing end vertex.")

    def is_empty(self) -> bool:
        """
        Returns True if the graph is empty.
        """
        return len(self._vertices) == 0
    
    def start(self) -> DependencyNode:
        """
        Returns the start vertex of the graph.
        """
        return deepcopy(self._start)
    
    def end(self) -> DependencyNode:    
        """
        Returns the end vertex of the graph.
        """
        return deepcopy(self._end)
    
    def vertices(self) -> Set[DependencyNode]:
        """
        Returns the vertices of the graph as a new set.
        """
        return deepcopy(self._vertices)
    
    def edges(self) -> Set[DependencyEdge]:
        """
        Returns the edges of the graph as a new set.
        """
        return deepcopy(self._edges)

    def induce_subgraph(self, trace:Trace) -> 'DependencyGraph':
        """
        Returns the induced subgraph of the dependency graph for the given
        trace, may be an empty graph.
        """
        acts = trace.seen_activities()
        retV = set([ v for v in self.vertices() if v.label in acts])
        pedges = set([ e for e in self.edges() if e.source in retV])
        retE = set([ 
            e 
            for e 
            in pedges
            if _check_follows_for(trace, e.target.label, e.source.label)
        ])
        return DependencyGraph(
            retV,
            retE,
            ignore_start_end=True    
        )
        
    def isconnected(self) -> bool:
        """
        Returns True if the graph is connected.
        """
        if self.is_empty():
            return False

        # starting point
        start_vertex = self.start()
        debug(f"starting from vertex ::  {start_vertex.label}")

        # Perform depth-first search starting from the start_vertex
        visited = set()
        stack = [start_vertex]

        while len(stack) > 0:
            vertex = stack.pop()
            visited.add(vertex)
            debug(f"visiting {vertex.label}")

            # Get the neighbors of the current vertex
            neighbors = [ e.target for e in self.outedges(vertex) ]

            # Add unvisited neighbors to the stack
            unvisited_neighbors = [neighbor for neighbor in neighbors if neighbor not in visited]
            stack.extend(unvisited_neighbors)

        # If all vertices have been visited, the graph is connected
        debug(f"visited the following vertices :: {visited}")
        debug(f"len check :: {len(visited)} vs {len(self._vertices)}")
        return len(visited) == len(self._vertices) and self.end() in visited
    
    def path_between(self, from_node:DependencyNode, to_node:DependencyNode
                    ) -> bool:
        """
        Returns True if there is a path from from_node to to_node in the graph.
        """
        # check if the path has already been calculated
        past = self._reachability[from_node]
        if to_node in past:
            return past[to_node]
        # compute new reachability
        visited = set()
        stack = [from_node]

        while stack:
            current_node = stack.pop()
            visited.add(current_node)

            if current_node == to_node:
                self._reachability[from_node][to_node] = True
                return True

            neighbors = [ e.target for e in self.outedges(current_node) ]
            unvisited_neighbors = [neighbor for neighbor in neighbors if neighbor not in visited]
            stack.extend(unvisited_neighbors)

        self._reachability[from_node][to_node] = False
        return False
    
    def does_not_violate(self, trace:Trace) -> bool:
        """
        Returns if the given trace does not violate any dependency.

        Ideally, should only be called on the induced subgraph of the 
        trace.
        """
        # check the starting 
        start = trace[0]
        if start != self.start().label:
            return False
        # check the ending
        end = trace[-1]
        if end != self.end().label:
            return False
        # now check the body of the trace
        for act in trace.seen_activities():
            deps = [ e for e in self.edges() if e.target.label == act]
            for edge in deps:
                if not _check_follows_for(trace, edge.target.label, edge.source.label):
                    return False
        # alll cases held, so the trace does not violate
        return True
    
    def transitive_reduction(self) -> 'DependencyGraph':
        """
        Returns the transitive reduction of the graph.
        """
        # create a copy of the graph
        retV = deepcopy(self.vertices())
        retE = deepcopy(self.edges())
        # calculate reachability for each pair of vertices
        for u in self.vertices():
            for v in self.vertices():
                self.path_between(u, v)
        reachability = self._reachability
        # reduce edges until only the smallest subset of edges remain that 
        # ensures that all connected members remain connected. 
        for v in self.vertices():
            for u in self.vertices():
                if u != v:
                    for w in self.vertices():
                        if w != u and w != v:
                            if reachability[u][v] and reachability[v][w] and reachability[u][w]:
                                debug(f"removing edge {u.label} -> {w.label}")
                                retE.discard(DependencyEdge(u, w))
        return DependencyGraph(retV, retE, ignore_start_end=True)
    
    def outedges(self, node:DependencyNode) -> Set[DependencyEdge]:
        """
        Returns the outedges of the given node.
        """
        return sorted( 
            self._outedges[node],
            key=lambda e: e.target.label
        )
    
    def get_neighbors(self, node:DependencyNode) -> Set[DependencyNode]:
        """
        Returns the neighbors of the given node.
        """
        return sorted(
            set([ e.target for e in self.outedges(node)]),
            key=lambda n: n.label
        )
    
    def walk_edges(self) -> List[DependencyEdge]:
        """
        Returns a consistence walk of the edges in the graph.
        """
        ret = [ ]
        stack = [ self.start() ]
        seen = set()
        while len(stack) > 0:
            node = stack.pop()
            seen.add(node)
            for edge in self.outedges(node):
                if edge not in seen:
                    ret.append(edge)
                    seen.add(edge)
                if (edge.target not in seen):
                    stack.append(edge.target)
        assert len(ret) == len(self.edges())
        return ret

    def walk_vertices(self) -> List[DependencyNode]:
        """
        Returns a consistence walk of the vertices in the graph.
        """
        ret = [ self.start() ]
        stack = [ self.start() ]
        seen = set()
        while len(stack) > 0:
            node = stack.pop()
            seen.add(node)
            if node not in ret and node != self.end():
                ret.append(node)
            for edge in self.outedges(node):
                if edge.target not in seen:
                    stack.append(edge.target)
        ret.append(self.end())
        assert len(ret) == len(self.vertices())
        return ret
    
    def create_dot_form(self) -> str:
        ret = "digraph{"
        ret += "dpi=150;rankdir=LR;nodesep=0.6;ranksep=0.3;"
        ret += "node[shape=circle,fillcolor=lightgray,style=filled,width=2,penwidth=8,fontsize=18,fontname=\"roboto\"];"
        ret += "edge[penwidth=4,fontsize=16,minlen=2,fontname=\"roboto\"];"
        nodeIds = dict()
        nid = 0
        for v in self.walk_vertices():
            nodeIds[v] = f"n{nid}"
            label = '<'+'<BR/>'.join([v.label[i:i+16] for i in range(0, len(v.label), 16)])+">"
            if v == self.start():
                ret += f"{nodeIds[v]}[label={label},fillcolor=green];" 
            elif v == self.end():
                ret += f"{nodeIds[v]}[label={label},fillcolor=red];" 
            else:
                ret += f"{nodeIds[v]}[label={label}];"
            nid += 1
        assert nid == len(self._vertices)
        elabel = 0
        seen = set()
        for v in self.walk_vertices():
            for e in self.outedges(v):
                if e.target not in seen:
                    ret += f"d{elabel}[shape=none,color=black,width=0.5,"\
                        +  f"label={e.counter},style=none];"
                    ret += f"{nodeIds[e.source]} -> d{elabel}:w"\
                        + f"[arrowhead=odot,color=black];"
                    ret += f"d{elabel}:e -> {nodeIds[e.target]}"\
                        + f"[arrowtail=odot,dir=both,color=black];"
                else:
                    ret += f"d{elabel}[shape=none,color=black,width=0.5,"\
                        +  f"label={e.counter},style=none];"
                    ret += f"{nodeIds[e.target]} -> d{elabel}:w"\
                        + f"[arrowhead=odot,dir=both,color=gray];"
                    ret += f"d{elabel}:e -> {nodeIds[e.source]}"\
                        + f"[arrowtail=odot,dir=back,color=gray];"
                elabel += 1
            seen.add(v)
        ret += "}"
        assert elabel == len(self._edges)
        return ret
    
    # model access functions
    
    def __eq__(self, value: object) -> bool:
        if issubclass(type(value), (DependencyGraph)):
            return (
                self.vertices() == value.vertices()
                and self.edges() == value.edges()
            )
        else:
            return False
        
    def __repr__(self) -> str:
        ret = "DependencyGraph(\n"
        ret += "\tset([\n"
        for v in self.walk_vertices():
            ret += f"\t\t{v.__repr__()},\n"
        ret += "\t]),\n"
        ret += "\tset([\n"
        for e in self.walk_edges():
            ret += f"\t\tDependencyEdge(\n"
            ret += f"\t\t\t{e.source.__repr__()},\n"
            ret += f"\t\t\t{e.target.__repr__()},\n"
            ret += f"\t\t\t{e.counter},\n"
            ret += "\t\t),\n"
        ret += "\t]),\n"
        ret += ")"
        return ret
        
    
def _check_follows_for(trace:Trace, actB:str, actA:str) -> bool:
        """
        Returns True if the first instance of activity A occurs before 
        the first instance activity B in the given trace.
        """
        first_a = -1
        first_b = -1
        for id,act in enumerate(trace.__iter__()):
            if act == actA:
                first_a = id
            if act == actB:
                first_b = id
            if first_a != -1 and first_b != -1:
                break
        debug(f"checking :: {trace} for {actA} -> {actB} :: {first_a} < {first_b}")
        return first_a < first_b

def compute_follows_relations(slog:EventLog) -> Set[Tuple[str,str]]:
        """
        Returns the set of follows relations for the given trace based on
        def.3 in Argrawal et al. 1998. That is each entry in the returned
        set (B,A) denotes that activity B follows activity A.

        An acitivty B follows activity A if B starts after A in each 
        trace that both B and A appear in, 
        OR,
        there exists an activity C such that C follows A and B follows C.
        """
        debug(slog)
        acts = slog.seen_activities()
        debug(acts)
        follows = set()
        # iterate over all traces and compute case 1
        for actB,actA in product(acts,acts):
            if actA == actB:
                continue
            debug(f"checking {actB} -> {actA}")
            # collect all executions where both acts occur
            traces = [ 
                trace 
                for trace,_ 
                in slog.__iter__() 
                if 
                    actA in trace.seen_activities() 
                    and 
                    actB in trace.seen_activities()
            ]
            if (len(traces) == 0):
                continue
            # check if B follow A in all traces
            debug(traces)
            traces = [
                1 if _check_follows_for(t,actB,actA) else 0
                for t 
                in traces
            ]
            debug(traces)
            if (sum(traces) == len(traces)):
                follows.add((actB,actA))
        # adjust follows based on case 2
        addtions = set()
        for actB,actA in product(acts,acts):
            if actB == actA:
                continue
            if (actB,actA) in follows:
                continue
            for actC in acts.difference({actB,actA}):
                debug(f"checking that {actC} -> {actA}, and {actB} -> {actC}")
                if (actC,actA) in follows and (actB,actC) in follows:
                    debug(f"found that {actB} follows {actA} through {actC}")
                    addtions.add((actB,actA))
                    break
        debug(follows)
        debug(addtions)
        follows = follows.union(addtions)
        return follows
    
def compute_dependencies(slog:EventLog) -> Set[Tuple[str,str]]:
    """
    Returns the set of dependencies for the given event log.
    That is a set, where each entry (B,A) denotes that activity 
    B depends on activity A.
    """
    follows = compute_follows_relations(slog)
    acts = slog.seen_activities()
    ret = set()
    # check for an activity A and activity B,
    # that B follows A, but A does not follow B,
    # then B depends on A.
    for actB,actA in product(acts,acts):
        if actB == actA:
            continue
        if (actB,actA) in follows and (actA,actB) not in follows:
            debug(f"found that {actB} depends on {actA}")
            ret.add((
                actB,
                actA
            ))
    return ret

def compute_independent_activities(slog:EventLog) -> Set[Tuple[str,str]]:
    """
    Returns the set of independent activities for the given event log.
    That is a set, where each entry (B,A) denotes that activity A and
    activity B are indpendent.
    """
    follows = compute_follows_relations(slog)
    acts = slog.seen_activities()
    ret = set()
    # check for an activity A and activity B,
    # such that either B follows A, but A follows B,
    # or B does not follow A, but A does not follow B.
    for actB,actA in product(acts,acts):
        if actB == actA:
            continue
        if (actB,actA) in follows and (actA,actB) in follows:
            debug(f"found that {actB} and {actA} are independent (both)")
            ret.add((
                actB,
                actA
            ))
            continue
        if (actB,actA) not in follows and (actA,actB) not in follows:
            debug(f"found that {actB} and {actA} are independent (neither)")
            ret.add((
                actB,
                actA
            ))
    return ret

def execution_is_consistent(trace:Trace, graph:DependencyGraph) -> bool:
    """
    Determines if the trace is consistent with the given graph, as described
    by definition 6 in R. Agrawal, D. Gunopulos, and F. Leymann, “Mining 
    process models from workflow logs”.
    """
    # check that the seen activities are a subset of the verticies 
    if (trace.seen_activities().issubset(graph._acts) == False):
        return False
    try:
        sub = graph.induce_subgraph(trace)
    except ValueError:
        return False

    if (sub.isconnected()):
        # now check that there exists a path between start and all 
        # other vertices
        start = sub.start()
        for v in sub._vertices:
            if (v == start):
                continue
            if (sub.path_between(start,v) == False):
                return False
        # check that no dependecies are violated by the ordering 
        # in the trace
        return sub.does_not_violate(trace)

    return False

def is_conformal(slog:EventLog, graph:DependencyGraph) -> bool:
    """
    Determines if the given event log is conformal with the given graph, as 
    described by definition 7 in R. Agrawal et. al. 1998.
    
    A dependency graph G is conformal with a log if the following holds:
        - for each dependency in  slog, there exists a path in G;
        - there is no path in G between independent activities;
        - G is consistent with every trace in the slog.
    """
    # check dependencies 
    for deps in compute_dependencies(slog):
        if not graph.path_between(
            DependencyNode(deps[1]), DependencyNode(deps[0])):
            return False
    # check that independent activities are not connected
    for indep in compute_independent_activities(slog):
        if graph.path_between(
            DependencyNode(indep[0]), DependencyNode(indep[1])):
            return False
    # check that the graph is consistent with every trace
    for trace,_ in slog.__iter__():
        if not execution_is_consistent(trace, graph):
            return False
    return True

def find_strongly_connected_components(graph: DependencyGraph) -> List[Set[DependencyNode]]:
    """
    Finds the strongly connected components in the given graph using Tarjan's algorithm.
    Returns a list of sets, where each set represents a strongly connected component.
    """
    index_counter = 0
    index = dict()
    low_link = dict()
    on_stack = set()
    stack = []
    components = []

    def strongconnect(node: DependencyNode):
        nonlocal index_counter, low_link, index, stack, on_stack, components
        index[node] = index_counter
        low_link[node] = index_counter
        index_counter += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in graph.get_neighbors(node):
            if neighbor not in index:
                strongconnect(neighbor)
                low_link[node] = min(low_link[node], low_link[neighbor])
            elif neighbor in on_stack:
                low_link[node] = min(low_link[node], index[neighbor])

        if low_link[node] == index[node]:
            component = set()
            while True:
                neighbor = stack.pop()
                on_stack.remove(neighbor)
                component.add(neighbor)
                if neighbor == node:
                    break
            components.append(component)

    for node in graph.vertices():
        if node not in index:
            strongconnect(node)

    return components

class ArgrawalMinerInstance(DiscoveryTechnique):
    """
    Mines a graph from an simplified event log using the proposed 
    approach by R. Argrawal D. Gunopulos and F. Leymann in 1998.

    The resulting graph aims to have the following properties:
    - completeness, the graph preserves all dependencies between activities
      presented in the event log.
    - irredundancy, the graph should not introduce spurious dependencies 
    - mimimality, the graph should have miminal edges.

    The resulting graph represents the constraints between activities rather
    than a system that executes to produce traces.
    """

    def __init__(self, 
                 optimise_step_five:bool=False, 
                 min_instances:int=1) -> None:
        """
        Initialises the miner for the following calls of `discover'.
         
        Internal Parameters:\n
        `optimise_step_five` (`bool=False`) 
            which sets what version of step five should be used, sequential 
            marking (False) or parallel marking over traces (True).
        `min_instances` (`int=1`)
            which sets the number of times an edge must be observed to be
            considered.
        """
        self._use_opt_five = optimise_step_five
        self._min_instances = min_instances

    def _test_for_consistent_activity_usage(self, slog:EventLog, n:int) -> bool:
        """
        Returns True if the event log, consistently uses the same activities
        for traces in the log, where at exactly n occurances of said 
        activities within traces.
        """
        acts = slog.seen_activities()
        for trace,_ in slog.__iter__():
            tacts = trace.seen_activities()
            # check that all activities are observed
            if tacts < acts:
                debug(f"trace {trace} does not contain all activities")
                return False
            seen = dict()
            # check that activities are observed n times
            for act in trace:
                if act in seen:
                    seen[act] += 1
                else:
                    seen[act] = 1
                if (seen[act] > n):
                    debug(
                        f"trace {trace} contains activity {act} more than \
                        {n} times")
                    return False
            # check ret matches n
            for act in tacts:
                if seen[act] != n:
                    debug(
                        f"trace {trace} does not contain activity {act} \
                        {n} times")
                    return False
        return True
    
    def _test_for_no_duplicated_activities(self, slog:EventLog) -> bool:
        """
        Tests whether the traces in the log have no duplicated activities.
        """
        for trace,_ in slog.__iter__():
            seen = set()
            # check that activities are observed n times
            for act in trace:
                if act in seen:
                    return False
                else:
                    seen.add(act)
        return True 
    
    def _adjust_traces(self, trace:Trace, prefix:bool, suffix:bool) -> Trace:
        """
        Adds a start and end activity to the trace if required.
        """
        ret = list(trace)
        if prefix:
            ret = [ "start" ] + ret
        if suffix:
            ret = ret + [ "end" ]
        return Trace(ret)
    
    @enable_logging
    def discover(self, slog:EventLog) -> DependencyGraph:
        """
        Discovers the dependency graph from the given simplifed event log, 
        using the proposed approach by R. Argrawal D. Gunopulos and F. 
        Leymann in 1998.

        For discovery, the conceptualisation of a process requires a single
        source and a single sink. Thus, abstracted starts and ends are 
        introduced into traces (if required).

        One of three algorithms will be used to discover the graph:
            - the special DAG algorithm, if the log consistently uses the
                same set of activities for a trace (exactly once).
            - the general DAG algorithm, if the log samples from the same
                set of activities for a trace (without replacement).
            - the cyclic DAG algorithm, if the log samples from a process
                where activities could repeated in a trace.
        """
        # adjust traces as required
        adjust_traces = False
        prefix = False
        suffix = False
        if len(slog.seen_start_activities()) != 1 \
            or len(slog.seen_end_activities()) != 1:
            if len(slog.seen_start_activities()) != 1:
                prefix = True
            if len(slog.seen_end_activities()) != 1:
                suffix = True
            adjust_traces = True
        if adjust_traces:
            info("adjusting traces by adding start and end activities " 
                 +"as needed")
            slog = EventLog([
                self._adjust_traces(t,prefix,suffix)
                for t,n in slog.__iter__()
                for i in range(n)
            ])
        # decide on the algorithm to use
        if self._test_for_consistent_activity_usage(slog, 1):
            info("using the special DAG algorithm")
            return self._discover_special_dag(slog)
        else:
            if self._test_for_no_duplicated_activities(slog):
                info("using the general DAG algorithm")
                return self._discover_general_dag(slog)
            else:
                info("using the cyclic DAG algorithm")
                return self._discover_cyclic_dag(slog)

    def _discover_special_dag(self, slog:EventLog)-> DependencyGraph:
        """
        Discovers the special DAG from the given simplifed event log, 
        using the proposed approach by R. Argrawal D. et. al. in 1998 
        through algorithm 1.

        The algorithm consists of the following steps:
            - start with a graph consisting of vertices for each activity
                and no edges.
            - for each execution E and activities u,v in E, add the edge of
                (u, v) if u terminates before v starts.
            - remove all edges that appear in both directions, i.e. 
                for activities u,v, if the edges (u,v) and (v,u) are in 
                the graph, remove both of them.
            - Compute the transitive closure of the graph.
            - Return the graph.
        """
        retV = self._step_one(slog)
        # step two 
        retE = self._step_two(slog)
        # step three
        graph = self._step_three(slog,retV,retE)
        # step four 
        info("step four started")
        graph = graph.transitive_reduction()
        info("step four completed")
        # step five
        info("returning a graph (|V|,|E|) :: ({},{})".format(
            len(graph.vertices()),len(graph.edges()))
            )
        return graph
    
    def _discover_general_dag(self, slog:EventLog) -> DependencyGraph:
        """
        Discovers the general DAG from the given simplifed event log, 
        using the proposed approach by R. Argrawal D. et. al. in 1998 
        through algorithm 2.

        The algorithm consists of the following steps:
            - start with a graph consisting of vertices for each activity
                and no edges.
            - for each execution E and activities u,v in E, add the edge of
                (u, v) if u terminates before v starts.
            - remove all edges that appear in both directions, i.e. 
                for activities u,v, if the edges (u,v) and (v,u) are in 
                the graph, remove both of them.
            - For each strongly connected component of G, remove from E 
                all edges between vertices in the same strongly connected 
                component.
            - For each process execution in L:
                - Find the induced subgraph of G.
                - Compute the transitive reduction of the subgraph.
                - Mark those edges in E that are present in the transitive 
                    reduction.
            - Remove the unmarked edges in E.
            - Return the graph.
        """
        retV = self._step_one(slog)
        retE = self._step_two(slog)
        graph = self._step_three(slog,retV,retE)
        graph = self._step_four(graph,retV,retE)
        if self._use_opt_five:
            marked = self._step_five_opt(slog,graph)
        else:
            marked = self._step_five(slog,graph)
        # step six
        graph = self._step_six(marked,graph)
        # step seven
        info("returning a graph (|V|,|E|) :: ({},{})".format(
            len(graph.vertices()),len(graph.edges()))
            )
        return graph
    
    def _suffix_repeated_activities(self, trace:Trace) -> Trace:
        """
        Replaces repeated activities in the trace with a suffix.
        """
        index = dict()
        ret = []
        for act in trace:
            if act not in index:
                ret.append(act)
                index[act] = 0
            else:
                index[act] = index[act] + 1
                id = index[act]
                ret.append(f"{act}##{id:02d}")
        return Trace(ret)
    
    def _discover_cyclic_dag(self, slog:EventLog) -> DependencyGraph:
        """
        Discover the cyclic DAG from the given simplifed event log,
        using the proposed approach by R. Argrawal D. et. al. in 1998
        through algorithm 3.

        The algorithm consists of the following steps:
            - process the log and replace repeated activities with a suffix
            - start with a graph consisting of vertices for each activity
                and no edges.
            - for each execution E and activities u,v in E, add the edge of
                (u, v) if u terminates before v starts.
            - remove all edges that appear in both directions, i.e. 
                for activities u,v, if the edges (u,v) and (v,u) are in 
                the graph, remove both of them.
            - For each strongly connected component of G, remove from E 
                all edges between vertices in the same strongly connected 
                component.
            - For each process execution in L:
                - Find the induced subgraph of G.
                - Compute the transitive reduction of the subgraph.
                - Mark those edges in E that are present in the transitive 
                    reduction.
            - Remove the unmarked edges in E.
            - merge the vertices that correspond to the different instances
                of the same activity and introduce edges between the merged
                verticies, if an subinstance had a edge between unmerged 
                vertices.
            - Return the graph.
        """
        slog = EventLog([
            self._suffix_repeated_activities(t)
            for t,i
            in slog
            for n 
            in range(i)
        ])
        retV = self._step_one(slog)
        retE = self._step_two(slog)
        graph = self._step_three(slog,retV,retE)
        graph = self._step_four(graph,retV,retE)
        if self._use_opt_five:
            marked = self._step_five_opt(slog,graph)
        else:
            marked = self._step_five(slog,graph)
        # step six
        graph = self._step_six(marked,graph)
        # step seven
        graph = self._step_seven(graph)
        info("returning a graph (|V|,|E|) :: ({},{})".format(
            len(graph.vertices()),len(graph.edges()))
            )
        return graph
    
    def _step_one(self, slog:EventLog) -> Set[DependencyNode]:
        """
        Creates a vertex for each activity seen in the log.
        """
        info("step one started")
        acts = slog.seen_activities()
        # step one
        retV = set([
            DependencyNode(act) 
            for act 
            in slog.seen_activities()
        ])
        info("step one completed")
        return retV

    def _step_two(self, slog:EventLog) -> Set[DependencyEdge]:
        """
        Computes the set of edges between activities, where each edge (A,B)
        denotes that activity A was eventually followed by activity B.

        If min_instances is set, then the edge must be observed at least
        min_instances times, by default set to 1. 
        """
        if self._use_opt_five:
            return self._step_two_opt(slog)
        info("step two started")
        retE = set()
        edges = dict()
        for trace,n in slog.__iter__():
            for left,right in product(range(len(trace)-1),range(1,len(trace))):
                if (left >= right):
                    continue
                edge = DependencyEdge(
                    DependencyNode(trace[left]),
                    DependencyNode(trace[right]),
                    n
                )
                if edge in retE:
                    for i in range(n):
                        edges[edge].increment()
                else:
                    retE.add(edge)
                    edges[edge] = edge
        # filter edges based on min_instances
        drops = set()
        for edge in retE:
            if edge.counter < self._min_instances:
                drops.add(edge)
        retE = retE.difference(drops)
        info("step two completed")
        return retE
    
    def _step_two_opt(self, slog:EventLog) -> Set[DependencyEdge]:
        """
        Parallel version of step two, that computes all eventually follows
        edges.
        """
        info("step two started")
        retE = set()
        edges = dict()
        from joblib import Parallel, delayed
        from tqdm import tqdm
        pool = Parallel(n_jobs=-2,return_as="generator_unordered")
        # define work 
        def work(trace:Trace, n:int)\
            -> Set[DependencyEdge]:
            edges = set()
            for left, right in product(
                range(len(trace)-1), range(1, len(trace))):
                if (left >= right):
                    continue
                edges.add(DependencyEdge( 
                    DependencyNode(trace[left]),
                    DependencyNode(trace[right]),
                    n)
                )
            return edges
        # prep work 
        tasks = [(trace, n ) for trace, n in slog]
        tasks = pool(delayed(work)(*task) for task in tasks)
        # add pb if on INFO 
        if get_logger().level == INFO:
            tasks = tqdm(tasks, desc="Launching jobs for step two", 
                         total=slog.get_nvariants())
        # sync work
        for workee in tasks:
            for edge in workee:
                if edge in edges:
                    for i in range(edge.counter):
                        edges[edge].increment()
                else:
                    edges[edge] = edge
                    retE.add(edge)
        # filter edges based on min_instances
        drops = set()
        for edge in retE:
            if edge.counter < self._min_instances:
                drops.add(edge)
        retE = retE.difference(drops)
        info("step two completed")
        return retE
        
    
    def _step_three(self, slog:EventLog, 
                    retV:Set[DependencyNode], retE:Set[DependencyEdge])\
        -> DependencyGraph:
        """
        Removes all edges that appear in both directions.
        """
        info("step three started")
        acts = slog.seen_activities()
        if get_logger().level == DEBUG:
            graph = DependencyGraph(retV,retE)
            debug(graph.__repr__())
            debug("graph before step three :: "+ graph.create_dot_form())
        for actA in acts:
            for actB in acts.difference({actA}):
                one_way = DependencyEdge(
                    DependencyNode(actA),
                    DependencyNode(actB)
                )
                if one_way in retE:
                    other_way = DependencyEdge(
                        DependencyNode(actB),
                        DependencyNode(actA)
                    )
                    if other_way in retE:
                        retE.discard(one_way)
                        retE.discard(other_way)
        graph = DependencyGraph(retV,retE)
        if get_logger().level == DEBUG:
            debug("graph after step three :: "+ graph.create_dot_form())
        info("step three completed")
        return graph

    def _step_four(self, graph:DependencyGraph, 
                   retV:Set[DependencyNode], retE:Set[DependencyEdge])\
        -> DependencyGraph:
        """
        Finds strongly connected components in the graph and removes all
        edges between vertices in the same strongly connected component.
        """
        info("step four started")
        components = find_strongly_connected_components(graph)
        for comp in components:
            for u in comp:
                for v in comp:
                    if u != v:
                        retE.discard(DependencyEdge(u,v))
        graph = DependencyGraph(retV,retE)     
        if get_logger().level == DEBUG:
            debug("graph after step four :: "+ graph.create_dot_form())
        info("step four completed")  
        return graph

    def _step_five(self, slog:EventLog, graph:DependencyGraph)\
        -> Set[DependencyEdge]:
        """
        Finds and marks all edges that are present in the induced subgraph
        for each trace, after the transitive reduction has been computed.
        """
        info("step five started")
        marked = set()
        for trace,_ in slog:
            sub = graph.induce_subgraph(trace)
            sub = sub.transitive_reduction()
            for edge in sub.edges():
                marked.add(edge)
        info("step five completed")
        return marked
    
    def _step_five_opt(self, slog:EventLog, graph:DependencyGraph)\
        -> Set[DependencyEdge]:
        """
        Optimised version of step five, that marks edges in parallel for
        all traces.
        """
        info("step five (opt) started")
        from joblib import Parallel, delayed
        from tqdm import tqdm
        pool = Parallel(n_jobs=-2,return_as="generator_unordered")
        # the work
        def mark(trace:Trace, graph:str)\
            -> str:
            from pmkoalas.discovery.agrawal_miner import DependencyGraph
            from pmkoalas.discovery.agrawal_miner import DependencyEdge 
            from pmkoalas.discovery.agrawal_miner import DependencyNode
            graph:DependencyGraph = eval(graph)
            marked = set()
            graph = graph.induce_subgraph(trace)
            graph = graph.transitive_reduction()
            for edge in graph.edges():
                marked.add(edge)
            return graph.edges().__repr__()
        # run the work
        graph_state = graph.__repr__()
        marks = pool(
            delayed(mark)(trace,graph_state)
            for trace,_ in slog
        )
        if (get_logger().level == INFO):
            marks = tqdm(marks, desc="launching jobs for step five (opt)", 
                 total=slog.get_nvariants())
        # sync over sets and keep the union from work
        marked = set()
        for markee in marks:
            markee = eval(markee)
            marked = marked.union(markee)
        info("step five (opt) completed")
        return marked

    
    def _step_six(self, marked:Set[DependencyEdge], graph:DependencyGraph)\
        -> DependencyGraph:
        """
        Removed unmarked edges from the graph.
        """
        info("step six started")
        retV = graph.vertices()
        retE = graph.edges()
        retE = retE.intersection(marked)
        info("step six completed")
        return DependencyGraph(retV,retE)

    def _step_seven(self, graph:DependencyGraph) -> DependencyGraph:
        """
        Merge the vertices into groups of equivalent activities, adding 
        edges between the merged vertices if an edge existed between a 
        member of a group and a member of another group.
        """
        info("step seven started")
        # find the groups of equivalent activities
        if (get_logger().level == DEBUG):
            debug("graph before step seven :: "+ graph.create_dot_form())
        groups = dict()
        for v in graph.vertices():
            label = v.label.split("##")[0]
            if label in groups:
                groups[label].add(v)
            else:
                groups[label] = set([v])
        debug(f"|groups| :: {len(groups)}")
        debug(f"found groups :: {groups}")
        retV = set()
        retE = set()
        edges = dict()
        # recreate nodes and edges
        for label in groups.keys():
            retV.add(DependencyNode(label))
            # add edges from the outedges for each member
            for member in groups[label]:
                for edge in graph.outedges(member):
                    tgt = edge.target.label.split("##")[0]
                    src = edge.source.label.split("##")[0]
                    if tgt == src:
                        continue
                    edge = DependencyEdge(
                        DependencyNode(src),
                        DependencyNode(tgt),
                        edge.counter
                    )
                    if edge in edges:
                        for i in range(edge.counter):
                            edges[edge].increment()
                    else:
                        edges[edge] = edge
                        retE.add(edge)
        graph = DependencyGraph(retV,retE)
        info("step seven completed")
        if (get_logger().level == DEBUG):
            debug("graph after step seven :: "+ graph.create_dot_form())
        return graph

    def compute_follows_relations(self, slog:EventLog) -> Set[Tuple[str,str]]:
        return compute_follows_relations(slog)
    
    def compute_dependencies(self, slog:EventLog) -> Set[Tuple[str,str]]:
        return compute_dependencies(slog)
    
    def compute_indepentent_activities(self, slog:EventLog) -> Set[Tuple[str,str]]:
        return compute_independent_activities(slog)