import unittest

from pmkoalas.simple import Trace

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
