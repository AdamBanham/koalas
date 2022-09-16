"""
This module provides functions to export out languages and different types of
event logs constructs to the XES format.
"""
from koalas.simple import EventLog

from koalas.xes_export import XesLogExtension
from koalas.xes_export import XES_LOG_TAG,XES_LOG_ATTRS
from koalas.xes_export import XES_EXT_CONCEPT_NAME,XES_EXT_CONCEPT_PREFIX, XES_EXT_CONCEPT_URI

from koalas.xes_export import XesString
from koalas.xes_export import XES_CONCEPT

from koalas.xes_export import XesTrace,XesEvent

import os 
from xml.etree import ElementTree as ET

EXPORT_SIMPLE_TRACE_FORMAT = "trace {id:d}"

def export_to_xes_simple(filepath:str, log:EventLog, debug:bool=True) -> None:
    """
    This exports a simple event log structure out into an XES format but consider
    the following before using:
    - A simple event log does not consider time, so no time:timstamp element will
      be produced.
    - Thus, the only attribute exported for events will be concept:name.
    - Traces will have a concept:name, and will be given a dummy concept:name 
      based on seen order from log.
    - For each trace variant, we add x number of traces, based on how many times
      a variant is seen.
    - Eventlogs will have concept:name, using the name from the event log.
    - We do not assume that the filepath exists, and will create the parent 
      directory path if does not exist.
    """

    # check filepath
    if (not os.path.exists(os.path.dirname(filepath))):
        os.makedirs(os.path.dirname(filepath),exist_ok=True)

        if(debug):
            print(f"made directory for :: {filepath}")

    with open(filepath,"wb") as flog:
        # add log element
        xml_log = ET.Element( XES_LOG_TAG, XES_LOG_ATTRS)
        # make xml docuement
        xml_tree = ET.ElementTree(xml_log)
        # add default extension for concept:name
        xml_log.append(XesLogExtension(XES_EXT_CONCEPT_NAME,
            XES_EXT_CONCEPT_PREFIX,
            XES_EXT_CONCEPT_URI)
        )
        # add concept:name to log
        xml_log.append(XesString(XES_CONCEPT, log.get_name()))

        # add traces
        trace_id = 1
        for trace,count in log.__iter__():
            events = []
            # add a trace, count times
            for _ in range(count):
                # generate parent trace
                xml_trace = XesTrace(EXPORT_SIMPLE_TRACE_FORMAT.format(id=trace_id))

                # only generate events once
                if (len(events) != len(trace)):
                    # generate subelements
                    for act in trace.__iter__():
                        ev = XesEvent()
                        # add concept for event
                        ev.append(XesString(XES_CONCEPT, act))
                        # keep event
                        events.append(ev)  

                # add events as subelements
                for ev in events:
                    xml_trace.append(ev) 

                # after adding all events to trace, add element to log
                xml_log.append(xml_trace)

                trace_id += 1

        # write out xml to file
        ET.indent(xml_tree, space="\t", level=0)
        xml_tree.write(flog, encoding="utf-8", method="xml", xml_declaration=True)
    
    if (debug):
        print(f"exported log to :: {filepath}")