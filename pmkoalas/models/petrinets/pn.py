''' 
This module contains data structures for labelled Petri Nets.

Allows explicit place or transition ids for simpler comparison, especially
during testing.

For material on Petri Nets, see:
    - Quick and dirty introduction on wikipedia 
    https://en.wikipedia.org/wiki/Petri_net
   
Design Considerations:
    - The `Place` and `Transition` classes are hashable and comparable.
       - However, in order to support exporting and then re-importing a 
         Petri net, we use an identify attribute (pid/tid)
       - In python land, what you decide to use an identifier is up to you.
         - There are good cases for using an integer, say 4, or string, 
           say 'foo'.
         - These simple options make testing easier and repr's more readable.
       - However, if you plan to export and then reimport into ProM 
         or another tool (say pm4py), then you need to ensure that you 
         use a valid uuuid version 4 as the identifier. We offer support
         in various ways, one way is to leave the tid/pid as None and it 
         will be generated for you. 
            - The ProM implementation puts all elements into a hashmap
              based on the identifier, so it can silently break if you
              are not careful.
            - In many cases, you cannot even import without valid uuidv4s.
            - Similarly for pm4py, the identifier plays an important role
              if you plan to use their alignment tools.
        - Note, that hashing in python land occurs over the attributes of
          the node, so comparing a node with a identifier of an int 4 and
          a string "4" will be the same. We convert down to a string for
          identifiers to make life simple.
        - Also, hashing in python is salted so caching the hash is not 
          advised for threaded code. 
          See: https://docs.python.org/3.13/using/cmdline.html#cmdoption-R
'''
from collections.abc import Iterable
from copy import deepcopy
from typing import Union, FrozenSet, Dict, Set, Iterator
from uuid import uuid4

def verbosecmp(obj1:object,obj2:object) -> str:
    """
    This function produces a verbose statement about the given equality of
    the two objects.

    Returns a string statement about this equality.    
    """
    if obj1 == obj2:
        return "Same"
    result = ""
    if obj1.__dict__.keys() != obj2.__dict__.keys():
        ks1 = set(obj1.__dict__.keys())
        ks2 = set(obj2.__dict__.keys())
        result += f"Attributes not in both objects: {ks1 ^ ks2}\n"
    if obj1.__dict__ != obj2.__dict__:
        for k in obj1.__dict__:
            if k in obj2.__dict__ and obj1.__dict__[k] != obj2.__dict__[k] :
                result += f"Attribute {k} differs:\n"\
                        + f"  {obj1.__dict__[k]} vs\n  {obj2.__dict__[k]}\n"
    return result


class Place:
    """
    This a hashable and identifable place for a petri net.
    A place has a name and an identifier.
    """

    def __init__(self,name:str,pid:object=None):
        self._name = name
        # create an identifier.
        if (pid == None):
            self._pid = str(uuid4())
        else:
            self._pid = pid

    @property 
    def name(self) -> str:
        return self._name

    @property
    def pid(self) -> object:
        return self._pid

    @property
    def nodeId(self) -> str:
        return self._pid

    def __eq__(self,other) -> bool:
        if isinstance(other, type(self)):
            return self._name == other._name \
                and str(self._pid) == str(other._pid)
        return False

    def __hash__(self) -> int:
        return hash((self._name,str(self._pid)))

    def __str__(self) -> str:
        return f'({self.name})'  if self._pid is None \
               else f'({self.name}({self._pid}))'

    def __repr__(self) -> str:
        return f'Place("{self.name}",pid="{self.pid}")'


class Transition:
    """
    This is hashable and identifable transition for a Petri net.
    A transition has a name, an identifier, and can be silent.
    """

    def __init__(self,name:str,tid:str=None,silent:bool=False):
        self._name = name
        # create an identifier.
        if (tid == None):
            self._tid = str(uuid4())
        else:
            self._tid = tid
        # add extras
        self._silent = silent

    @property 
    def name(self) -> str:
        return self._name

    @property
    def silent(self) -> bool:
        return self._silent

    @property
    def tid(self) -> str:
        return self._tid

    @property
    def nodeId(self) -> str:
        return self._tid

    def __eq__(self,other) -> bool:
        if isinstance(other,type(self)):
            return self.name == other.name \
                and str(self.tid) == str(other.tid) \
                and self._silent == other._silent
        return False

    def __hash__(self) -> int:
        return hash((self._name,str(self._tid),self._silent))

    def __str__(self) -> str:
        return f'[{self.name}]'  if self._tid is None \
               else f'[{self.name}({self._tid})]'

    def __repr__(self) -> str:
        return f'Transition("{self.name}",tid="{self.tid}",' \
               + f'silent={self.silent})'

class Arc:
    """
    This is directed arc, which has no name or idenfitier, for Petri net.
    """

    def __init__(self,from_node:Union[Place,Transition],
                 to_node:Union[Place,Transition]):
        self._from_node = from_node
        self._to_node = to_node

    @property
    def from_node(self) -> Union[Place,Transition]:
        return self._from_node

    @property
    def to_node(self) -> Union[Place,Transition]:
        return self._to_node

    def __eq__(self,other) -> bool:
        if isinstance(other,type(self)):
            return self.from_node == other.from_node and \
                    self.to_node  == other.to_node
        return False

    def __hash__(self) -> int:
        return hash((self._from_node,self._to_node))

    def __str__(self) -> str:
        return f'{self.from_node} -> {self.to_node}' 

    def __repr__(self) -> str:
        return f'Arc(from_node={self.from_node.__repr__()},' \
               + f'to_node={self.to_node.__repr__()})'


class LabelledPetriNet:
    """
    A labelled Petri Net. It consists of places, transitions and directed arcs 
    between them.  Places and transitions have labels (names) and identifiers. 
    The net is also named.
    """

    def __init__(self, places:Iterable[Place], transitions:Iterable[Transition],
                 arcs:Iterable[Arc], 
                 name:str='Petri net'):
        self._places = set([ deepcopy(p) for p in places ])
        self._transitions = set([ deepcopy(t) for t in transitions])
        self._arcs = set([ deepcopy(a) for a in arcs])
        self._name = name
        self._postset_cache = dict(
            (node,self._postset(node)) 
            for node in 
            self._places.union(self._transitions)
        )
        self._preset_cache = dict(
            (node,self._preset(node))
            for node in
            self._places.union(self._transitions)
        )

    @property 
    def places(self) -> FrozenSet[Place]:
        return frozenset(self._places)

    @property
    def transitions(self) -> FrozenSet[Transition]:
        return frozenset(self._transitions)

    @property
    def arcs(self) -> FrozenSet[Arc]:
        return frozenset(self._arcs)

    @property
    def name(self) -> str:
        return self._name
    
    def postset(self,node:Union[Place,Transition]
        ) -> FrozenSet[Union[Place,Transition]]:
        """
        Returns the set of nodes that are reachable from the given node.
        """
        if node in self._postset_cache.keys():
            return self._postset_cache[node]
        else:
            raise ValueError(f"Node {node} does not belong to the net \n({self}).")
    
    def _postset(self,node:Union[Place,Transition]
        ) -> FrozenSet[Union[Place,Transition]]:
        """
        Computes the set of nodes that are reachable from the given node.
        """
        return frozenset([arc.to_node 
                          for arc in self.arcs 
                          if arc.from_node == node])
    
    def preset(self,node:Union[Place,Transition]
        ) -> FrozenSet[Union[Place,Transition]]:
        """
        Returns the set of nodes that can reach the given node.
        """
        if node in self._preset_cache.keys():
            return self._preset_cache[node]
        else:
            raise ValueError(f"Node {node} does not belong to the net \n({self}).")

    def _preset(self,node:Union[Place,Transition]
        ) -> FrozenSet[Union[Place,Transition]]:
        """
        Computes the set of nodes that can reach the given node.
        """
        return frozenset([arc.from_node 
                          for arc in self.arcs 
                          if arc.to_node == node])

    def __eq__(self,other) -> bool:
        if isinstance(other, type(self)):
            return self._name  == other._name and \
                   self._places == other._places and \
                   self._transitions == other._transitions and \
                   self._arcs   == self._arcs
        return False

    def __repr__(self) -> str:
        repr = "LabelledPetriNet(\n"
        # add places
        repr += "\tplaces=[\n"
        for p in self.places:
            repr += f"\t\t{p.__repr__()},\n"
        repr += "\t],\n"
        # add transitions
        repr += "\ttransitions=[\n"
        for t in self.transitions:
            repr += f"\t\t{t.__repr__()},\n"
        repr += "\t],\n"
        # add arcs
        repr += "\tarcs=[\n"
        for a in self.arcs:
            repr += f"\t\t{a.__repr__()},\n"
        repr += "\t],\n"
        # add name
        repr += f"\tname='{self.name}'\n"
        #close param
        repr += ")"
        return repr

    def __str__(self) -> str:
        _str = "LabelledPetriNet with name of '" + self._name + "'\n"
        _str += "\tPlaces: \n"
        for p in self.places:
            _str += f"\t\t- {p}\n"
        _str += "\tTransitions: \n"
        for t in self.transitions:
            _str += f"\t\t- {t}\n"
        _str += "\tArcs: \n"
        for a in self.arcs:
            _str += f"\t\t- {a}\n"
        return _str

class PetriNetMarking():
    """
    Data structure for a marking in a petri net, i.e. a multiset of places.
    """
    
    def __init__(self, marking:Dict[Place,int]) -> None:
        self._mark = deepcopy(marking)

    @property
    def mark(self) -> Dict[Place,int]:
        return deepcopy(self._mark)
    
    def contains(self, place:Place) -> bool:
        """
        Returns true if the place is in the marking.
        """
        return place in self
    
    # data-model functions
    def __getitem__(self, place:Place) -> int:
        if (self.contains(place)):
            return self._mark[place]
        return 0
    
    def __contains__(self, place:Place) -> None:
        if (isinstance(place, Place)):
            return place in self._mark and self._mark[place] > 0
        return False
    
    def __iter__(self) -> Iterator[Place]:
        return iter([p for p in self._mark if self._mark[p] > 0])
    
    ## self + other returns a new marking with the sum of the two
    def __add__(self, other:'PetriNetMarking') -> 'PetriNetMarking':
        if (not isinstance(other, type(self))):
            return NotImplemented
        new_mark = deepcopy(self._mark)
        for place in other._mark:
            if place in self:
                new_mark[place] = new_mark[place] + other._mark[place]
            else:
                new_mark[place] = other._mark[place]
        return PetriNetMarking(new_mark)
    
    ## self - other returns a new marking with the difference of the two
    def __sub__(self, other:'PetriNetMarking') -> 'PetriNetMarking':
        if (not isinstance(other, type(self))):
            return NotImplemented
        new_mark = deepcopy(self._mark)
        for place in other:
            if place in self:
                new_mark[place] = max(
                    new_mark[place] - other._mark[place],
                    0)
            else:
                new_mark[place] = 0
        return PetriNetMarking(new_mark)
    
    ## self << other checks that self is a subset of other
    def __lshift__(self, other:'PetriNetMarking') -> 'PetriNetMarking':
        if (not isinstance(other, type(self))):
            return NotImplemented
        for place in self:
            if place not in other._mark:
                return False
            if self._mark[place] > other._mark[place]:
                return False
        return True

    def __str__(self) -> str:
        vals = [ (i,v) for i,v in self._mark.items() if v > 0 ]
        return str(vals)
    
    def __eq__(self, other: object) -> bool:
        if (isinstance(other, type(self))):
            for place in self:
                if place not in other:
                    return False
                if self[place] != other[place]:
                    return False
            for place in other:
                if place not in self:
                    return False
            return True
        return False
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self._mark.items(),key=lambda x: x[0].name)))

class AcceptingPetriNet():
    """
    Abstraction to handle data for the execution of a `PetriNet`.
    """
    def __init__(self, net:LabelledPetriNet, inital:PetriNetMarking,
                 finals:Set[PetriNetMarking]) -> None:
        self._net = deepcopy(net)
        self._initial = deepcopy(inital)
        self._finals = deepcopy(finals)

    @property
    def net(self) -> LabelledPetriNet:
        return deepcopy(self._net)
    
    @property
    def initial_marking(self) -> PetriNetMarking:
        return deepcopy(self._initial)
    
    @property
    def final_markings(self) -> Set[PetriNetMarking]:
        return deepcopy(self._finals)
    
    def __eq__(self, other: object) -> bool:
        if (isinstance(other, type(self))):
            return self._net == other._net \
                and self._initial == other._initial \
                and self._finals == other._finals
    
class PetriNetSemantics():
    """
    Abstraction to handle the runtime execution semantics of a `PetriNet`.
    """
    def __init__(self, net:AcceptingPetriNet, curr:PetriNetMarking) -> None:
        self._anet = deepcopy(net)
        self._net = self._anet.net
        self._curr = deepcopy(curr)
        self._fires = self._firable()

    def fireable(self) -> Set[Transition]:
        """
        Returns the set of transitions that are fireable from the current marking.
        """
        return deepcopy(self._fires)

    def _firable(self) -> Set[Transition]:
        """
        Computes the set of transitions that are firable from the current marking.
        """
        ret = set()
        for tran in self._net.transitions:
            preset = self._net.preset(tran)
            preset = dict((f,1) for f in preset)
            if (PetriNetMarking(preset) << self._curr):
                ret.add(tran)
        return ret

    def peek(self, firing:Transition) -> 'PetriNetSemantics':
        """
        Peeks at the next marking that results from firing the given transition.
        """
        if (firing not in self._fires):
            raise ValueError("Given transition cannot fire from this marking.")
        postset = self._net.postset(firing)
        firing = dict( (f,1) for f in postset )
        firing = PetriNetMarking(firing)
        return PetriNetSemantics(self._net, self._curr - firing)

    def fire(self, firing:Transition) -> 'PetriNetSemantics':
        """
        Fires the given transition and returns the changed semantics.
        """
        if (firing not in self._fires):
            raise ValueError("Given transition cannot fire from this marking.")
        pre = dict( (f,1) for f in self._net.preset(firing) )
        mark = self._curr - PetriNetMarking(pre)
        post = dict( (f,1) for f in self._net.postset(firing) )
        mark = mark + PetriNetMarking(post)
        return PetriNetSemantics(self._anet, mark)

    def reached(self, mark:PetriNetMarking) -> bool:
        """
        Returns true if the given marking is reached.
        """
        return self._curr == mark

    # old interface
    def enabled(self) -> Set[Transition]:
        """
        returns the set of transitions that are enabled at this marking.
        """
        return self.fireable()

    def can_fire(self) -> Set[Transition]:
        """
        returns the set of transitions that can fire from this marking.
        """
        return self.enabled()
    
    def remark(self, firing:Transition) -> 'PetriNetSemantics':
        """
        Returns a new marking, that is one step from this marking by firing
        the given transition.
        """
        return self.fire(firing)
    
    def contains(self, place:Place) -> bool:
        """
        Returns true if the given place is in the marking.
        """
        if (place in self._mark.keys()):
            return self._mark[place] > 0
        return False
    
    def is_subset(self, other:'PetriNetMarking') -> bool:
        """
        Returns true if this marking is a subset of the other marking.
        """
        return self._mark << other
    
    def reached_final(self) -> bool:
        """
        Returns true if the marking is the final marking of the net.
        """
        for fmark in self._anet.final_markings:
            if (self.reached(fmark)):
                return True
        return False

    ## data-model functions
    def __str__(self):
        return f"{self._curr} -> {[ str(f) for f in self.fireable()]}"
    
    def __eq__(self, other: object) -> bool:
        if (isinstance(other, type(self))):
            return self._mark == other._mark and self._anet == other._anet
        return False
    
    def __hash__(self) -> int:
        return hash((self._mark,self._anet))
    
class ExecutablePetriNet():
    """
    Abstraction to contain all the data needed to execute a `PetriNet`.
    """
    def __init__(self, anet:AcceptingPetriNet, sem:PetriNetSemantics) -> None:
        self._anet = deepcopy(anet)
        self._sem = deepcopy(sem)

    @property
    def semantics(self) -> PetriNetSemantics:
        return deepcopy(self._sem)
    
    @property
    def anet(self) -> AcceptingPetriNet:
        return deepcopy(self._anet)
    
    ## data model functions
    def __eq__(self, other: object) -> bool:
        if (isinstance(other, type(self))):
            return self._anet == other._anet and self._sem == other._sem
        return False
    
    def __hash__(self) -> int:
        return hash((self._anet,self._sem))
    
def get_execution_semantics(anet:AcceptingPetriNet) -> ExecutablePetriNet:
    """
    Constructs an executable Petri net from the given Petri net and initial marking.
    """
    sem = PetriNetSemantics(anet, anet.initial_marking)
    return ExecutablePetriNet(anet, sem)