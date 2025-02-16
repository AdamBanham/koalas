"""
This module includes some utility functions for Petri nets.
"""
from pmkoalas.models.petrinets.wpn import WeightedTransition

SILENT_TRANSITION_DEFAULT_NAME='tau'
def silent_transition(name=None,tid=None,weight=None):
    tn = SILENT_TRANSITION_DEFAULT_NAME
    if name:
        tn = name
    tw = 1
    ttid = None
    if tid:
        ttid = tid
    if weight:
        tw = weight
    return WeightedTransition(name=tn,weight=tw,tid=ttid,silent=True)

# Candidate to move to a utility package
def steq(self,other):
    if type(other) is type(self):
        return self.__dict__ == other.__dict__
    return False