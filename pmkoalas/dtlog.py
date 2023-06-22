"""
Parses delimited traces into koalas EventLog objects.
"""
from typing import Iterable
from pmkoalas.simple import EventLog, Trace


DEFAULT_DELIM=" "

def convertTrace(trace: str, delimiter=DEFAULT_DELIM) -> Iterable[str]:
    if (len(trace) < 1):
        return Trace(list())
    return Trace(trace.split(delimiter))

def convert(*traces: Iterable[str], delimiter=DEFAULT_DELIM) -> EventLog:
    """
    This function converts a sequence of `"a b c"` into traces,
    and then creates an event log. Examplar uses are the following:
    \n
    `convert("a b c", "a b", "a")`\n
    `convert(*[ t for t in traces])`\n
    """
    conv = lambda x: convertTrace(x, delimiter=delimiter)
    return EventLog( map( conv, traces ) )


