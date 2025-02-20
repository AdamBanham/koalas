"""
This module contains the abstraction layer that reads an arbitrary pnml file.
"""
from pmkoalas.models.petrinets.pn import LabelledPetriNet, Place
from pmkoalas.models.petrinets.pn import Transition, Arc
from pmkoalas.models.petrinets.pn import AcceptingPetriNet, PetriNetMarking
from pmkoalas.models.petrinets.dpn import PetriNetWithData, GuardedTransition
from pmkoalas.models.petrinets.dpn import AcceptingDataPetriNet
from pmkoalas.models.petrinets.wpn import WeightedPetriNet
from pmkoalas.models.petrinets.wpn import WeightedAcceptingPetriNet
from pmkoalas.models.petrinets.wpn import WeightedTransition
from pmkoalas.models.petrinets.guards import Guard,Expression

from os import path
from copy import deepcopy
from typing import Union
from xml.etree.ElementTree import parse

def parse_pnml_into_lpn(filepath:str,
        use_localnode_id:bool=False) -> Union[LabelledPetriNet,AcceptingPetriNet]:
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
        tools = place.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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
        tools = transition.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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
            silent
        )
        transitions[tid] = parsed
    ### parse the arcs    
    nodes = deepcopy(places)
    nodes.update(transitions)
    node_ids = place_ids
    node_ids.update(transition_ids)
    for arc in tgt_page.findall("arc"):
        tools = arc.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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

def parse_pnml_into_wpn(filepath:str,
                        use_localnode_id:bool=False
    ) -> Union[WeightedPetriNet,WeightedAcceptingPetriNet]:
    """
    Constructs a weighted Petri net from the given filepath to a pnml file.
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
        tools = place.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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
        tools = transition.findall("toolspecific")
        lid = None
        weight = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
            if tool.attrib['tool'] == "StochasticPetriNet":
                if "weight" in tool.attrib:
                    weight = float(tool.attrib["weight"])
        id = transition.attrib["id"]
        # check for silence 
        if "invisible"  in transition.attrib.keys():
            silent = transition.attrib["invisible"] == "true"
        else:
            silent = False
        # making a transition
        tid = lid if lid != None and use_localnode_id else id 
        transition_ids[id] = tid 
        parsed = WeightedTransition( 
            transition.find("name").find("text").text,
            tid,
            silent,
            weight if weight != None else 1
        )
        transitions[tid] = parsed
    ### parse the arcs    
    nodes = deepcopy(places)
    nodes.update(transitions)
    node_ids = place_ids
    node_ids.update(transition_ids)
    for arc in tgt_page.findall("arc"):
        tools = arc.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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
    net = WeightedPetriNet(
        places=set(list(places.values())),
        transitions=set(list(transitions.values())),
        arcs=set(list(arcs)),
        name=net_name
    )
    if (len(initial_marking.keys()) > 0) and (len(final_marking.keys()) > 0):
        net = WeightedAcceptingPetriNet(
            net,
            PetriNetMarking(initial_marking), 
            [PetriNetMarking(final_marking)]
        )
    return net

def parse_pnml_for_dpn(filepath:str,
                       use_localnode_id:bool=False
    ) -> Union[PetriNetWithData, AcceptingDataPetriNet]:
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
        tools = place.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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
        tools = transition.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
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
        tid = lid if lid != None and use_localnode_id else id
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
        tools = arc.findall("toolspecific")
        lid = None
        for tool in tools:
            if tool.attrib['tool'] == "ProM":
                if "localNodeID" in tool.attrib:
                    lid = tool.attrib["localNodeID"]
        id = arc.attrib["id"]
        src = node_ids[arc.attrib["source"]]
        tgt = node_ids[arc.attrib["target"]]
        # making an arc 
        aid = lid if lid != None and use_localnode_id else id
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