""""
This module contains the abstractions and structures for a data Petri net.

"""
from pmkoalas.models.petrinets.pn import LabelledPetriNet, Place
from pmkoalas.models.petrinets.pn import Transition, Arc
from pmkoalas.models.petrinets.pn import AcceptingPetriNet, PetriNetMarking
from pmkoalas.models.petrinets.pn import PetriNetSemantics
from pmkoalas.models.petrinets.pn import ExecutablePetriNet
from pmkoalas.models.petrinets.guards import Guard

from copy import deepcopy
from typing import Iterable, FrozenSet, Set

class GuardedTransition(Transition):
    """
    An abstraction for a transition with a guard.
    """

    def __init__(self, 
                 name: str, 
                 guard: Guard,
                 tid: str = None, 
                 silent: bool = False):
        super().__init__(name, tid, silent)
        self._guard = deepcopy(guard)

    @property
    def guard(self) -> Guard:
        return self._guard
    
    def __str__(self) -> str:
        return f"[{self.name} {self.guard}]"
    
    def __hash__(self) -> int:
        return hash((super().__hash__(), self.guard.__hash__()))
    
    def __eq__(self, other) -> bool:
        if super().__eq__(other):
            return self.guard == other.guard
        return False
    
    def __repr__(self) -> str:
        return f'GuardedTransition("{self.name}",guard={self.guard.__repr__()}'\
               + f',tid="{self.tid}",silent={self.silent})'
    
class PetriNetWithData(LabelledPetriNet):
    """
    An abstraction for extending a Petri net to one with data. This abstraction
    only includes guards.
    """

    def __init__(self, places: Iterable[Place], 
                 transitions: Iterable[GuardedTransition], 
                 arcs: Iterable[Arc], 
                 name: str = 'Petri net with Data'):
        super().__init__(places, transitions, arcs, name)

    @property
    def transitions(self) -> FrozenSet[GuardedTransition]:
        return deepcopy(self._transitions)
    
    def __repr__(self) -> str:
        repr = "PetriNetWithData(\n"
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
    
class AcceptingDataPetriNet(AcceptingPetriNet):
    """
    Further structure for a data Petri net that contains its initial marking
    and possible final markings.
    """
    def __init__(self, net:PetriNetWithData, inital:PetriNetMarking, 
                 finals:Set[PetriNetMarking]):
        super().__init__(net, inital, finals)

    @property
    def net(self) -> PetriNetWithData:
        return super().net

class DataPetriNetSemantics(PetriNetSemantics):
    """
    An abstraction for the semantics of a data Petri net.
    """
    def __init__(self, net: PetriNetWithData, curr: PetriNetMarking):
        super().__init__(net, curr)

    def fireable(self) -> Set[GuardedTransition]:
        return super().fireable()
    
    def peek(self, firing: GuardedTransition) -> 'DataPetriNetSemantics':
        return super().peek(firing)
    
    def fire(self, firing: GuardedTransition) -> 'DataPetriNetSemantics':
        return super().fire(firing)

class ExecutableDataPetriNet(ExecutablePetriNet):
    """
    An abstraction for a data Petri net that can be executed.
    """
    def __init__(self, anet:AcceptingDataPetriNet, sem:DataPetriNetSemantics):
        super().__init__(anet, sem)

    @property
    def semantics(self) -> DataPetriNetSemantics:
        return super().semantics
    
    @property
    def anet(self) -> AcceptingDataPetriNet:
        return super().anet

def get_execution_semantics(anet:AcceptingDataPetriNet) -> ExecutableDataPetriNet:
    """
    Constructs an executable data Petri net from the given data Petri net and
    initial marking.
    """
    sem = DataPetriNetSemantics(anet, anet.initial_marking)
    return ExecutableDataPetriNet(anet, sem)