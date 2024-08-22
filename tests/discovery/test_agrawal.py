import unittest

from pmkoalas.simple import Trace
from pmkoalas import dtlog
from pmkoalas.discovery.agrawal_miner import ArgrawalMinerInstance
from pmkoalas.discovery.agrawal_miner import DependencyEdge,DependencyNode
from pmkoalas.discovery.agrawal_miner import DependencyGraph
from pmkoalas.discovery.agrawal_miner import execution_is_consistent

class DTLogTest(unittest.TestCase):

    def test_consistency(self):
        graph_consistent = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("D"),
                DependencyNode("C"),
                DependencyNode("E"),
            ]),
            set([
                DependencyEdge( 
                    DependencyNode("A"),
                    DependencyNode("B")
                ),
                DependencyEdge( 
                    DependencyNode("A"),
                    DependencyNode("D")
                ),
                DependencyEdge( 
                    DependencyNode("A"),
                    DependencyNode("C")
                ),
                DependencyEdge( 
                    DependencyNode("B"),
                    DependencyNode("D")
                ),
                DependencyEdge( 
                    DependencyNode("B"),
                    DependencyNode("C")
                ),
                DependencyEdge( 
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
                DependencyEdge( 
                    DependencyNode("C"),
                    DependencyNode("E")
                ),
            ])
        )

        graph_inconsistent = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("D"),
                DependencyNode("C"),
                DependencyNode("E"),
            ]),
            set([ 
                DependencyEdge( 
                    DependencyNode("A"),
                    DependencyNode("B")
                ),
                DependencyEdge( 
                    DependencyNode("A"),
                    DependencyNode("D")
                ),
                DependencyEdge( 
                    DependencyNode("B"),
                    DependencyNode("D")
                ),
                DependencyEdge( 
                    DependencyNode("B"),
                    DependencyNode("C")
                ),
                DependencyEdge( 
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
                DependencyEdge( 
                    DependencyNode("C"),
                    DependencyNode("E")
                ),
            ])
        )
        execution = Trace(["A", "C", "B", "E"])
        self.assertTrue(
            execution_is_consistent(execution, graph_consistent),
            "Should be consistent with trace"
        )
        self.assertFalse(
            execution_is_consistent(execution, graph_inconsistent),
            "Should be inconsistent with trace"
        )

class TestArgrawalMinerInstance(unittest.TestCase):

    def setUp(self):
        self.miner = ArgrawalMinerInstance()

    def test_compute_follows_relations_simple(self):
        log = dtlog.convert("a b c", "a c", "b c")
        expected_follows = {('b', 'a'), ('c', 'b'), ('c', 'a')}
        self.assertEqual(self.miner.compute_follows_relations(log), expected_follows)

    def test_compute_follows_relations_no_follows(self):
        log = dtlog.convert("a", "b", "c")
        expected_follows = set()
        self.assertEqual(self.miner.compute_follows_relations(log), expected_follows)

    def test_compute_follows_relations_complex(self):
        log = dtlog.convert("a b c e", "a c d e", "a d b e")
        expected_follows = {('b', 'a'), ('c', 'a'), ('d', 'a'), ('e', 'a'), 
                            ('c', 'b'), ('e', 'b'), 
                            ('e', 'c'), ('d', 'c'),
                            ('b', 'd'), ('e', 'd') }
        self.assertEqual(self.miner.compute_follows_relations(log), expected_follows)
