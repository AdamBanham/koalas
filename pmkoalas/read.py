"""
This module provides functions to read in an XES formatted event log in various forms.
"""

from dataclasses import dataclass
from enum import Enum
from os import path
from datetime import datetime
from typing import List, Mapping
from copy import deepcopy

from xml.etree.ElementTree import Element, parse

from pmkoalas.simple import EventLog, Trace
from pmkoalas.complex import ComplexEvent, ComplexTrace, ComplexEventLog
from pmkoalas._logging import debug, info, enable_logging
from pmkoalas.xes import XES_CONCEPT,XES_TIME,XES_XML_NAMESPACE

from pmkoalas.xes_export import XES_STRING_TAG, XES_TIME_TAG , XES_INT_TAG
from pmkoalas.xes_export import XES_FLOAT_TAG, XES_BOOLEAN_TAG

class XesType(Enum):
    STRING = XES_STRING_TAG
    DATE = XES_TIME_TAG
    INT = XES_INT_TAG
    FLOAT = XES_FLOAT_TAG
    BOOLEAN = XES_BOOLEAN_TAG
    UNKNOWN = "NaN"


def find_xes_type(tag:str) -> XesType:
    if XesType.STRING.value in tag:
        return XesType.STRING
    elif XesType.DATE.value in tag:
        return XesType.DATE
    elif XesType.INT.value in tag: 
        return XesType.INT
    elif XesType.FLOAT.value in tag:
        return XesType.FLOAT
    elif XesType.BOOLEAN.value in tag:
        return XesType.BOOLEAN

    return XesType.UNKNOWN

@dataclass
class XesAttribute:
    type:XesType 
    key:str
    value:str

    def get(self) -> object:
        if self.type == XesType.STRING:
            return self.value.__str__()
        elif self.type == XesType.DATE:
            return datetime.fromisoformat(self.value)
        elif self.type == XesType.INT:
            return int(self.value.__str__())
        elif self.type == XesType.FLOAT:
            pass_one = float(self.value.__str__())
            pass_two = f"{pass_one:.8f}"
            return float(pass_two)
        elif self.type == XesType.BOOLEAN:
            val = str(self.value).lower()
            if (val == 'true' or val == '1'):
                return True
            elif (val == 'false' or val == '0'):
                return False
        return self.value.__str__()

@dataclass
class EventExtract:
    event_order:int 
    label:XesAttribute 
    sorter:XesAttribute
    map:Mapping[str,XesAttribute] = None

    def get_label(self) -> str:
        return self.label.get()
    
    def get_data(self) -> Mapping[str,XesAttribute]:
        if self.map == None:
            return dict()
        else:
            return deepcopy(self.map)

    def get_sorter(self) -> object:
        return self.sorter.get()

    def __str__(self) -> str:
        return f"{self.event_order}-{self.get_label()}-{self.get_sorter()}"
    
def find_element(root:Element, find:str, use_namespace:bool) -> List[Element]:
    if (use_namespace):
        return [ event for event in root.findall(f"xes:{find}", 
                        XES_XML_NAMESPACE)]
    else: 
        return [ event for event in root.findall(f"{find}")]

@enable_logging
def read_xes_complex(filepath:str,
                    label_attribute=XES_CONCEPT) -> ComplexEventLog:
    """
    Reads an XES formatted event log and creates a complex event log
    object. 

    Parameters
    ----------
    filepath: `str`
    \t the filepath to the xes file to read.
    label_attribute: `str`=`concept:name`
    \t the xes attribute for the process label for an event
    """ 

    # check that file exists
    if not path.exists(filepath):
        raise FileNotFoundError("event log file not found at :: "+filepath)
    
    # parse traces
    xml_tree = parse(filepath)
    log = xml_tree.getroot()

    if (log == None):
        raise ValueError("Unable to find log element in xml structure")
    
    # find name of log
    log_attrs = log.find(".*[@key='concept:name']")

    name = "Unknown Event log"
    if log_attrs != None:
        name = log_attrs.attrib.get("value")
        debug(f"extracted event log name :: {name}")

    # check with namespace
    ns_traces = [ trace for trace in log.findall("xes:trace",
     XES_XML_NAMESPACE)]
    #  check without namespace
    nns_traces = [ trace for trace in log.findall("trace",
     XES_XML_NAMESPACE)]
    #  decide what to do with namespace
    use_namespace = True
    if (len(ns_traces) == nns_traces):
        traces = ns_traces 
        del nns_traces
    elif (len(ns_traces) < len(nns_traces)):
        traces = nns_traces
        use_namespace = False
        del ns_traces 
    else: 
        traces = ns_traces
        del ns_traces

    info(f"parsing {len(traces)} traces ...")
    # extract the following from a trace,
    # a sequence of activity labels
    # sort traces by time:timestamp before 
    extracted_traces = []
    for trace in traces:
        trace_ins = [] # each element is a EventExtract
        events = find_element(trace, "event", use_namespace)
        for id,event in enumerate(events):
            label = None 
            map = dict()
            for child in event.iter():
                key = child.attrib.get('key')
                if (key == label_attribute):
                    label = XesAttribute(find_xes_type(child.tag), 
                                        key, child.attrib.get("value"))
                else:
                    if (key == None):
                        continue
                    map[key] = XesAttribute(
                        find_xes_type(child.tag),
                        key, 
                        child.attrib.get("value")                        
                    ).get()
            extract = EventExtract(id, label , sorter=None, map=map)
            trace_ins.append(extract)
        # handle complex event construction
        # collect any trace level attributes
        trace_map = dict()
        for child in trace:
            key = child.attrib.get('key')
            if (key == None):
                continue
            trace_map[key] = XesAttribute(
                        find_xes_type(child.tag),
                        key, 
                        child.attrib.get("value")                        
                    ).get()
        # build complex events and trace
        trace_ins = ComplexTrace(
            [ ComplexEvent(t.get_label(),t.get_data()) for t in trace_ins ],
             data=trace_map)
        # store complex trace
        extracted_traces.append(trace_ins) 
    # build log-level attributes
    log_map = dict()
    for child in log:
        key = child.attrib.get('key')
        if (key == None):
            continue
        log_map[key] = XesAttribute(
                    find_xes_type(child.tag),
                    key, 
                    child.attrib.get("value")                        
                ).get()
    return ComplexEventLog(extracted_traces, name=name, data=log_map)

@enable_logging
def read_xes_simple(filepath:str, label_attribute:List[str]=[XES_CONCEPT]) -> EventLog:
    """
    Reads an XES formatted event log and creates a simplified event log 
    object. Traces from the event log are kept in document order before 
    making the sequence of labels (concept:name by default).

    Parameters
    ----------
    filepath: `str`
    \t the filepath to the xes file to read.
    label_attribute: `List[str]`=`[concept:name]`
    \t the xes attribute for the process label for an event
    """
    # backwards compatibility for label
    if (type(label_attribute) == str):
        label_attribute = [label_attribute]

    # check that file exists
    if not path.exists(filepath):
        raise FileNotFoundError("event log file not found at :: "+filepath)

    # parse traces
    xml_tree = parse(filepath)
    log = xml_tree.getroot()

    if (log == None):
        raise ValueError("Unable to find log element in xml structure")

    # find name of log
    log_attrs = log.find(".*[@key='concept:name']")

    name = "Unknown Event log"
    if log_attrs != None:
        name = log_attrs.attrib.get("value")
        debug(f"extracted event log name :: {name}")

    # check with namespace
    ns_traces = [ trace for trace in log.findall("xes:trace",
     XES_XML_NAMESPACE)]
    #  check without namespace
    nns_traces = [ trace for trace in log.findall("trace",
     XES_XML_NAMESPACE)]
    #  decide what to do with namespace
    use_namespace = True
    if (len(ns_traces) == nns_traces):
        traces = ns_traces 
        del nns_traces
    elif (len(ns_traces) < len(nns_traces)):
        traces = nns_traces
        use_namespace = False
        del ns_traces 
    else: 
        traces = ns_traces
        del ns_traces

    info(f"parsing {len(traces)} traces ...")
    # extract the following from a trace,
    # a sequence of activity labels
    # sort traces by time:timestamp before 
    extracted_traces = []
    for trace in traces:
        trace_ins = [] # eache element is a EventExtract
        events = find_element(trace, "event", use_namespace)
        for id,event in enumerate(events):
            label = None
            sorter = None 
            for child in event.iter():
                key = child.attrib.get('key')
                # print(key)
                if (key in label_attribute):
                    if (label == None):
                        label = child.attrib.get("value")
                    else:
                        label = " ".join([label, child.attrib.get("value")])
            if label == None:
                raise ValueError(
                    f"unable to find label attribute on :: {event}"
                )
            label = XesAttribute(XES_STRING_TAG, 
                                 "concept:name", label)
            extract = EventExtract(id, label , sorter)
            trace_ins.append(extract)
        trace_ins = Trace([ t.get_label() for t in trace_ins ])
        extracted_traces.append(trace_ins) 
    return EventLog(extracted_traces, name)

