"""
This model contains the base abstraction layers for exporting a net into
a pnml file.
"""
from pmkoalas.models.petrinets.pn import LabelledPetriNet
from pmkoalas.models.petrinets.dpn import PetriNetWithData
from pmkoalas.models.petrinets.pn import AcceptingPetriNet
from pmkoalas.models.petrinets.dpn import GuardedTransition
from pmkoalas.models.petrinets.wpn import WeightedTransition

from uuid import UUID
import xml.etree.ElementTree as ET
from typing import Union

ENCODING='unicode'
PNML_URL='http://www.pnml.org/version-2009/grammar/pnmlcoremodel'

def convert_net_to_xml(
        net:Union[LabelledPetriNet,AcceptingPetriNet],
        include_prom_bits:bool=True       
    ) -> ET.Element: 
    """
    Converts a given Petri net to an XML structure that conforms with the pnml
    schema.

    See: http://www.pnml.org/version-2009/grammar/pnmlcoremodel.rng
    """
    if (isinstance(net,AcceptingPetriNet)):
        anet = net
        net = net.net
    else:
        anet = net
    # handlers for UUID for prombits
    from random import Random
    rd = Random(1998)
    def getUUID(given:str) -> str:
        try:
            uuid_obj = UUID(given, version=4)
            if str(uuid_obj) == given:
                return given
            raise ValueError("given was not a valid UUID")
        except Exception:
            return str(UUID(int=rd.getrandbits(128), version=4))
    # the conversion
    root = ET.Element('pnml')
    net_node = ET.SubElement(root,'net', 
            attrib={'type': PNML_URL,
                    'id':net.name} )
    net_name = ET.SubElement(net_node, "name")
    net_text = ET.SubElement(net_name, "text")
    net_text.text = net.name
    page = ET.SubElement(net_node,'page', id="page1")
    nodes = dict()
    attributes_for_guards = set()
    for place in net.places:
         # work out the id for the transition
        if isinstance(place.pid, int):
            pid = f"{place.pid}"
        else:
            pid = place.pid
        nodes[place] = pid
        placeNode = ET.SubElement(page,'place', 
            attrib={'id': pid } )
        if place.name:
            name_node = ET.SubElement(placeNode,'name')
            text_node = ET.SubElement(name_node,'text')
            text_node.text = place.name
        if (include_prom_bits):
            ET.SubElement(
                    placeNode, 'toolspecific',
                    attrib={
                        'tool' : "ProM",
                        'version' : "6.4",
                        'localNodeID' : getUUID(place.pid)
                    }
                )
        if isinstance(anet,AcceptingPetriNet):
            if anet.initial_marking.contains(place):
                imarking = ET.SubElement(placeNode,'initialMarking')
                text_node = ET.SubElement(imarking,'text')
                text_node.text = str(anet.initial_marking[place])
            fmark = list(anet.final_markings)[0]
            if fmark.contains(place):
                fmarking = ET.SubElement(placeNode,'finalMarking')
                text_node = ET.SubElement(fmarking,'text')
                text_node.text = str(fmark[place])

    for tran in net.transitions:
        # work out the id for the transition
        if isinstance(tran.tid, int):
            tid = f"{tran.tid}"
        else:
            tid = tran.tid
        nodes[tran] = tid
        # the default attributes for transitions
        attribs = { 'id' : tid}
        # check for guards 
        if isinstance(tran, GuardedTransition):
            attribs['guard'] = str(tran.guard)
            attributes_for_guards.update(tran.guard.variables())
        # check for silent
        if tran.silent:
            attribs['invisible'] = "true"
        # make a transition
        tranNode = ET.SubElement(page,'transition', 
                        attrib=attribs )
        if tran.name:
            name_node = ET.SubElement(tranNode,'name')
            text_node = ET.SubElement(name_node,'text')
            text_node.text = tran.name
        # include additional info for prom
        if (include_prom_bits):
            prom_node = ET.SubElement(
                tranNode, 'toolspecific',
                attrib={
                    'tool' : "ProM",
                    'version' : "6.4",
                    'activity' : "$invisible$" if tran.silent else "",
                    'localNodeID' : getUUID(tran.tid)
                }
            )
        # include stochastic info
        if isinstance(tran,WeightedTransition):
            ET.SubElement(tranNode,'toolspecific',
                        attrib={ 'tool':'StochasticPetriNet',
                                'version':'0.2', 
                                'invisible': str(tran.silent),
                                'priority': '1',
                                'weight' : str(tran.weight),
                                'distributionType': 'IMMEDIATE'} 
            )
    arcid = 1
    for arc in net.arcs:
        aid = "arc-"+str(arcid)
        arcNode = ET.SubElement(page,'arc',
            attrib={'source': nodes[arc.from_node], 
                    'target': nodes[arc.to_node],
                    'id':  aid} )
        arcid += 1
        if (include_prom_bits):
            prom_node = ET.SubElement(
                arcNode, 'toolspecific',
                attrib={
                    'tool' : "ProM",
                    'version' : "6.4",
                    'localNodeID' : getUUID(aid)
                }
            )
            arctype = ET.SubElement(
                arcNode, "arctype"
            )
            ET.SubElement(
                arctype, "text"
            ).text = "normal"

    # check if dpn and if so add variables
    if (isinstance(net,PetriNetWithData)):
        vars = ET.SubElement(net_node, 'variables')
        for attr in attributes_for_guards:
            var = ET.SubElement(vars, 'variable', attrib={'type':'java.lang.Double'})
            name = ET.SubElement(var, 'name')
            name.text = attr
    
    return root


def convert_net_to_xmlstr(
        net:LabelledPetriNet,
        include_prom_bits:bool=False             
    ) -> str: 
    """
    Converts a given Petri net, to an XML structure, and then returns a string
    representation of the indented XML tree.
    """
    xml = convert_net_to_xml(net,include_prom_bits)  
    ET.indent( xml ) 
    return ET.tostring(xml,encoding=ENCODING)

def export_net_to_pnml(
        net:LabelledPetriNet,fname:str,
        include_prom_bits:bool=True
        ) -> None: 
    """
    Converts a given Petri net, to an XML structure conforming to the pnml 
    schema, then writes out the XML to a given file location (fname).

    No checking of file location is done for you.
    """
    xml =  convert_net_to_xml(net,include_prom_bits=include_prom_bits)  
    ET.indent( xml ) 
    ET.ElementTree(xml).write(fname,xml_declaration=True, encoding="utf-8")