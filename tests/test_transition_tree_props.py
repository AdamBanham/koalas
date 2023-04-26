import unittest
from os import path,remove

from pmkoalas.simple import Trace
from pmkoalas.complex import ComplexEvent
from pmkoalas.read import read_xes_simple,read_xes_complex

from pmkoalas.models.transitiontree import TransitionTree
from pmkoalas.models.transitiontree import TransitionTreeVertex,TransitionTreeRoot
from pmkoalas.models.transitiontree import TransitionTreeGuardFlow,TransitionTreePopulationFlow
from pmkoalas.models.transitiontree import TransitionTreeGuard, TranstionTreeEarlyComplete
from pmkoalas.models.transitiontree import Offer
from pmkoalas.models.transitiontree import construct_from_log

HALT_ACT = TranstionTreeEarlyComplete().activity()

# dummy transition tree
D1_ROOT = TransitionTreeRoot()
D1_VERTS = [
    D1_ROOT,
    TransitionTreeVertex(2, Trace(['a'])),
    TransitionTreeVertex(3, Trace(['b'])),
    TransitionTreeVertex(4, Trace(['a','c'])),
    TransitionTreeVertex(5, Trace(['b','c'])),
    TransitionTreeVertex(6, Trace(['a','c','d'])),
    TransitionTreeVertex(7, Trace(['a','c','e'])),
    TransitionTreeVertex(8, Trace(['b','c','d'])),
    TransitionTreeVertex(9, Trace(['b','c','e'])),
    TransitionTreeVertex(6, Trace(['a','c','d', HALT_ACT]), True),
    TransitionTreeVertex(7, Trace(['a','c','e', HALT_ACT]), True),
    TransitionTreeVertex(8, Trace(['b','c','d', HALT_ACT]), True),
    TransitionTreeVertex(9, Trace(['b','c','e', HALT_ACT]), True),
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

    TransitionTreePopulationFlow(D1_VERTS[5], HALT_ACT, D1_VERTS[9], 
        [ ComplexEvent('d', {}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[6], HALT_ACT, D1_VERTS[10], 
        [ ComplexEvent('e', {}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[7], HALT_ACT, D1_VERTS[11], 
        [ ComplexEvent('c', {}) ]                             
    ),
    TransitionTreePopulationFlow(D1_VERTS[8], HALT_ACT, D1_VERTS[12], 
        [ ComplexEvent('c', {}) ]                             
    ),
])
D1_STRICT = set([ D1_ROOT, D1_VERTS[3], D1_VERTS[4] ])
D1_VERTS = set(D1_VERTS)
D1_OFFERS = set([ 
    Offer(v.sigma_sequence(), set([ f.activity() for f in v.outgoing(D1_FLOWS)]))
    for v 
    in D1_VERTS
])
D1_CHOICES = set([ 
    Offer(v.sigma_sequence(), set([ f.activity() for f in v.outgoing(D1_FLOWS)]))
    for v 
    in D1_STRICT
])
D1_TREE = TransitionTree(D1_VERTS, D1_ROOT, D1_FLOWS)
D1_ATTRS = set([
    'a1', 'a2', 'a3'
])

SSMALL = path.join(".","tests","small_01.xes")
SSMALL_ROOT = TransitionTreeRoot()
SSMALL_VERTS = [
    SSMALL_ROOT,
    TransitionTreeVertex(2, Trace(['A'])),
    TransitionTreeVertex(3, Trace(['A','A'])),
    TransitionTreeVertex(4, Trace(['A','B'])),
    TransitionTreeVertex(5, Trace(['A','A','A'])),
    TransitionTreeVertex(6, Trace(['A','B','C'])),
    TransitionTreeVertex(7, Trace(['A','A','A','B'])),
    TransitionTreeVertex(8, Trace(['A','B','C','D'])),
    TransitionTreeVertex(9, Trace(['A','B','C','E'])),
    TransitionTreeVertex(10, Trace(['A','A','A','B','E'])),
    TransitionTreeVertex(11, Trace(['A','B','C','D','E'])),
    TransitionTreeVertex(12, Trace(['A','B','C','D','D'])),
    TransitionTreeVertex(13, Trace(['A','B','C','E','E'])),
    TransitionTreeVertex(14, Trace(['A','A','A','B','E', HALT_ACT])),
    TransitionTreeVertex(15, Trace(['A','B','C','D','E', HALT_ACT])),
    TransitionTreeVertex(16, Trace(['A','B','C','D','D', HALT_ACT])),
    TransitionTreeVertex(17, Trace(['A','B','C','E','E', HALT_ACT])),
]
SSMALL_FLOWS = set([
    TransitionTreePopulationFlow(SSMALL_ROOT, 'A', SSMALL_VERTS[1], 
        [ ComplexEvent('A', {}), ] * 5                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[1], 'A', SSMALL_VERTS[2], 
        [ ComplexEvent('A', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[1], 'B', SSMALL_VERTS[3], 
        [ ComplexEvent('B', {}), ] * 4                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[2], 'A', SSMALL_VERTS[4], 
        [ ComplexEvent('A', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[3], 'C', SSMALL_VERTS[5], 
        [ ComplexEvent('C', {}), ] * 4                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[4], 'B', SSMALL_VERTS[6], 
        [ ComplexEvent('B', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[5], 'D', SSMALL_VERTS[7], 
        [ ComplexEvent('D', {}), ] * 3                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[5], 'E', SSMALL_VERTS[8], 
        [ ComplexEvent('D', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[6], 'E', SSMALL_VERTS[9], 
        [ ComplexEvent('E', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[7], 'D', SSMALL_VERTS[11], 
        [ ComplexEvent('D', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[7], 'E', SSMALL_VERTS[10], 
        [ ComplexEvent('E', {}), ] * 2                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[8], 'E', SSMALL_VERTS[12], 
        [ ComplexEvent('E', {}), ] * 1                             
    ),

    TransitionTreePopulationFlow(SSMALL_VERTS[9], HALT_ACT, SSMALL_VERTS[13], 
        [ ComplexEvent('E', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[11], HALT_ACT, SSMALL_VERTS[15], 
        [ ComplexEvent('D', {}), ] * 1                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[10], HALT_ACT, SSMALL_VERTS[14], 
        [ ComplexEvent('E', {}), ] * 2                             
    ),
    TransitionTreePopulationFlow(SSMALL_VERTS[12], HALT_ACT, SSMALL_VERTS[16], 
        [ ComplexEvent('E', {}), ] * 1                             
    ),
])
SSMALL_VERTS = set(SSMALL_VERTS)

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
        self.assertEqual(tree.strict_vertices(), D1_STRICT) 
        # test offers
        self.assertEqual(tree.offers(), D1_OFFERS)
        # test choices
        self.assertEqual(tree.choices(), D1_CHOICES)

    def test_validate_attributes(self):
        self.assertEqual(D1_TREE.attributes(), D1_ATTRS) 

    def test_populations(self):
        # TODO
        pass 

    def test_guards(self):
        # TODO 
        pass 

    def test_simple_log_construction(self):
        try :
            tree = construct_from_log(read_xes_simple(SSMALL))
            self.assertTrue(isinstance(tree, TransitionTree))
            self.assertEqual(tree.vertices() , SSMALL_VERTS)
            self.assertEqual(tree.flows() , SSMALL_FLOWS)
        except Exception as e:
            self.fail("Failed to construct a transition tree with simple log"+ 
                      f" :: {e}") 

    def test_complex_log_construction(self):
        try :
            tree = construct_from_log(read_xes_complex(SSMALL))
            self.assertTrue(isinstance(tree, TransitionTree))
            self.assertEqual(tree.vertices() , SSMALL_VERTS)
            self.assertEqual(tree.flows() , SSMALL_FLOWS)
        except Exception as e:
            self.fail("Failed to construct a transition tree with complex log"+ 
                      f" :: {e}")  
            
    def test_building_dot_file(self):
        try :
            tree = construct_from_log(read_xes_simple(SSMALL))
            tree.generate_dot(path.join(".", "tests", "dummy.dot"))
            remove(path.join(".", "tests", "dummy.dot"))
        except Exception as e:
            self.fail("Failed to construct a dot file for transition tree "+
                      f" :: {e}")


