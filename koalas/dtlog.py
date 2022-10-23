"""
Parses delimited traces into koalas EventLog objects.
"""
from typing import Iterable
from koalas.simple import EventLog, Trace


DEFAULT_DELIM=" "

def convertTrace(trace: str, delimiter=DEFAULT_DELIM) -> Iterable[str]:
    if (len(trace) < 1):
        return Trace(list())
    return Trace(trace.split(delimiter))

"""
Files are of the form
	 
LOG   :: TRACE {TRACE_DELIMITER TRACE}
TRACE :: EVENT {EVENT_DELIMITER EVENT}
EVENT :: <string label>
"""
def convert(*traces: Iterable[str], delimiter=DEFAULT_DELIM) -> EventLog:
    return EventLog( map( convertTrace, traces ) )


