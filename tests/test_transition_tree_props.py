import unittest

from koalas.simple import Trace
from koalas.complex import ComplexEvent

from koalas.models.transitiontree import TransitionTree
from koalas.models.transitiontree import TransitionTreeVertex,TransitionTreeRoot
from koalas.models.transitiontree import TransitionTreeGuardFlow,TransitionTreePopulationFlow
from koalas.models.transitiontree import TransitionTreeGuard

# dummy transition tree
D1_ROOT = TransitionTreeRoot()
D1_VERTS = [
    D1_ROOT,
    TransitionTreeVertex(2, Trace(['a'])),
    TransitionTreeVertex(3, Trace(['b'])),
    TransitionTreeVertex(4, Trace(['a','c'])),
    TransitionTreeVertex(5, Trace(['b','c'])),
    TransitionTreeVertex(6, Trace(['a','c','d']), True),
    TransitionTreeVertex(7, Trace(['a','c','e']), True),
    TransitionTreeVertex(8, Trace(['b','c','d']), True),
    TransitionTreeVertex(9, Trace(['b','c','e']), True),
]
D1_FLOWS = set([
    TransitionTreePopulationFlow(D1_ROOT, 'a', D1_VERTS[1], 
        [ ComplexEvent('a', {}), ComplexEvent('a', {})]                             
    ),
    TransitionTreePopulationFlow(D1_ROOT, 'b', D1_VERTS[2], 
        [ ComplexEvent('b', {}), ComplexEvent('b', {})]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[1], 'c', D1_VERTS[3], 
        [ ComplexEvent('c', {'a1' : 5}), 
          ComplexEvent('c', {'a1' : 7}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[2], 'c', D1_VERTS[4], 
        [ ComplexEvent('c', {'a1' : 2, 'a2' : 0.3}), 
          ComplexEvent('c', {'a1' : 3, 'a2' : 0.25}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[3], 'd', D1_VERTS[5], 
        [ ComplexEvent('d', {'a1' : 5, 'a3' : 'high'}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[3], 'e', D1_VERTS[6], 
        [ ComplexEvent('e', {'a1' : 7, 'a3' : 'mid'}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[4], 'd', D1_VERTS[7], 
        [ ComplexEvent('c', {'a1' : 2, 'a2' : 0.3}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[4], 'e', D1_VERTS[8], 
        [ ComplexEvent('c', {'a1': 3, 'a2': 0.25}) ]                             
    ),
])
D1_VERTS = set(D1_VERTS)
D1_TREE = TransitionTree(D1_VERTS, D1_ROOT, D1_FLOWS)

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
            self.fail(f"Expection raised during ideal construction of tree :: {e}")

    def test_validate_basic_props(self):
        # test vertices
        tree = D1_TREE 
        self.assertEqual(tree.vertices(), D1_VERTS)
        # test root
        self.assertEqual(tree.root(), D1_ROOT)
        # test flows
        self.assertEqual(tree.flows(), D1_FLOWS)
        # test strict vertices
        #TODO 
        # test offers
        #TODO
        # test choices
        #TODO

    def test_validate_attributes(self):
        # TODO
        pass 

    def test_populations(self):
        # TODO
        pass 

    def test_guards(self):
        # TODO 
        pass 


