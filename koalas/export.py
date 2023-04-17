"""
This module provides functions to export out languages and different types 
of event logs constructs to the XES format.
"""
from koalas import __version__

from koalas.simple import EventLog
from koalas.complex import ComplexEventLog
from koalas._logging import debug,info, enable_logging, get_logger

from koalas.xes_export import XesLogExtension, XesLogClassifier
from koalas.xes_export import XES_LOG_TAG,XES_LOG_ATTRS
from koalas.xes_export import XES_EXT_CONCEPT_NAME,XES_EXT_CONCEPT_PREFIX 
from koalas.xes_export import XES_EXT_CONCEPT_URI

from koalas.xes_export import XesString, XesInt, XesTime, XesFloat, XesBoolean
from koalas.xes_export import XES_CONCEPT

from koalas.xes_export import XesTrace,XesEvent

import os 
import logging
from typing import Union
from datetime import datetime

from xml.etree import ElementTree as ET

EXPORT_SIMPLE_TRACE_FORMAT = "trace {id:d}"

@enable_logging
def export_to_xes_simple(filepath:str, log:EventLog) -> None:
    """
    This exports a simple event log structure out into an XES format but 
    consider the following before using:
    - A simple event log does not consider time, so no time:timstamp 
       element will be produced.
    - Thus, the only attribute exported for events will be concept:name.
    - Traces will have a concept:name, and will be given a dummy 
       concept:name based on seen order from log.
    - For each trace variant, we add x number of traces, based on how many 
       times a variant is seen.
    - Eventlogs will have concept:name, using the name from the event log.
    - We do not assume that the filepath exists, and will create the parent 
      directory path if does not exist.
    """

    info(f"exporting log of size :: {len(log)}")

    # check filepath
    if (not os.path.exists(os.path.dirname(filepath))):
        os.makedirs(os.path.dirname(filepath),exist_ok=True)

        info(f"made directory for :: {filepath}")

    with open(filepath,"wb") as flog:
        # add log element
        xml_log = ET.Element( XES_LOG_TAG, XES_LOG_ATTRS)
        # make xml docuement
        xml_tree = ET.ElementTree(xml_log)
        # (1) add default extension for concept:name
        xml_log.append(XesLogExtension(XES_EXT_CONCEPT_NAME,
            XES_EXT_CONCEPT_PREFIX,
            XES_EXT_CONCEPT_URI)
        )
        # (2) add any globals
        # (3) add any classifiers
        xml_log.append(XesLogClassifier("activity-classifier",
         [XES_CONCEPT]))
        # (4) add any properties 
        # add concept:name to log
        xml_log.append(XesString(XES_CONCEPT, log.get_name()))
        # add meta_exporter to log as koalas
        xml_log.append(XesString("meta:exporter", "koalas"))
        xml_log.append(XesString("meta:exporter:version", 
         f"{__version__}"))
        # add traces
        trace_id = 1
        debug("starting trace conversion")
        for trace,count in log.__iter__():
            events = []
            # add a trace, count times
            for _ in range(count):
                # generate parent trace
                xml_trace = XesTrace(EXPORT_SIMPLE_TRACE_FORMAT.format(
                  id=trace_id))

                # only generate events once
                if (len(events) != len(trace)):
                  debug(f"Generating events for variant ::"+
                   f"{trace} x {count}")
                  # generate subelements
                  for act in trace.__iter__():
                      ev = XesEvent()
                      # add concept for event
                      ev.append(XesString(XES_CONCEPT, act))
                      # keep event
                      events.append(ev)  

                  if (get_logger().isEnabledFor(logging.DEBUG)):
                    debug(f"Generated sequence of events :: "+
                     f"{[ ET.tostring(e) for e in events ]}")

                # add events as subelements
                for ev in events:
                    xml_trace.append(ev) 

                # after adding all events to trace, add element to log
                xml_log.append(xml_trace)

                trace_id += 1
        debug(f"exported traces :: {trace_id-1}")
        # write out xml to file
        ET.indent(xml_tree, space="\t", level=0)
        xml_tree.write(flog, encoding="utf-8", method="xml",
         xml_declaration=True)
    
    info(f"exported log to :: {filepath}")

def create_xes_attribute(key:str, value:object) -> Union[XesString, XesInt, XesTime]:
    if isinstance(value, float):
       return XesFloat(key, value) 
    elif isinstance(value, bool):
       return XesBoolean(key, value)
    elif isinstance(value, int):
      return XesInt(key, value)
    elif isinstance(value, datetime):
      return XesTime(key, value)
    else:
      return XesString(key, value)


@enable_logging
def export_to_xes_complex(filepath:str, log:ComplexEventLog) -> None:
    """
    This exports a complex event log structure out into an XES format but 
    consider the following before using:
    - Traces will have a concept:name, and will be given a dummy 
       concept:name based on seen order from log if not presented.
    - Any data associated with an event, trace or event log will be added as 
      attributes at the associated level.
    - For each trace variant, we add all instances of that variant in seen order
    - Eventlogs will have concept:name, using the name from the event log.
    - We do not assume that the filepath exists, and will create the parent 
      directory path if does not exist.
    """

    if (isinstance(log, EventLog)):
        info("Changing to simple version as given log was simple")
        export_to_xes_simple(filepath, log)
        return 
    elif (not isinstance(log, ComplexEventLog)):
        raise ValueError(f"Was expecting a complex event log, but was given :: {type(log)}")

    info(f"exporting log of size :: {len(log)}")

    # check filepath
    if (not os.path.exists(os.path.dirname(filepath))):
        os.makedirs(os.path.dirname(filepath),exist_ok=True)

        info(f"made directory for :: {filepath}")

    with open(filepath,"wb") as flog:
        # add log element
        xml_log = ET.Element( XES_LOG_TAG, XES_LOG_ATTRS)
        # make xml docuement
        xml_tree = ET.ElementTree(xml_log)
        # (1) add default extension for concept:name
        xml_log.append(XesLogExtension(XES_EXT_CONCEPT_NAME,
            XES_EXT_CONCEPT_PREFIX,
            XES_EXT_CONCEPT_URI)
        )
        # (2) add any globals
        # (3) add any classifiers
        xml_log.append(XesLogClassifier("activity-classifier",
         [XES_CONCEPT]))
        # (4) add any properties 
        # add concept:name to log
        xml_log.append(XesString(XES_CONCEPT, log.get_name()))
        # add elements from data
        if (log.data() != None):
           for key,val in log.data().items():
              xml_log.append(create_xes_attribute(key,val))
        # add meta_exporter to log as koalas
        xml_log.append(XesString("meta:exporter", "koalas"))
        xml_log.append(XesString("meta:exporter:version", 
         f"{__version__}"))
        # add traces
        trace_id = 1
        debug("starting trace conversion")
        for _,complexes in log.get_instances().items():
            for trace in complexes:
              events = []
              # generate complex trace
              xml_trace = None
              if ( XES_CONCEPT in trace.data().keys()):
                name = trace.data()[XES_CONCEPT]
              else:
                name = EXPORT_SIMPLE_TRACE_FORMAT.format(
                  id=trace_id)
              xml_trace = XesTrace(name)
              # generate events
              debug(f"Generating events for variant ::"+
              f"{trace}")
              # generate subelements
              for cev in trace:
                  xml_ev = XesEvent()
                  # add concept for event
                  xml_ev.append(XesString(XES_CONCEPT, cev.activity()))
                  # add other attributes to event
                  for key,val in cev.data().items():
                     if key == XES_CONCEPT:
                        continue
                     else:
                        xml_ev.append(create_xes_attribute(key,val))
                  # keep event
                  events.append(xml_ev)  

              if (get_logger().isEnabledFor(logging.DEBUG)):
                debug(f"Generated sequence of events :: "+
                f"{[ ET.tostring(e) for e in events ]}")

              # add attributes to trace
              for key,val in trace.data().items():
                 if key == XES_CONCEPT:
                    continue
                 else:
                    xml_trace.append(create_xes_attribute(key,val))

              # add events as subelements
              for xml_ev in events:
                  xml_trace.append(xml_ev) 

              # after adding all events to trace, add element to log
              xml_log.append(xml_trace)
              trace_id += 1

        debug(f"exported traces :: {trace_id-1}")
        # write out xml to file
        ET.indent(xml_tree, space="\t", level=0)
        xml_tree.write(flog, encoding="utf-8", method="xml",
         xml_declaration=True)
    
    info(f"exported log to :: {filepath}")