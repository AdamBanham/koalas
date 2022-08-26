from typing import Iterable
from koalas.simple import Trace,EventLog

from string import ascii_uppercase as language
from random import choice, randint

# random functions for debugging behaviour and properties

def make_random_trace(length:int) -> Trace:
    """
    Makes a random trace consisting of asciiletters, for a given length
    """
    sequence = list()
    while length > 0:
        sequence.append(choice(language))
        length -= 1
    return Trace(sequence)

def make_random_event_log(traces:int, max_trace_length:int) -> EventLog:
    """
    Makes a random event log of random traces, where traces are not longer than max_trace_length and consists of one event.
    """ 
    trace_list = list()

    while traces > 0:
        trace_list.append(make_random_trace(randint(1,max_trace_length)))
        traces -= 1

    return EventLog(trace_list, "random_log")

# known languages for event logs

def make_decision_point_log(traces:int) -> EventLog:
    """
    Makes a event log of a known language with the following properties:
       - c is twice as likely as d 
       - f is three times as likely as g

    Language consits of: \n
    ______ /-> c ______ /-> f \n
    a -> b ______ -> e _______ -> h \n
    ______ \\\\-> d ______ \\\\-> g \n
    """

    trace_list = [ None for _ in range(traces)]

    while traces > 0:
        sequence = list()
        sequence.append("A")
        sequence.append("B")
        if (randint(1,3) < 2):
            sequence.append("D")
        else: 
            sequence.append("C")
        sequence.append("E")
        if (randint(1,4) < 2):
            sequence.append("G")
        else:
            sequence.append("F")
        sequence.append("H")
        traces -= 1
        trace_list[traces] = (Trace(sequence))

    return EventLog(trace_list, "decision_language_one")
