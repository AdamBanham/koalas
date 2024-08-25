import unittest
from logging import DEBUG, ERROR, INFO
from copy import deepcopy   

from pmkoalas.simple import Trace
from pmkoalas import dtlog
from pmkoalas._logging import setLevel
from pmkoalas.discovery.agrawal_miner import AgrawalMinerInstance
from pmkoalas.discovery.agrawal_miner import DependencyEdge,DependencyNode
from pmkoalas.discovery.agrawal_miner import DependencyGraph
from pmkoalas.discovery.agrawal_miner import execution_is_consistent
from pmkoalas.discovery.agrawal_miner import is_conformal
from pmkoalas.discovery.agrawal_miner import find_strongly_connected_components


class TestDependencyGraph(unittest.TestCase):

    def setUp(self):
        setLevel(ERROR)
        self.fig1 = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("C"),
                DependencyNode("D"),
                DependencyNode("E"),
            ]),
            set([
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("B")
                ),DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("D")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
            ])
        )

        self.fig2a = DependencyGraph(
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
                    DependencyNode("C")
                ),
                 DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("D")
                ),
                 DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("C")
                ),
                 DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("D")
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

        self.fig2b = DependencyGraph(
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
                    DependencyNode("C")
                ),
                 DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("D")
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

        self.fig3a = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("C"),
                DependencyNode("D"),
                DependencyNode("E"),
            ]),
            set([
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("B")
                ),
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("D")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
            ])
        )

        self.fig3b = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("C"),
                DependencyNode("D"),
                DependencyNode("E"),
            ]),
            set([
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("B")
                ),
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("D")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
            ])
        )

    def tearDown(self):
        setLevel(ERROR)

    def test_consistency(self):
        graph_consistent = self.fig2a
        graph_inconsistent = self.fig2b
        exec1 = dtlog.convertTrace("A D C E")
        exec2 = dtlog.convertTrace("A B C D E")
        self.assertTrue(
            execution_is_consistent(exec1, graph_consistent),
            f"Should be consistent with trace ({exec1})"
        )
        self.assertTrue(
            execution_is_consistent(exec2, graph_consistent),
            f"Should be consistent with trace ({exec2})"
        )
        self.assertFalse(
            execution_is_consistent(exec1, graph_inconsistent),
            "Should be inconsistent with trace ({exec1})"
        )
        self.assertTrue(
            execution_is_consistent(exec2, graph_inconsistent),
            f"Should be consistent with trace ({exec2})"
        )

    def test_consistency_agrawal(self):
        graph = self.fig1
        con_exec = dtlog.convertTrace("A C B E")
        incon_exec = dtlog.convertTrace("A D B E")
        self.assertTrue(
            execution_is_consistent(con_exec, graph),
            f"Should be consistent with trace ({con_exec})."
        )
        self.assertFalse(
            execution_is_consistent(incon_exec, graph),
            f"Should be inconsistent with trace ({incon_exec})."
        )

    def test_conformal(self):
        conformal_graph = self.fig2a
        non_conformal_graph = self.fig2b
        log = dtlog.convert( 
            "A D C E",
            "A B C D E"
        )
        self.assertTrue(
            is_conformal(log, conformal_graph),
            f"Should be conformal with log ({log}).")
        self.assertFalse(
            is_conformal(log, non_conformal_graph),
            f"Should not be conformal with log ({log}).")
        
    def test_transitive_reduction(self):
        base_graph = self.fig3a
        expected_graph = self.fig3b
        self.assertEqual(
            base_graph.transitive_reduction(),
            expected_graph,
            "Should return the expected transitive reduction."
        )

    def test_equality(self):
        # trues
        self.assertEqual(self.fig1,deepcopy(self.fig1))
        self.assertEqual(self.fig2a,deepcopy(self.fig2a))
        self.assertEqual(self.fig2b,deepcopy(self.fig2b))
        self.assertEqual(self.fig3a,deepcopy(self.fig3a))
        self.assertEqual(self.fig3b,deepcopy(self.fig3b))
        # falses
        self.assertNotEqual(self.fig1,self.fig2a)
        self.assertNotEqual(deepcopy(self.fig1),deepcopy(self.fig2a))

    def test_equality_of_nodes(self):
        node1 = DependencyNode("A")
        node2 = DependencyNode("A")
        node3 = DependencyNode("B")
        self.assertEqual(node1, node2, "Nodes with the same label should be equal")
        self.assertNotEqual(node1, node3, "Nodes with different labels should not be equal")

    def test_equality_of_edges(self):
        edge1 = DependencyEdge(DependencyNode("A"), DependencyNode("B"))
        edge2 = DependencyEdge(DependencyNode("A"), DependencyNode("B"))
        edge3 = DependencyEdge(DependencyNode("A"), DependencyNode("C"))
        self.assertEqual(edge1, edge2, "Edges with the same source and target should be equal")
        self.assertNotEqual(edge1, edge3, "Edges with different sources and targets should not be equal")

    def test_strongly_connected(self):
        graph = DependencyGraph(
                set([
                        DependencyNode('A'),
                        DependencyNode('B'),
                        DependencyNode('C'),
                        DependencyNode('D'),
                        DependencyNode('E'),
                        DependencyNode('F'),
                        DependencyNode('C'),
                        DependencyNode('D'),
                ]),
                set([
                        DependencyEdge(
                                DependencyNode('A'),
                                DependencyNode('B'),
                        ),
                        DependencyEdge(
                                DependencyNode('A'),
                                DependencyNode('C'),
                        ),
                        DependencyEdge(
                                DependencyNode('A'),
                                DependencyNode('D'),
                        ),
                        DependencyEdge(
                                DependencyNode('A'),
                                DependencyNode('E'),
                        ),
                        DependencyEdge(
                                DependencyNode('A'),
                                DependencyNode('F'),
                        ),
                        DependencyEdge(
                                DependencyNode('E'),
                                DependencyNode('C'),
                        ),
                        DependencyEdge(
                                DependencyNode('E'),
                                DependencyNode('F'),
                        ),
                        DependencyEdge(
                                DependencyNode('C'),
                                DependencyNode('D'),
                        ),
                        DependencyEdge(
                                DependencyNode('C'),
                                DependencyNode('F'),
                        ),
                        DependencyEdge(
                                DependencyNode('D'),
                                DependencyNode('E'),
                        ),
                        DependencyEdge(
                                DependencyNode('D'),
                                DependencyNode('F'),
                        ),
                        DependencyEdge(
                                DependencyNode('D'),
                                DependencyNode('E'),
                        ),
                        DependencyEdge(
                                DependencyNode('D'),
                                DependencyNode('F'),
                        ),
                        DependencyEdge(
                                DependencyNode('C'),
                                DependencyNode('D'),
                        ),
                        DependencyEdge(
                                DependencyNode('C'),
                                DependencyNode('F'),
                        ),
                        DependencyEdge(
                                DependencyNode('B'),
                                DependencyNode('C'),
                        ),
                        DependencyEdge(
                                DependencyNode('B'),
                                DependencyNode('F'),
                        ),
                ]),
        )
        expect_compontents = [
            {DependencyNode(label='F')},
            {DependencyNode(label='E'), DependencyNode(label='D'), 
             DependencyNode(label='C')},
            {DependencyNode(label='B')},
            {DependencyNode(label='A')}
        ]
        self.assertEqual(find_strongly_connected_components(graph), 
                          expect_compontents,
        )

    def test_repr_is_same(self):
        self.assertEqual(
            self.fig1,
            eval(repr(self.fig1)),
            "Should return the same graph when parsed from its repr."
        )
        self.assertEqual(
            self.fig1.create_dot_form(),
            eval(repr(self.fig1)).create_dot_form(),
            "Should return the same dot when parsed from its repr."
        )
        self.assertEqual(
            self.fig2a,
            eval(repr(self.fig2a)),
            "Should return the same graph when parsed from its repr."
        )
        self.assertEqual(
            self.fig2a.create_dot_form(),
            eval(repr(self.fig2a)).create_dot_form(),
            "Should return the same dot when parsed from its repr."
        )
        self.assertEqual(
            self.fig2b,
            eval(repr(self.fig2b)),
            "Should return the same graph when parsed from its repr."
        )
        self.assertEqual(
            self.fig2b.create_dot_form(),
            eval(repr(self.fig2b)).create_dot_form(),
            "Should return the same dot when parsed from its repr."
        )


class TestAgrawalMinerInstance(unittest.TestCase):

    def setUp(self):
        self.miner = AgrawalMinerInstance()
        setLevel(ERROR)

    def tearDown(self):
        setLevel(ERROR)

    def test_compute_follows_relations_simple(self):
        log = dtlog.convert("a b c", "a c", "b c")
        expected_follows = {('b', 'a'), ('c', 'b'), ('c', 'a')}
        self.assertEqual(self.miner.compute_follows_relations(log), 
                         expected_follows)

    def test_compute_dependencies_simple(self):
        log = dtlog.convert("a b c", "a c", "b c")
        expected_dependencies = {('b', 'a'), ('c', 'b'), ('c', 'a')}
        self.assertEqual(self.miner.compute_dependencies(log), 
                         expected_dependencies)

    def test_compute_follows_relations_none(self):
        log = dtlog.convert("a", "b", "c")
        expected_follows = set()
        self.assertEqual(self.miner.compute_follows_relations(log), 
                         expected_follows)

    def test_compute_dependencies_none(self):
        log = dtlog.convert("a", "b", "c")
        expected_dependencies = set()
        self.assertEqual(self.miner.compute_dependencies(log), 
                         expected_dependencies)
        
    def test_compute_independent_none(self):
        log = dtlog.convert("a", "b", "c")
        expected_dependencies = set([ ('a','b'), ('a','c'), 
                                      ('b','a'), ('b','c'), 
                                      ('c','a'), ('c','b')])
        self.assertEqual(self.miner.compute_indepentent_activities(log), 
                         expected_dependencies)

    def test_compute_follows_relations_complex(self):
        log = dtlog.convert("a b c e", "a c d e", "a d b e")
        expected_follows = {('b', 'a'), ('c', 'a'), ('d', 'a'), ('e', 'a'), 
                            ('c', 'b'), ('e', 'b'), ('d', 'b'),
                            ('e', 'c'), ('d', 'c'), ('b', 'c'),
                            ('b', 'd'), ('e', 'd'), ('c', 'd') }
        self.assertEqual(self.miner.compute_follows_relations(log), 
                         expected_follows)
        
    def test_compute_follows_dependencies_complex(self):
        log = dtlog.convert("a b c e", "a c d e", "a d b e")
        expected_follows = {('b', 'a'), ('c', 'a'), ('d', 'a'), ('e', 'a'), 
                            ('e', 'b'), 
                            ('e', 'c'),  
                            ('e', 'd'),  }
        self.assertEqual(self.miner.compute_dependencies(log), 
                         expected_follows)

    def test_compute_follows_independent_complex(self):
        log = dtlog.convert("a b c e", "a c d e", "a d b e")
        expected_follows = { 
                            ('c', 'b'), ('d', 'b'),
                            ('d', 'c'), ('b', 'c'),
                            ('b', 'd'), ('c', 'd') 
                            }
        self.assertEqual(self.miner.compute_indepentent_activities(log), 
                         expected_follows)

    def test_compute_follows_relations_transitive(self):
        log = dtlog.convert("a b c e", "a c d e", "a d b e", "a d c e")
        expected_follows = {('b', 'a'), ('c', 'a'), ('d', 'a'), ('e', 'a'), 
                            ('c', 'b'), ('e', 'b'), 
                            ('e', 'c'), 
                            ('b', 'd'), ('e', 'd'), ('c', 'd') }
        self.assertEqual(self.miner.compute_follows_relations(log), 
                         expected_follows)
        
    def test_consistent_activity_usage(self):
        log = dtlog.convert("a b c e", "a c b e", "c b a e", "e a b c")
        self.assertTrue(
            self.miner._test_for_consistent_activity_usage(log,1),
            "Should return true as all activities are observed in traces once."
        )
        self.assertFalse(
            self.miner._test_for_consistent_activity_usage(log,2),
            "Should return false as all activities are not observed in traces twice."
        )

    def test_compute_special_dag(self):
        log = dtlog.convert("A B C D E", "A C D B E", "A C B D E")
        expected_graph = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("C"),
                DependencyNode("D"),
                DependencyNode("E"),
            ]),
            set([
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("B")
                ),DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("D")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
            ])
        )
        self.assertEqual(self.miner.discover(log), expected_graph)

    def test_compute_general_dag(self):
        log = dtlog.convert("A B C F", "A C D F", "A D E F", "A E C F")
        expected_graph = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("C"),
                DependencyNode("D"),
                DependencyNode("E"),
                DependencyNode("F"),
            ]),
            set([
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("B")
                ),
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("D")
                ),
                DependencyEdge(
                    DependencyNode("A"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("F")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("F")
                ),
                DependencyEdge(
                    DependencyNode("E"),
                    DependencyNode("F")
                )
            ])
        )
        disc_graph = self.miner.discover(log)
        self.assertEqual(disc_graph.vertices(), expected_graph.vertices())
        self.assertEqual(disc_graph.edges(), expected_graph.edges())
        self.assertEqual(disc_graph, expected_graph)

    def test_compute_cyclic_graph(self):
        log = dtlog.convert("A B D C E", "A B D C B C E", 
                            "A B C B D C E", "A D E")
        expected_graph = DependencyGraph(
            set([
                DependencyNode("A"),
                DependencyNode("B"),
                DependencyNode("C"),
                DependencyNode("D"),
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
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("B"),
                    DependencyNode("D")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("B")
                ),
                DependencyEdge(
                    DependencyNode("C"),
                    DependencyNode("E")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("C")
                ),
                DependencyEdge(
                    DependencyNode("D"),
                    DependencyNode("E")
                ),
            ])
        )
        disc_graph = self.miner.discover(log)
        self.assertEqual(disc_graph.vertices(), expected_graph.vertices())
        self.assertEqual(disc_graph.edges(), expected_graph.edges())
        self.assertEqual(disc_graph, expected_graph)

class TestAgrawalMinerInstanceOpt(TestAgrawalMinerInstance):

    def setUp(self):
        self.miner = AgrawalMinerInstance(
            optimise_step_five=True
        )
        setLevel(ERROR)

    def tearDown(self):
        setLevel(ERROR)

    def test_repr_is_same(self):
        log = dtlog.convert("A B D C E", "A B D C B C E", 
                            "A B C B D C E", "A D E")
        graph = self.miner.discover(log)
        self.assertEqual(
            graph,
            eval(repr(graph)),
            "Should return the same graph when parsed from its repr."
        )
        self.assertEqual(
            graph.create_dot_form(),
            eval(repr(graph)).create_dot_form(),
            "Should return the same dot when parsed from its repr."
        )