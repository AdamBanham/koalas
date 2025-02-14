"""
This module contains helpers to create peretty dot (graphviz) digraphs 
for petri-net-type structures.

"""
from pmkoalas.models.petrinets.pn import LabelledPetriNet

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
        # fstr += f'label="{tran.weight}", style="filled",'
        height = self._default_height
        fstr += f'height="{height}", width="{height}"'
        fstr += '];\n'
        return fstr

    def transform_place(self,place,pi) -> str:
        fstr = '{} [shape="circle",label="{}"];\n'
        return fstr.format('n' + str(pi),place.name)

    def transform_arc(self,arc) -> str:
        from_node = self._nodemap[arc.from_node.nodeId]
        to_node = self._nodemap[arc.to_node.nodeId]
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
            self._nodemap[pl.nodeId] = ni
            dotstr += self.transform_place(pl,ni)
        for tr in self._pn.transitions:
            ni += 1
            self._nodemap[tr.nodeId] = ni
            dotstr += self.transform_transition(tr,ni)
        for ar in self._pn.arcs:
            dotstr += self.transform_arc(ar)
        dotstr += '}\n'
        return dotstr

def convert_net_to_dot(net:LabelledPetriNet) -> str:
    return PetriNetDOTFormatter(net).transform_net()