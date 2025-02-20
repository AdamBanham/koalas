"""
This module contains the abstractions and structures for a weighted Petri 
nets or stochastic Petri nets. These nets are used to model the likelihood
of actions in a systems at runtime.

See:
    - Process mining with labelled stochastic nets. Adam Burke. 2024.
    - Bause and Kritzinger (2002) - Stochastic Petri Nets: An Introduction 
    to the Theory. Freely available textbook at
    https://www.researchgate.net/publication/258705139_Stochastic_Petri_Nets_-An_Introduction_to_the_Theory
"""
from pmkoalas.models.petrinets.pn import Transition, Arc, Place
from pmkoalas.models.petrinets.pn import LabelledPetriNet, AcceptingPetriNet
from pmkoalas.models.petrinets.pn import PetriNetMarking, PetriNetSemantics
from pmkoalas.models.petrinets.pn import ExecutablePetriNet

from typing import Iterable, FrozenSet, Union, Set
class WeightedTransition(Transition):
    """
    A transition with an associated weight.
    """
    def __init__(self, name:str, tid:object = None, 
                 silent:bool = False, weight:float = 1):
        super().__init__(name, tid, silent)
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight
    
    @weight.setter
    def weight(self,value:float) -> None:
        self._weight = value

    # data model methods
    def __str__(self) -> str:
        return f"[{self.name}({self._tid}) {self.weight}]"
    
    def __eq__(self,other) -> bool:
        if (super().__eq__(other)):
            return self.weight == other.weight
        return False

    def __hash__(self) -> int:
        return hash((super().__hash__(),self.weight))
    
    def __repr__(self) -> str:
        return f'WeightedTransition("{self.name}",tid="{self.tid}",' \
               + f'silent={self.silent}, weight={self.weight})'
    
class WeightedPetriNet(LabelledPetriNet):
    """
    A Petri net with transitions that have weights.
    """
    def __init__(self, places: Iterable[Place], 
                 transitions: Iterable[WeightedTransition], 
                 arcs: Iterable[Arc], 
                 name: str = 'Weighted Petri net'):
        super().__init__(places, transitions, arcs, name)
    
    @property
    def transitions(self) -> FrozenSet[WeightedTransition]:
        return frozenset([t for t in self._transitions])
    
    def preset(self, node:Union[Place,WeightedTransition]
               ) -> FrozenSet[Union[Place,WeightedTransition]]:
        return super().preset(node)
    
    def postset(self, node:Union[Place,WeightedTransition]
                ) -> FrozenSet[Union[Place,WeightedTransition]]:
        return super().postset(node)
    
    def __repr__(self) -> str:
        repr = "WeightedLabelledPetriNet(\n"
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
        _str = "WeightedLabelledPetriNet with name of '" + self._name + "'\n"
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


class BuildablePetriNet(WeightedPetriNet):
    """
    Allows for the builder design pattern to be used for constructing a 
    Petri net. Users can add places, transitions and arcs through a single 
    chain of method calls. See usage below.

    Usage
    -----
    ```
    # setup elements
    buildable = BuildablePetriNet("dupe_tran_with_id")
    initial_place = Place("I",1)
    ta1 = Transition("a",1)
    ta2 = Transition("a",2)
    tb = Transition("b",3)
    finalPlace = Place("F",2)
    # build net
    buildable.add_place(initialPlace) \\
        .add_transition(ta1) \\
        .add_transition(ta2) \\
        .add_transition(tb) \\
        .add_place(finalPlace) \\
        .add_arc_between(initialPlace, ta1) \\
        .add_arc_between(ta1,finalPlace) \\
        .add_arc_between(initialPlace, ta2) \\
        .add_arc_between(ta2,finalPlace) \\
        .add_arc_between(initialPlace, tb) \\
        .add_arc_between(tb,finalPlace) 
    # get a state of build
    net = buildable.create_net()
    ```
    """
    def __init__(self,label:str=None):
        super().__init__(set(),set(),set(),label)

    def add_place(self,place:Place) -> 'BuildablePetriNet':
        "Adds a place to the net."
        self._places.add(place)
        return self

    def add_transition(self,tran:WeightedTransition) -> 'BuildablePetriNet':
        "Adds a tranistion to the net."
        self._transitions.add(tran)
        return self

    def add_arc(self,arc:Arc)-> 'BuildablePetriNet':
        "Adds an arc to the net."
        self._arcs.add(arc)
        return self

    def add_arc_between(self,from_node:Union[Place,WeightedTransition],
                             to_node:Union[Place,WeightedTransition]
                        ) -> 'BuildablePetriNet' :
        "Constructs an arc between the given nodes and adds it to the net."
        self.add_arc(Arc(from_node,to_node))
        return self

    def create_net(self) -> WeightedPetriNet:
        "Returns a Petri net of the current built state"
        return WeightedPetriNet(
            self._places,
            self._transitions,
            self._arcs,
            self._name
        )

    def __eq__(self,other):
        if isinstance(other,type(self)) or isinstance(other,LabelledPetriNet):
            return self._name  == other._name and \
                   self._places == other._places and \
                   self._transitions == other._transitions and \
                   self._arcs   == self._arcs
        return False

class WeightedAcceptingPetriNet(AcceptingPetriNet):
    """
    A weighted Petri net with marking information.
    """
    def __init__(self, net:WeightedPetriNet,
                 inital:PetriNetMarking, 
                 finals:Set[PetriNetMarking]):
        super().__init__(net, inital, finals)

class WeightedPetriNetSemantics(PetriNetSemantics):
    """
    The semantics of a weighted Petri net.
    """
    def __init__(self, wanet:WeightedAcceptingPetriNet, curr:PetriNetMarking):
        super().__init__(wanet, curr)

    def fireable(self) -> set[WeightedTransition]:
        return super().fireable()
    
    def peek(self, tran:WeightedTransition) -> 'WeightedPetriNetSemantics':
        ret = super().peek(tran)
        return WeightedPetriNetSemantics(ret._anet, ret._curr)
    
    def fire(self, tran:WeightedTransition) -> 'WeightedPetriNetSemantics':
        ret = super().fire(tran)
        return WeightedPetriNetSemantics(ret._anet, ret._curr)
    
class ExecutableWeightedPetriNet(ExecutablePetriNet):
    """
    An executable weighted Petri net.
    """
    def __init__(self, wanet:WeightedAcceptingPetriNet, 
                 sem:WeightedPetriNetSemantics):
        super().__init__(wanet, sem)

    @property
    def semantics(self) -> WeightedPetriNetSemantics:
        return self._sem
    
    @property
    def anet(self) -> WeightedAcceptingPetriNet:
        return self._anet

def get_execution_semantics(wanet:WeightedAcceptingPetriNet):
    """
    Returns the execution semantics of a given weighted Petri net.
    """
    sem = WeightedPetriNetSemantics(wanet, wanet.initial_marking)
    return ExecutableWeightedPetriNet(wanet, sem)