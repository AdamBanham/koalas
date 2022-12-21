"""
This module includes functions to quickly generate koalas 
event logs, traces, and events in both simple and complex forms.

Simple Form Objects
-------------------
gen_log\n
gen_trace\n

Complex Form Objects
--------------------
Coming soon...
"""
from typing import Iterable
from koalas.simple import EventLog, Trace


DEFAULT_DELIM=" "

def gen_trace(trace: str, delimiter=DEFAULT_DELIM) -> Iterable[str]:
    """
    This function generates a (simple) Trace from a delimited trace,
    e.g. "a b c".
    """
    if (len(trace) < 1):
        return Trace(list())
    return Trace(trace.split(delimiter))

def gen_log(*traces: Iterable[str], delimiter=DEFAULT_DELIM) -> EventLog:
    """
    This function generates an (simple) event log from a collection
    of delimited traces, e.g. ["a b", "a c", "a b d"]. Exemplar 
    uses consist of:\n
    `convert("a b c", "a b", "a")`\n
    `convert(*[ t for t in traces])`\n
    """
    return EventLog( map( gen_trace, traces ) )


