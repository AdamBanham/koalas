"""
This module provides functions to read in an XES formatted event log in various forms.
"""

from dataclasses import dataclass
from enum import Enum
from os import path

from datetime import datetime

from xml.etree.ElementTree import parse

from koalas.simple import EventLog, Trace
from koalas.xes import XES_CONCEPT,XES_TIME,XES_XML_NAMESPACE


class XesType(Enum):
    STRING = "string"
    DATE = "date"
    INT = "int"
    UNKNOWN = "NaN"


def find_xes_type(tag:str) -> XesType:
    if XesType.STRING.value in tag:
        return XesType.STRING
    elif XesType.DATE.value in tag:
        return XesType.DATE
    elif XesType.INT.value in tag: 
        return XesType.INT

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
            return datetime.strptime(self.value, "%Y-%m-%dT%H:%M:%S.%f%z")
        elif self.type == XesType.INT:
            return int(self.value.__str__())

        return self.value.__str__()

@dataclass
class EventExtract:
    event_order:int 
    label:XesAttribute 
    sorter:XesAttribute

    def get_label(self) -> str:
        return self.label.get()

    def get_sorter(self) -> object:
        return self.sorter.get()

    def __str__(self) -> str:
        return f"{self.event_order}-{self.get_label()}-{self.get_sorter()}"


def read_xes_simple(filepath:str, sort_attribute:str=XES_TIME,
                    label_attribute=XES_CONCEPT, debug:bool=True) -> EventLog:
    """
    Reads an XES formatted event log and creates a simplified event log object.\n
    Traces from the event log are sorted by the sort_attribute (time:timestamp 
    by default) before making the sequence of labels (concept:name by default).  
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
        if debug:
            print(f"extracted event log name :: {name}")

    traces = [ trace for trace in log.findall("xes:trace", XES_XML_NAMESPACE)]

    if debug:
        print(f"parsing {len(traces)} traces ...")
    # extract the following from a trace,
    # a sequence of activity labels
    # sort traces by time:timestamp before 
    extracted_traces = []
    for trace in traces:
        trace_ins = [] # eache element is a EventExtract
        events = [ event for event in trace.findall("xes:event", 
                        XES_XML_NAMESPACE)]
        for id,event in enumerate(events):
            label = None 
            sorter = None 
            for child in event.iter():
                key = child.attrib.get('key')
                # print(key)
                if (key == label_attribute):
                    label = XesAttribute(find_xes_type(child.tag), 
                                        key, child.attrib.get("value"))
                if (key == sort_attribute):
                    sorter = XesAttribute(find_xes_type(child.tag), 
                                        key, child.attrib.get("value"))
            extract = EventExtract(id, label , sorter)
            trace_ins.append(extract)
        sorted_traces = sorted(trace_ins, key=lambda t: t.get_sorter())
        trace = Trace([ t.get_label() for t in sorted_traces ])
        extracted_traces.append(trace) 
    return EventLog(extracted_traces, name)

