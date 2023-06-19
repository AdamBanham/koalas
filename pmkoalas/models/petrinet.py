
''' 
Weighted Petri net with place and transition labels.

Allows explicit place or transition ids for simpler comparison, especially
during testing.
'''
from collections.abc import Iterable
from typing import Union
import xml.etree.ElementTree as ET

ENCODING='unicode'

# Candidate to move to a utility package
def steq(self,other):
    if type(other) is type(self):
        return self.__dict__ == other.__dict__
    return False

def verbosecmp(obj1,obj2):
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
    def __init__(self,name,pid=None):
        self._name = name
        self._pid = pid

    @property 
    def name(self):
        return self._name

    @property
    def pid(self):
        return self._pid

    @property
    def nodeId(self):
        return self._pid

    def __eq__(self,other):
        if type(other) == type(self):
            return self.name == other.name and self.pid == other.pid
        return False

    def __hash__(self):
        return hash((self._name,self._pid))

    def __str__(self):
        return f'({self.name})'  if self._pid is None \
               else f'({self.name}({self._pid}))'

    def __repr__(self):
        return 'Place:' + str(self)


class Transition:
    def __init__(self,name,tid=None,weight=None,silent=None):
        self._name = name
        self._tid = tid
        if weight is None:
            self._weight = 1
        else:
            self._weight = weight
        if not silent:
            self._silent = False
        else:
            self._silent = True

    @property 
    def name(self):
        return self._name

    @property
    def silent(self):
        return self._silent

    @property
    def tid(self):
        return self._tid

    @property
    def nodeId(self):
        return self._tid

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self,value):
        self._weight = value

    def __eq__(self,other):
        if type(self) == type(other):
            return self.name == other.name and self.tid == other.tid and  \
                   self.weight == other.weight and self._silent == other._silent
        return False

    def __hash__(self):
        return hash((self._name,self._tid,self._weight,self._silent))

    def __str__(self):
        return f'[{self.name} {self.weight}]'  if self._tid is None \
               else f'[{self.name}({self._tid}) {self.weight}]'

    def __repr__(self):
        return 'Transition:' + str(self)


SILENT_TRANSITION_DEFAULT_NAME='tau'
def silentTransition(name=None,tid=None,weight=None):
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
    def __init__(self,fromNode,toNode):
        self._fromNode = fromNode
        self._toNode = toNode

    @property
    def fromNode(self):
        return self._fromNode

    @property
    def toNode(self):
        return self._toNode

    def __eq__(self,other):
        if type(other) is type(self):
            return self.fromNode == other.fromNode and \
                    self.toNode  == other.toNode
        return False

    def __hash__(self):
        return hash((self._fromNode,self._toNode))

    def __str__(self):
        return f'{self.fromNode} -> {self.toNode}' 

    def __repr__(self):
        return 'Arc:' + str(self)



'''
Petri net with a label. Create the components first and call the constructor.
'''
class LabelledPetriNet:
    def __init__(self,places:Iterable[Place],transitions:Iterable[Transition],
                 arcs:Iterable[Arc],label:str=None):
        self._places = set(places)
        self._transitions = set(transitions)
        self._arcs = set(arcs)
        if label is None:
            self._label = 'Petri net'
        else:
            self._label = label

    @property 
    def places(self) -> Iterable[Place]:
        return frozenset(self._places)

    @property
    def transitions(self) -> Iterable[Transition]:
        return frozenset(self._transitions)

    @property
    def arcs(self) -> Iterable[Arc]:
        return frozenset(self._arcs)

    @property
    def label(self) -> str:
        return self._label

    def __eq__(self,other) -> bool:
        if isinstance(other,self.__class__):
            return self._label  == other._label and \
                   self._places == other._places and \
                   self._transitions == other._transitions and \
                   self._arcs   == self._arcs
        return False

    def reprcontents(self) -> str:
        return f"places: {self._places} transitions: {self._transitions} arcs: {self._arcs}"

    def __repr__(self) -> str:
        return f"LabelledPetriNet:{self._label} " + self.reprcontents()

    def __str__(self) -> str:
        return "LabelledPetriNet(" + self._label + ")\n" \
            +  " Places: " + str(self.places) + "\n" \
            +  " Trans: " + str(self.transitions) + "\n" \
            +  " Arcs: " + str(self.arcs)
    

'''
Petri net intended to be modified after creation. Eg, create the net then call 
addPlace(), addTransition, and so on.
'''
class MutableLabelledPetriNet(LabelledPetriNet):
    def __init__(self,label:str=None):
        super(MutableLabelledPetriNet,self).__init__(set(),set(),set(),label)

    def addPlace(self,place:Place):
        self._places.add(place)

    def addTransition(self,tran:Transition):
        self._transitions.add(tran)

    def addArc(self,arc:Arc):
        self._arcs.add(arc)

    def addArcForNodes(self,fromNode:Union[Place,Transition],
                             toNode:Union[Place,Transition]):
        self.addArc(Arc(fromNode,toNode))

    def __repr__(self):
        return f"MutableLabelledPetriNet:{self._label} " + self.reprcontents()

    def __eq__(self,other):
        if isinstance(other,LabelledPetriNet):
            return self._label  == other._label and \
                   self._places == other._places and \
                   self._transitions == other._transitions and \
                   self._arcs   == self._arcs
        return False



class PetriNetDOTFormatter:
    def __init__(self,pn,font='SimSun'):
        self._pn = pn
        self._font = font
        self._nodemap = {}
        self._defaultHeight = 0.2

    def tranDOT(self,tran,ti):
        fstr = 'n{} [shape="box",margin="0, 0.1",label="{} {}",style="filled"];\n'
        tl = tran.name if tran.name and tran.name != 'tau' else '&tau;'
        fstr = f'n{str(ti)} [shape="box",margin="0, 0.1",'
        fstr += f'label="{tran.weight}", style="filled",'
        height = self._defaultHeight
        fstr += f'height="{height}", width="{height}"'
        fstr += '];\n'
        return fstr

    def placeDOT(self,place,pi):
        fstr = '{} [shape="circle",label="{}"];\n'
        return fstr.format('n' + str(pi),place.name)

    def arcDOT(self,arc):
        fromNode = self._nodemap[arc.fromNode]
        toNode = self._nodemap[arc.toNode]
        return f'n{fromNode}->n{toNode}\n'

    def netToDOT(self):
        dotstr = ""
        dotstr += 'digraph G{\n'
        dotstr += f'ranksep=".3"; fontsize="14"; remincross=true; margin="0.0,0.0"; fontname="{self._font}";rankdir="LR";charset=utf8;\n'
        dotstr += 'edge [arrowsize="0.5"];\n'
        dotstr += f'node [height="{self._defaultHeight}",width="{self._defaultHeight}",fontname="{self._font}"'
        dotstr += ',fontsize="14"];\n'
        dotstr += 'ratio=0.4;\n'
        ni = 1
        for pl in self._pn.places:
            ni += 1
            self._nodemap[pl] = ni
            dotstr += self.placeDOT(pl,ni)
        for tr in self._pn.transitions:
            ni += 1
            self._nodemap[tr] = ni
            dotstr += self.tranDOT(tr,ni)
        for ar in self._pn.arcs:
            dotstr += self.arcDOT(ar)
        dotstr += '}\n'
        return dotstr


def exportToDOT(net:LabelledPetriNet) -> str:
    return PetriNetDOTFormatter(net).netToDOT()



PNML_URL='http://www.pnml.org/version-2009/grammar/pnmlcoremodel',

def exportToPNMLObj(net:LabelledPetriNet) -> ET.Element: 
    root = ET.Element('pnml')
    netNode = ET.SubElement(root,'net', 
            attrib={'type':PNML_URL,
                    'id':net.label} )
    page = ET.SubElement(netNode,'page', id="page1")
    for place in net.places:
        placeNode = ET.SubElement(page,'place', attrib={'id':str(place.pid) } )
        if place.name:
            nameNode = ET.SubElement(placeNode,'name')
            textNode = ET.SubElement(nameNode,'text')
            textNode.text = place.name
    for tran in net.transitions:
        tranNode = ET.SubElement(page,'transition', 
                        attrib={'id':str(tran.tid) } )
        if tran.name:
            nameNode = ET.SubElement(tranNode,'name')
            textNode = ET.SubElement(nameNode,'text')
            textNode.text = tran.name
        tsNode = ET.SubElement(tranNode,'toolspecific',
                        attrib={ 'tool':'StochasticPetriNet',
                                 'version':'0.2', 
                                 'invisible': str(tran.silent),
                                 'priority': '1',
                                 'weight' : str(tran.weight),
                                 'distributionType': 'IMMEDIATE'} )
    arcid = 1
    for arc in net.arcs:
        arcNode = ET.SubElement(page,'arc',
                    attrib={'source': str(arc.fromNode.nodeId), 
                            'target': str(arc.toNode.nodeId),
                            'id': str(arcid) } )
        arcid += 1
    return root


def exportToPNMLStr(net:LabelledPetriNet) -> ET.Element: 
    xml = exportToPNMLObj(net)  
    ET.indent( xml ) 
    return ET.tostring(xml,encoding=ENCODING)

def exportToPNML(net:LabelledPetriNet,fname:str): 
    xml =  exportToPNMLObj(net)  
    ET.indent( xml ) 
    ET.ElementTree(xml).write(fname,xml_declaration=True, encoding="utf-8")

