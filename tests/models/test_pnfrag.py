import doctest
import unittest

from pmkoalas.models.petrinet import *
from pmkoalas.models.pnfrag import *



initialI = Place("I",1)

expected_net_parsed_with_spaces = LabelledPetriNet(
        places=[
                Place("F",pid=3),
                Place("p",pid=1),
                Place("I",pid=1),
        ],
        transitions=[
                Transition("tau",tid=2,weight=1.0,silent=True),
                Transition("Create Fine",tid=2,weight=1.0,silent=False),
                Transition("Create Finer",tid=3,weight=0.3,silent=False),
        ],
        arcs=[
                Arc(from_node=Transition("tau",tid=2,weight=1.0,
                    silent=True),to_node=Place("F",pid=3)),
                Arc(from_node=Place("I",pid=1),to_node=Transition(
                    "Create Finer",tid=3,weight=0.3,silent=False)),
                Arc(from_node=Place("I",pid=1),to_node=Transition(
                    "Create Fine",tid=2,weight=1.0,silent=False)),
                Arc(from_node=Transition("Create Finer",tid=3,weight=0.3,
                    silent=False),to_node=Place("p",pid=1)),
                Arc(from_node=Place("p",pid=1),to_node=Transition("tau",
                    tid=2,weight=1.0,silent=True)),
                Arc(from_node=Transition("Create Fine",tid=2,weight=1.0,
                    silent=False),to_node=Place("p",pid=1)),
        ],
        name='ROAD FINES NORMATIVE MODEL'
)

class PetriNetFragmentTest(unittest.TestCase):
    def setUp(self):
        self.parser = PetriNetFragmentParser()


    def test_invalid_input(self):
       self.assertRaises(ParseException, self.parser.create_net,
               "invalid", "I --> ~jerry [a] -> F")

    def test_ptp_fragment(self):
        tran_a = Transition("a",2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a]),
                                     arcs = set([Arc(initialI,tran_a),
                                                 Arc(tran_a,final)]),
                                     name = 'test' )
        result = self.parser.create_net("test","I -> [a] -> F")
        self.assertEqual( expected, result )

    def test_duplicate_arcs(self):
        expected = BuildablePetriNet("test_duplicate_arcs");
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta = Transition("a",2)
        expected.add_transition(ta)
        finalPlace = Place("F",3)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta)
        expected.add_arc_between(ta,finalPlace)
        net = BuildablePetriNet("test_duplicate_arcs")
        self.parser.add_to_net(net, "I -> [a] -> F")
        self.parser.add_to_net(net, "I -> [a] -> F")
        self.assertEqual( expected, net)

    def test_tran_with_id(self):
        expected = BuildablePetriNet("tran_with_id")
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta = Transition("a",1)
        expected.add_transition(ta)
        finalPlace = Place("F",2)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta)
        expected.add_arc_between(ta,finalPlace)
        net = BuildablePetriNet("tran_with_id")
        self.parser.add_to_net(net, "I -> [a__1] -> F")
        self.assertEqual( expected, net)

    def test_dupe_tran_with_id(self):
        expected = BuildablePetriNet("dupe_tran_with_id")
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta1 = Transition("a",1)
        expected.add_transition(ta1)
        ta2 = Transition("a",2)
        expected.add_transition(ta2)
        finalPlace = Place("F",2)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta1)
        expected.add_arc_between(ta1,finalPlace)
        expected.add_arc_between(initialPlace, ta2)
        expected.add_arc_between(ta2,finalPlace)
        net = BuildablePetriNet("dupe_tran_with_id")
        self.parser.add_to_net(net, "I -> [a__1] -> F")
        self.parser.add_to_net(net, "I -> [a__2] -> F")
        self.assertEqual( expected, net)

    def test_dupe_tran_with_partial_id(self):
        expected = BuildablePetriNet("dupe_tran_with_id")
        initialPlace = Place("I",1)
        ta1 = Transition("a",1)
        ta2 = Transition("a",2)
        tb = Transition("b",3)
        finalPlace = Place("F",2)
        expected.add_place(initialPlace) \
            .add_transition(ta1) \
            .add_transition(ta2) \
            .add_transition(tb) \
            .add_place(finalPlace) \
            .add_arc_between(initialPlace, ta1) \
            .add_arc_between(ta1,finalPlace) \
            .add_arc_between(initialPlace, ta2) \
            .add_arc_between(ta2,finalPlace) \
            .add_arc_between(initialPlace, tb) \
            .add_arc_between(tb,finalPlace)
        net = BuildablePetriNet("dupe_tran_with_id")
        self.parser.add_to_net(net, "I -> [a__1] -> F")
        self.parser.add_to_net(net, "I -> [a__2] -> F")
        self.parser.add_to_net(net, "I -> [b]    -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition(self):
        tran_a = Transition("a",weight=0.4,tid=2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a]),
                                     arcs = set([Arc(initialI,tran_a),
                                                 Arc(tran_a,final)]),
                                     name = "weighted_transition" )
        net = self.parser.create_net("weighted_transition","I -> {a 0.4} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition_with_id(self):
        tran_a = Transition("a",weight=0.4,tid=1)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a]),
                                     arcs = set([Arc(initialI,tran_a),
                                                 Arc(tran_a,final)]),
                                     name = "weighted_transition_with_id" )
        net = self.parser.create_net("weighted_transition_with_id",
                                    "I -> {a__1 0.4} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_weighted_transition_with_dupes(self):
        tran_a1 = Transition("a",weight=0.4,tid=1)
        tran_a2 = Transition("a",weight=0.5,tid=2)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a1,tran_a2]),
                                     arcs = set([Arc(initialI,tran_a1),
                                                 Arc(tran_a1,final),
                                                 Arc(initialI,tran_a2),
                                                 Arc(tran_a2,final)]),
                                     name = "weighted_transition_with_dupes" )
        net = self.parser.create_net("weighted_transition_with_dupes",
                                    "I -> {a__1 0.4} -> F")
        self.parser.add_to_net(net,   "I -> {a__2 0.5} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_id_backrefs(self):
        tran_a1 = Transition("a",tid=1)
        tran_a2 = Transition("a",tid=2)
        tranB  = Transition("b",tid=4)
        p1    = Place("p1",3)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,p1,final]),
                                     transitions = set([tran_a1,tran_a2,tranB]),
                                     arcs = set([Arc(initialI,tran_a1),
                                                 Arc(tran_a1,final),
                                                 Arc(initialI,tran_a2),
                                                 Arc(tran_a2,final),
                                                 Arc(tran_a2,p1),
                                                 Arc(p1,tranB),
                                                 Arc(tranB,final)]),
                                     name = "id_backrefs" )
        net = self.parser.create_net("id_backrefs",
                                    "I -> {a__1} -> F")
        self.parser.add_to_net(net,   "I -> {a__2} -> F")
        self.parser.add_to_net(net,   "I -> {a__2} -> p1 -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_id_backrefs_weighted(self):
        tran_a1 = Transition("a",tid=1,weight=0.4)
        tran_a2 = Transition("a",tid=2,weight=0.5)
        tranB  = Transition("b",tid=4)
        p1    = Place("p1",3)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,p1,final]),
                                     transitions = set([tran_a1,tran_a2,tranB]),
                                     arcs = set([Arc(initialI,tran_a1),
                                                 Arc(tran_a1,final),
                                                 Arc(initialI,tran_a2),
                                                 Arc(tran_a2,final),
                                                 Arc(tran_a2,p1),
                                                 Arc(p1,tranB),
                                                 Arc(tranB,final)]),
                                     name = "id_backrefs_weighted" )
        net = self.parser.create_net("id_backrefs_weighted",
                                    "I -> {a__1 0.4} -> F")
        self.parser.add_to_net(net,   "I -> {a__2 0.5} -> F")
        self.parser.add_to_net(net,   "I -> {a__2 0.5} -> p1 -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition_above_ten(self):
        tran_a = Transition("a",weight=10.4,tid=2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a]),
                                     arcs = set([Arc(initialI,tran_a),
                                                 Arc(tran_a,final)]),
                                     name = "weighted_transition_above_ten" )
        net = self.parser.create_net("weighted_transition_above_ten",
                                    "I -> {a 10.4} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition_default_weight(self):
        tran_a = Transition("a",tid=2)
        final = Place("F",3)
        expected = LabelledPetriNet( 
                    places = set([initialI,final]),
                    transitions = set([tran_a]),
                    arcs = set([Arc(initialI,tran_a),
                                Arc(tran_a,final)]),
                    name = "weighted_transition_default_weight" )
        net = self.parser.create_net("weighted_transition_default_weight",
                                    "I -> {a} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_two_transition_fragment(self):
        expected = BuildablePetriNet("two_transition_fragment")
        initialPlace = Place("initialPlace",1)
        expected.add_place(initialPlace)
        t1 = Transition("transition1",2)
        expected.add_transition(t1)
        mp = Place("mp",3)
        expected.add_place(mp)
        t2 = Transition("transition2",4)
        expected.add_transition(t2)
        finalPlace = Place("finalPlace",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, t1)
        expected.add_arc_between(t1,mp)
        expected.add_arc_between(mp, t2)
        expected.add_arc_between(t2,finalPlace)
        net = BuildablePetriNet("two_transition_fragment")
        self.parser.add_to_net(net, 
            "initialPlace -> [transition1] -> mp -> [transition2] -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_trailing_whitespace(self):
        expected = BuildablePetriNet("trailing_whitespace")
        initialPlace = Place("initialPlace",1)
        expected.add_place(initialPlace)
        t1 = Transition("transition1",2)
        expected.add_transition(t1)
        mp = Place("mp",3)
        expected.add_place(mp)
        t2 = Transition("transition2",4)
        expected.add_transition(t2)
        finalPlace = Place("finalPlace",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, t1)
        expected.add_arc_between(t1,mp)
        expected.add_arc_between(mp, t2)
        expected.add_arc_between(t2,finalPlace)
        net = BuildablePetriNet("trailing_whitespace")
        self.parser.add_to_net(net, 
            "initialPlace -> [transition1] -> mp -> [transition2] -> finalPlace ")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_blog_example(self):
        expected = BuildablePetriNet("blog_example")
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta = Transition("a",2)
        expected.add_transition(ta)
        tb = Transition("b",4)
        expected.add_transition(tb)
        finalPlace = Place("F",3)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta)
        expected.add_arc_between(ta,finalPlace)
        expected.add_arc_between(initialPlace, tb)
        expected.add_arc_between(tb,finalPlace)
        parser = PetriNetFragmentParser()
        # This is equivalent to a single net
	#     [a]
	# I -/   \-> F
	#    \[b]/
        net = parser.create_net("blog_example",
                             "I -> [a] -> F")
        parser.add_to_net(net, "I -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))
        # loop example
        net = parser.create_net("net",
		               "I -> [a] -> p1 -> [b] -> F")
        parser.add_to_net(net,               "p1 -> [c] -> p1")
        # no assert for the loop here or in the Java version ...

    def test_multi_edge(self):
        expected = BuildablePetriNet("multi_edge")
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta = Transition("a",2)
        expected.add_transition(ta)
        tb = Transition("b",4)
        expected.add_transition(tb)
        finalPlace = Place("F",3)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta)
        expected.add_arc_between(ta,finalPlace)
        expected.add_arc_between(initialPlace, tb)
        expected.add_arc_between(tb,finalPlace)
        parser = PetriNetFragmentParser()
        # This is equivalent to a single net
	#     [a]
	# I -/   \-> F
	#    \[b]/
        net = parser.create_net("multi_edge",
                             "I -> [a] -> F")
        parser.add_to_net(net, "I -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    # No equivalent tests for the accepting net, as it's more of an artifact of 
    # the Java class hierarchy in ProM
        

    def test_silent_transition(self):
        expected = BuildablePetriNet("silent_transition")
        initialPlace = Place("initialPlace",1)
        expected.add_place(initialPlace)
        t1 = Transition("transition1",2)
        expected.add_transition(t1)
        mp = Place("mp",3)
        expected.add_place(mp)
        t2 = silent_transition(tid=4)
        expected.add_transition(t2)
        finalPlace = Place("finalPlace",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, t1)
        expected.add_arc_between(t1,mp)
        expected.add_arc_between(mp, t2)
        expected.add_arc_between(t2,finalPlace)
        net = BuildablePetriNet("silent_transition")
        self.parser.add_to_net(net, 
            "initialPlace -> [transition1] -> mp -> [tau] -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_silent_weighted_transition(self):
        expected = BuildablePetriNet("silent_weighted_transition")
        initialPlace = Place("initialPlace",1)
        expected.add_place(initialPlace)
        t1 = Transition("transition1",2)
        expected.add_transition(t1)
        mp = Place("mp",3)
        expected.add_place(mp)
        t2 = silent_transition(tid=4)
        expected.add_transition(t2)
        finalPlace = Place("finalPlace",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, t1)
        expected.add_arc_between(t1,mp)
        expected.add_arc_between(mp, t2)
        expected.add_arc_between(t2,finalPlace)
        net = BuildablePetriNet("silent_weighted_transition")
        self.parser.add_to_net(net, 
            "initialPlace -> {transition1} -> mp -> {tau} -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_silent_transition_with_ids(self):
        expected = BuildablePetriNet("silent_transition")
        initialPlace = Place("initialPlace",1)
        expected.add_place(initialPlace)
        t1 = Transition("transition1",2)
        expected.add_transition(t1)
        mp = Place("mp",3)
        expected.add_place(mp)
        tau1 = silent_transition(tid=1)
        expected.add_transition(tau1)
        tau2 = silent_transition(tid=2)
        expected.add_transition(tau2)
        mp2 = Place("mp2",4)
        expected.add_place(mp2)
        finalPlace = Place("finalPlace",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, t1)
        expected.add_arc_between(t1,mp)
        expected.add_arc_between(mp, tau1)
        expected.add_arc_between(tau1,mp2)
        expected.add_arc_between(mp2,tau2)
        expected.add_arc_between(tau2,finalPlace)
        net = BuildablePetriNet("silent_transition")
        self.parser.add_to_net(net, 
            "initialPlace -> [transition1] -> mp -> [tau__1] -> mp2 -> [tau__2] -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_place_with_id(self):
        expected = BuildablePetriNet("place_with_id")
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta = Transition("a",2)
        expected.add_transition(ta)
        finalPlace = Place("F",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta)
        expected.add_arc_between(ta,finalPlace)
        net = BuildablePetriNet("place_with_id")
        self.parser.add_to_net(net, "I -> [a] -> F__5")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_place_with_id_lookup(self):
        expected = BuildablePetriNet("place_with_id")
        initialPlace = Place("I",1)
        expected.add_place(initialPlace)
        ta = Transition("a",2)
        expected.add_transition(ta)
        tb = Transition("b",3)
        expected.add_transition(tb)
        finalPlace = Place("F",5)
        expected.add_place(finalPlace)
        expected.add_arc_between(initialPlace, ta)
        expected.add_arc_between(ta,finalPlace)
        expected.add_arc_between(initialPlace, tb)
        expected.add_arc_between(tb,finalPlace)
        net = BuildablePetriNet("place_with_id")
        self.parser.add_to_net(net, "I -> [a] -> F__5")
        self.parser.add_to_net(net, "I -> [b] -> F__5")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_parse_net_fragments_function(self):
        tran_a = Transition("a",2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a]),
                                     arcs = set([Arc(initialI,tran_a),
                                                 Arc(tran_a,final)]),
                                     name = 'test' )
        result = parse_net_fragments("test","I -> [a] -> F")
        self.assertEqual( expected, result )

    def test_create_net_function(self):
        tran_a = Transition("a",2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tran_a]),
                                     arcs = set([Arc(initialI,tran_a),
                                                 Arc(tran_a,final)]),
                                     name = 'test' )
        result = create_net("test","I -> [a] -> F")
        self.assertEqual( expected, result )

    def test_spaces_in_labels(self):
        result = parse_net_fragments(
            "ROAD FINES NORMATIVE MODEL",
            "I -> [  Create Fine __ 2] -> p __ 1 -> [  tau] -> F",
            "I -> [Create Fine __ 2 ] -> p __ 1 -> [tau  ] -> F",
            "I -> [  Create Fine __ 2 ] -> p __ 1 -> [   tau      ] -> F",
            "I -> {              Create Finer  __ 3   0.3} -> p __ 1 -> [tau      ] -> F",
        )
        self.assertTrue(result == expected_net_parsed_with_spaces)
        

def load_tests(loader, tests, ignore):
    ''' docstring tests in main module'''
    import pmkoalas.models.pnfrag as pnfrag
    tests.addTests(doctest.DocTestSuite(pnfrag))
    return tests


