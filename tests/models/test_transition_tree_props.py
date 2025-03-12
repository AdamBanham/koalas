import unittest
from os import path,remove

from pmkoalas.simple import Trace
from pmkoalas.complex import ComplexEvent
from pmkoalas.read import read_xes_simple,read_xes_complex

from pmkoalas.models.guards import Guard, GuardOutcomes, Expression
from pmkoalas.conformance.tokenreplay import PlayoutTransitionGuard
from pmkoalas.models.transitiontree import TransitionTree
from pmkoalas.models.transitiontree import TransitionTreeVertex,TransitionTreeRoot
from pmkoalas.models.transitiontree import TransitionTreeGuardFlow,TransitionTreePopulationFlow
from pmkoalas.models.transitiontree import TransitionTreeGuard
from pmkoalas.models.transitiontree import Offer
from pmkoalas.models.transitiontree import construct_from_log

#TODO:: need to rework tests for the construction

class TraceTest(unittest.TestCase):

    def test_init_fail(self):
        # fail cases
        with self.assertRaises(ValueError):
            tree = TransitionTree(None, None)
        with self.assertRaises(ValueError):
            tree = TransitionTree(set(), None,)
        with self.assertRaises(ValueError):
            tree = TransitionTree(list(), 5,)
        with self.assertRaises(ValueError):
            tree = TransitionTree(None, set())


