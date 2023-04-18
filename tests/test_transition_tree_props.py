import unittest

from koalas.simple import Trace
from koalas.complex import ComplexEvent

from koalas.models.transitiontree import TransitionTree
from koalas.models.transitiontree import TransitionTreeVertex,TransitionTreeRoot
from koalas.models.transitiontree import TransitionTreeGuardFlow,TransitionTreePopulationFlow
from koalas.models.transitiontree import TransitionTreeGuard

class TraceTest(unittest.TestCase):

    def test_init_fail(self):
        # fail cases
        with self.assertRaises(ValueError):
            tree = TransitionTree(None, None, None)
        with self.assertRaises(ValueError):
            tree = TransitionTree(set(), None, None)
        with self.assertRaises(ValueError):
            tree = TransitionTree(list(), 5, None)
        with self.assertRaises(ValueError):
            tree = TransitionTree(None, set(), 5)
        with self.assertRaises(ValueError):
            tree = TransitionTree(None, None, set())

    def test_init_true(self):
        # good cases
        try:
            # simple case, just a root vertex
            tree = TransitionTree(set(), TransitionTreeRoot(), set())
            # non-trivial case, log side
            vertices = [
                TransitionTreeRoot(),
                TransitionTreeVertex(2, Trace(['a']), True),
                TransitionTreeVertex(3, Trace(['b']), True)
            ]
            root = vertices[0]
            flows = set([
                TransitionTreePopulationFlow(
                    root, 'a', vertices[1], [ ComplexEvent('root', {'a' : 5}) ]
                ),
                TransitionTreePopulationFlow(
                    root, 'b', vertices[1], [ ComplexEvent('root', {'c' : 5.12}) ]
                )
            ])
            vertices = set(vertices)
            tree = TransitionTree(vertices, root, flows)
            # non-trivial case, model side
            vertices = [
                TransitionTreeRoot(),
                TransitionTreeVertex(2, Trace(['a']), True),
                TransitionTreeVertex(3, Trace(['b']), True)
            ]
            root = vertices[0]
            flows = set([
                TransitionTreeGuardFlow(
                    root, 'a', vertices[1], TransitionTreeGuard()
                ),
                TransitionTreeGuardFlow(
                    root, 'b', vertices[1], TransitionTreeGuard()
                )
            ])
            vertices = set(vertices)
            tree = TransitionTree(vertices, root, flows)

        except Exception as e:
            self.fail(f"Expection raise during ideal construction of tree :: {e}")

        
