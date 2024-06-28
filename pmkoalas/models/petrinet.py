''' 
Weighted Petri net with place and transition labels.

Allows explicit place or transition ids for simpler comparison, especially
during testing.

For material on Petri Nets, see:
    - Quick and dirty introduction on wikipedia https://en.wikipedia.org/wiki/Petri_net
    - Bause and Kritzinger (2002) - Stochastic Petri Nets: An Introduction to the Theory. Freely available textbook https://www.researchgate.net/publication/258705139_Stochastic_Petri_Nets_-An_Introduction_to_the_Theory
'''

from collections.abc import Iterable
from typing import Union,FrozenSet
import xml.etree.ElementTree as ET
from uuid import uuid4,UUID

ENCODING='unicode'

# Candidate to move to a utility package
def steq(self,other):
    if type(other) is type(self):
        return self.__dict__ == other.__dict__
    return False

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

    def __init__(self,name:str,pid:str=None):
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
    def pid(self) -> str:
        return self._pid

    @property
    def nodeId(self) -> str:
        return self._pid

    def __eq__(self,other) -> bool:
        if type(other) == type(self):
            return self.name == other.name and self.pid == other.pid
        return False

    def __hash__(self) -> int:
        return hash((self._name,self._pid))

    def __str__(self) -> str:
        return f'({self.name})'  if self._pid is None \
               else f'({self.name}({self._pid}))'

    def __repr__(self) -> str:
        return f'Place("{self.name}",pid="{self.pid}")'

class Transition:
    """
    This is hashable and identifable transition for a Petri net.
    A transition has a name, an identifier, a possible weight and can be silent.
    """

    def __init__(self,name:str,tid:str=None,weight:float=1.0,silent:bool=False):
        self._name = name
        # create an identifier.
        if (tid == None):
            self._tid = str(uuid4())
        else:
            self._tid = tid
        # add extras
        self._weight = weight
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

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self,value:float) -> None:
        self._weight = value

    def __eq__(self,other) -> bool:
        if type(self) == type(other):
            return self.name == other.name and self.tid == other.tid and  \
                   self.weight == other.weight and self._silent == other._silent
        return False

    def __hash__(self) -> int:
        return hash((self._name,self._tid,self._weight,self._silent))

    def __str__(self) -> str:
        return f'[{self.name} {self.weight}]'  if self._tid is None \
               else f'[{self.name}({self._tid}) {self.weight}]'

    def __repr__(self) -> str:
        return f'Transition("{self.name}",tid="{self.tid}",weight={self.weight},' \
               + f'silent={self.silent})'

SILENT_TRANSITION_DEFAULT_NAME='tau'
def silent_transition(name=None,tid=None,weight=None):
    tn = SILENT_TRANSITION_DEFAULT_NAME
    if name:
        tn = name
    tw = 1
    ttid = None
    if tid:
        ttid = tid
    if weight:
        tw = weight
    return Transition(name=tn,weight=tw,tid=ttid,silent=True)

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
        if type(other) is type(self):
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
    This is a data structure for a class of Petri Nets.
    This class consists of places, transitions and directed arcs 
    between them.
    The class contract implies that places and transitions have 
    labels/names and identifiers. Each instance of this class, 
    has a name or title for the net.
    """

    def __init__(self, places:Iterable[Place], transitions:Iterable[Transition],
                 arcs:Iterable[Arc], name:str='Petri net'):
        self._places = set(places)
        self._transitions = set(transitions)
        self._arcs = set(arcs)
        self._name = name

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

    def __eq__(self,other) -> bool:
        if isinstance(other,self.__class__):
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
    

class BuildablePetriNet(LabelledPetriNet):
    """
    This class allows for the builder design pattern to be used
    for constructing a petri net. It allows for users to quickly
    add places, transitions and arcs through a single chain of
    method calls. See usage below.

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
        super(BuildablePetriNet,self).__init__(set(),set(),set(),label)

    def add_place(self,place:Place) -> 'BuildablePetriNet':
        "Adds a place to the net."
        self._places.add(place)
        return self

    def add_transition(self,tran:Transition) -> 'BuildablePetriNet':
        "Adds a tranistion to the net."
        self._transitions.add(tran)
        return self

    def add_arc(self,arc:Arc)-> 'BuildablePetriNet':
        "Adds an arc to the net."
        self._arcs.add(arc)
        return self

    def add_arc_between(self,from_node:Union[Place,Transition],
                             to_node:Union[Place,Transition]
                        ) -> 'BuildablePetriNet' :
        "Constructs an arc between the given nodes and adds it to the net."
        self.add_arc(Arc(from_node,to_node))
        return self

    def create_net(self) -> LabelledPetriNet:
        "Returns a Petri net of the current built state"
        return eval(self.__repr__())

    def __eq__(self,other):
        if isinstance(other,LabelledPetriNet):
            return self._name  == other._name and \
                   self._places == other._places and \
                   self._transitions == other._transitions and \
                   self._arcs   == self._arcs
        return False

class PetriNetDOTFormatter:
    """
    This class creates a dot (graphviz) structure for displaying Petri nets. 
    Used as internal machinery for exporting to a dot file.
    """
    def __init__(self,pn:LabelledPetriNet,font:str='SimSun'):
        self._pn = pn
        self._font = font
        self._nodemap = {}
        self._default_height = 0.2

    def transform_transition(self,tran,ti) -> str:
        fstr = 'n{} [shape="box",margin="0, 0.1",label="{} {}",style="filled"];\n'
        tl = tran.name if tran.name and tran.name != 'tau' else '&tau;'
        fstr = f'n{str(ti)} [shape="box",margin="0, 0.1",'
        fstr += f'label="{tran.weight}", style="filled",'
        height = self._default_height
        fstr += f'height="{height}", width="{height}"'
        fstr += '];\n'
        return fstr

    def transform_place(self,place,pi) -> str:
        fstr = '{} [shape="circle",label="{}"];\n'
        return fstr.format('n' + str(pi),place.name)

    def transform_arc(self,arc) -> str:
        from_node = self._nodemap[arc.from_node]
        to_node = self._nodemap[arc.to_node]
        return f'n{from_node}->n{to_node}\n'

    def transform_net(self) -> str:
        dotstr = ""
        dotstr += 'digraph G{\n'
        dotstr += f'ranksep=".3"; fontsize="14"; remincross=true; margin="0.0,0.0"; fontname="{self._font}";rankdir="LR";charset=utf8;\n'
        dotstr += 'edge [arrowsize="0.5"];\n'
        dotstr += f'node [height="{self._default_height}",width="{self._default_height}",fontname="{self._font}"'
        dotstr += ',fontsize="14"];\n'
        dotstr += 'ratio=0.4;\n'
        ni = 1
        for pl in self._pn.places:
            ni += 1
            self._nodemap[pl] = ni
            dotstr += self.transform_place(pl,ni)
        for tr in self._pn.transitions:
            ni += 1
            self._nodemap[tr] = ni
            dotstr += self.transform_transition(tr,ni)
        for ar in self._pn.arcs:
            dotstr += self.transform_arc(ar)
        dotstr += '}\n'
        return dotstr

def convert_net_to_dot(net:LabelledPetriNet) -> str:
    return PetriNetDOTFormatter(net).transform_net()

PNML_URL='http://www.pnml.org/version-2009/grammar/pnmlcoremodel'

def convert_net_to_xml(net:LabelledPetriNet,
        include_prom_bits:bool=False       
    ) -> ET.Element: 
    """
    Converts a given Petri net to an XML structure that conforms with the pnml
    schema.

    See: http://www.pnml.org/version-2009/grammar/pnmlcoremodel.rng
    """
    root = ET.Element('pnml')
    net_node = ET.SubElement(root,'net', 
            attrib={'type': PNML_URL,
                    'id':net.name} )
    page = ET.SubElement(net_node,'page', id="page1")
    for place in net.places:
        placeNode = ET.SubElement(page,'place', attrib={'id':str(place.pid) } )
        if place.name:
            name_node = ET.SubElement(placeNode,'name')
            text_node = ET.SubElement(name_node,'text')
            text_node.text = place.name
    for tran in net.transitions:
        tranNode = ET.SubElement(page,'transition', 
                        attrib={'id':str(tran.tid) } )
        if tran.name:
            name_node = ET.SubElement(tranNode,'name')
            text_node = ET.SubElement(name_node,'text')
            text_node.text = tran.name
        # include additional info for prom
        if (include_prom_bits):
            if isinstance(tran.tid, int):
                from random import Random
                rd = Random(tran.tid)
                localNode = str(UUID(int=rd.getrandbits(128), version=4))
            else:
                localNode = tran.tid
            if  tran.silent:
                prom_node = ET.SubElement(
                    tranNode, 'toolspecific',
                    attrib={
                        'tool' : "ProM",
                        'version' : "6.4",
                        'activity' : "$invisible$",
                        'localNodeID' : localNode
                    }
                )
            else:
                prom_node = ET.SubElement(
                    tranNode, 'toolspecific',
                    attrib={
                        'tool' : "ProM",
                        'version' : "6.4",
                        'localNodeID' : localNode
                    }
                )
        # include stochastic info
        ts_node = ET.SubElement(tranNode,'toolspecific',
                        attrib={ 'tool':'StochasticPetriNet',
                                 'version':'0.2', 
                                 'invisible': str(tran.silent),
                                 'priority': '1',
                                 'weight' : str(tran.weight),
                                 'distributionType': 'IMMEDIATE'} )
    arcid = 1
    for arc in net.arcs:
        arcNode = ET.SubElement(page,'arc',
                    attrib={'source': str(arc.from_node.nodeId), 
                            'target': str(arc.to_node.nodeId),
                            'id': str(arcid) } )
        arcid += 1
    return root


def convert_net_to_xmlstr(net:LabelledPetriNet) -> str: 
    """
    Converts a given Petri net, to an XML structure, and then returns a string
    representation of the indented XML tree.
    """
    xml = convert_net_to_xml(net)  
    ET.indent( xml ) 
    return ET.tostring(xml,encoding=ENCODING)

def export_net_to_pnml(
        net:LabelledPetriNet,fname:str,
        include_prom_bits:bool=False
        ) -> None: 
    """
    Converts a given Petri net, to an XML structure conforming to the pnml 
    schema, then writes out the XML to a given file location (fname).

    No checking of file location is done for you.
    """
    xml =  convert_net_to_xml(net,include_prom_bits=include_prom_bits)  
    ET.indent( xml ) 
    ET.ElementTree(xml).write(fname,xml_declaration=True, encoding="utf-8")

