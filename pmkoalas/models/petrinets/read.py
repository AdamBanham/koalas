"""
This module contains the abstraction layer that reads an arbitrary pnml file.

TODO: Craft the abstraction layer for reading pnml files.
"""
from pmkoalas.models.petrinets.pn import LabelledPetriNet, Place
from pmkoalas.models.petrinets.pn import Transition, Arc
from pmkoalas.models.petrinets.pn import AcceptingPetriNet, PetriNetMarking
from pmkoalas.models.petrinets.dpn import PetriNetWithData, GuardedTransition
from pmkoalas.models.petrinets.dpn import AcceptingDataPetriNet
from pmkoalas.models.petrinets.guards import Guard,Expression

from os import path
from copy import deepcopy
from xml.etree.ElementTree import parse

def parse_pnml_into_lpn(filepath:str,
        use_localnode_id:bool=True) -> LabelledPetriNet:
    """
    Constructs a labelled Petri net from the given filepath to a pnml file.
    """
    # setup compontents
    initial_marking = {}
    final_marking = {}
    # begin parsing
    ## check that file exists
    if not path.exists(filepath):
        raise FileNotFoundError("pnml file not found at :: "+filepath)
    xml_tree = parse(filepath)
    pnml = xml_tree.getroot()
    net = pnml.find("net")
    net_name = net.find("name").find("text").text
    pages = net.findall("page")
    tgt_page = pages[0]
    ## we only parse the first page.
    places = {}
    place_ids = {}
    transitions = {}
    transition_ids = {}
    arcs = set()
    ### parse the places 
    for place in tgt_page.findall("place"):
        tools = place.find("toolspecific")
        lid = None
        if tools != None:
            if "localNodeID" in tools.attrib:
                lid = tools.attrib["localNodeID"]
        id = place.attrib["id"]
        # making a place
        pid = lid if lid != None and use_localnode_id else id
        place_ids[id] = pid
        parsed = Place( place.find("name").find("text").text, pid)
        places[pid] = parsed
        # handle markings
        init = place.find("initialMarking")
        final = place.find("finalMarking")
        if init != None:
            initial_marking[places[pid]] = int(init.find("text").text)
        if final != None:
            final_marking[places[pid]] = int(final.find("text").text)
    ### parse the transitions
    for transition in tgt_page.findall("transition"):
        tools = transition.find("toolspecific")
        lid = None
        if tools != None:
            if "localNodeID" in tools.attrib:
                lid = tools.attrib["localNodeID"]
        id = transition.attrib["id"]
        # check for silence 
        if "invisible"  in transition.attrib.keys():
            silent = transition.attrib["invisible"] == "true"
        else:
            silent = False
        # making a transition
        tid = lid if lid != None and use_localnode_id else id 
        transition_ids[id] = tid 
        parsed = Transition( 
            transition.find("name").find("text").text,
            tid,
            1,
            silent
        )
        transitions[tid] = parsed
    ### parse the arcs    
    nodes = deepcopy(places)
    nodes.update(transitions)
    node_ids = place_ids
    node_ids.update(transition_ids)
    for arc in tgt_page.findall("arc"):
        tools = arc.find("toolspecific")
        lid = None
        if tools != None:
            if "localNodeID" in tools.attrib:
                lid = tools.attrib["localNodeID"]
        id = arc.attrib["id"]
        src = node_ids[arc.attrib["source"]]
        tgt = node_ids[arc.attrib["target"]]
        # making an arc 
        aid = lid if lid != None and use_localnode_id else id  # we aren't storing the actual id??
        src_node = nodes[src]
        tgt_node = nodes[tgt]
        arcs.add(Arc(
            src_node, tgt_node
        ))
    # finalise compontents
    net = LabelledPetriNet(
        places=set(list(places.values())),
        transitions=set(list(transitions.values())),
        arcs=set(list(arcs)),
        name=net_name
    )
    if (len(initial_marking.keys()) > 0) and (len(final_marking.keys()) > 0):
        net = AcceptingPetriNet(
            net,
            PetriNetMarking(initial_marking), 
            [PetriNetMarking(final_marking)]
        )
    return net

def parse_pnml_for_dpn(filepath:str) -> PetriNetWithData:
    """
    Constructs a Petri net with data from the given filepath to a pnml file.
    """
    # setup compontents
    initial_marking = {}
    final_marking = {}
    # begin parsing
    ## check that file exists
    if not path.exists(filepath):
        raise FileNotFoundError("pnml file not found at :: "+filepath)
    xml_tree = parse(filepath)
    pnml = xml_tree.getroot()
    net = pnml.find("net")
    net_name = net.find("name").find("text").text
    pages = net.findall("page")
    tgt_page = pages[0]
    ## we only parse the first page.
    places = {}
    place_ids = {}
    transitions = {}
    transition_ids = {}
    arcs = set()
    ### parse the places 
    for place in tgt_page.findall("place"):
        tools = place.find("toolspecific")
        lid = None
        if tools != None:
            if "localNodeID" in tools.attrib:
                lid = tools.attrib["localNodeID"]
        id = place.attrib["id"]
        # making a place
        pid = lid if lid != None else id
        place_ids[id] = pid
        parsed = Place( place.find("name").find("text").text, pid)
        places[pid] = parsed
        # handle markings
        init = place.find("initialMarking")
        final = place.find("finalMarking")
        if init != None:
            initial_marking[places[pid]] = int(init.find("text").text)
        if final != None:
            final_marking[places[pid]] = int(final.find("text").text)
    ### parse the transitions
    for transition in tgt_page.findall("transition"):
        tools = transition.find("toolspecific")
        lid = None
        if tools != None:
            if "localNodeID" in tools.attrib:
                lid = tools.attrib["localNodeID"]
        id = transition.attrib["id"]
        # add guards if they exist
        if "guard" in transition.attrib:
            guard = Guard(Expression(transition.attrib['guard']))
        else: 
            guard = Guard(Expression("true"))
        # check for silence 
        if "invisible"  in transition.attrib.keys():
            silent = transition.attrib["invisible"] == "true"
        else:
            silent = False
        # making a transition
        tid = lid if lid != None else id 
        transition_ids[id] = tid 
        parsed = GuardedTransition( 
            transition.find("name").find("text").text,
            guard,
            tid,
            silent
        )
        transitions[tid] = parsed
    ### parse the arcs    
    nodes = deepcopy(places)
    nodes.update(transitions)
    node_ids = place_ids
    node_ids.update(transition_ids)
    for arc in tgt_page.findall("arc"):
        tools = arc.find("toolspecific")
        lid = None
        if tools != None:
            if "localNodeID" in tools.attrib:
                lid = tools.attrib["localNodeID"]
        id = arc.attrib["id"]
        src = node_ids[arc.attrib["source"]]
        tgt = node_ids[arc.attrib["target"]]
        # making an arc 
        aid = lid if lid != None else id  # we aren't storing the actual id??
        src_node = nodes[src]
        tgt_node = nodes[tgt]
        arcs.add(Arc(
            src_node, tgt_node
        ))
    # finalise compontents
    dpn = PetriNetWithData(
        places=set(list(places.values())),
        transitions=set(list(transitions.values())),
        arcs=set(list(arcs)),
        name=net_name
    )
    if (len(initial_marking.keys()) > 0) and (len(final_marking.keys()) > 0):
        dpn = AcceptingDataPetriNet(
                dpn,
                PetriNetMarking(initial_marking), 
                [PetriNetMarking(final_marking)]
            )
    return dpn