import unittest

from pmkoalas.models.petrinet import *
from pmkoalas.models.pnfrag import *



initialI = Place("I",1)

class PetriNetFragmentTest(unittest.TestCase):
    def setUp(self):
        self.parser = PetriNetFragmentParser()


    def test_invalid_input(self):
       self.assertRaises(ParseException, self.parser.createNet,
               "invalid", "I --> ~jerry [a] -> F")

    def test_ptp_fragment(self):
        tranA = Transition("a",2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tranA]),
                                     arcs = set([Arc(initialI,tranA),
                                                 Arc(tranA,final)]),
                                     label = 'test' )
        result = self.parser.createNet("test","I -> [a] -> F")
        self.assertEqual( expected, result )

    def test_duplicate_arcs(self):
        expected = MutableLabelledPetriNet("test_duplicate_arcs");
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta = Transition("a",2)
        expected.addTransition(ta)
        finalPlace = Place("F",3)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta)
        expected.addArcForNodes(ta,finalPlace)
        net = MutableLabelledPetriNet("test_duplicate_arcs")
        self.parser.addToNet(net, "I -> [a] -> F")
        self.parser.addToNet(net, "I -> [a] -> F")
        self.assertEqual( expected, net)

    def test_tran_with_id(self):
        expected = MutableLabelledPetriNet("tran_with_id")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta = Transition("a",1)
        expected.addTransition(ta)
        finalPlace = Place("F",2)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta)
        expected.addArcForNodes(ta,finalPlace)
        net = MutableLabelledPetriNet("tran_with_id")
        self.parser.addToNet(net, "I -> [a__1] -> F")
        self.assertEqual( expected, net)

    def test_dupe_tran_with_id(self):
        expected = MutableLabelledPetriNet("dupe_tran_with_id")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta1 = Transition("a",1)
        expected.addTransition(ta1)
        ta2 = Transition("a",2)
        expected.addTransition(ta2)
        finalPlace = Place("F",2)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta1)
        expected.addArcForNodes(ta1,finalPlace)
        expected.addArcForNodes(initialPlace, ta2)
        expected.addArcForNodes(ta2,finalPlace)
        net = MutableLabelledPetriNet("dupe_tran_with_id")
        self.parser.addToNet(net, "I -> [a__1] -> F")
        self.parser.addToNet(net, "I -> [a__2] -> F")
        self.assertEqual( expected, net)

    def test_dupe_tran_with_partial_id(self):
        expected = MutableLabelledPetriNet("dupe_tran_with_id")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta1 = Transition("a",1)
        expected.addTransition(ta1)
        ta2 = Transition("a",2)
        expected.addTransition(ta2)
        tb = Transition("b",3)
        expected.addTransition(tb)
        finalPlace = Place("F",2)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta1)
        expected.addArcForNodes(ta1,finalPlace)
        expected.addArcForNodes(initialPlace, ta2)
        expected.addArcForNodes(ta2,finalPlace)
        expected.addArcForNodes(initialPlace, tb)
        expected.addArcForNodes(tb,finalPlace)
        net = MutableLabelledPetriNet("dupe_tran_with_id")
        self.parser.addToNet(net, "I -> [a__1] -> F")
        self.parser.addToNet(net, "I -> [a__2] -> F")
        self.parser.addToNet(net, "I -> [b]    -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition(self):
        tranA = Transition("a",weight=0.4,tid=2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tranA]),
                                     arcs = set([Arc(initialI,tranA),
                                                 Arc(tranA,final)]),
                                     label = "weighted_transition" )
        net = self.parser.createNet("weighted_transition","I -> {a 0.4} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition_with_id(self):
        tranA = Transition("a",weight=0.4,tid=1)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tranA]),
                                     arcs = set([Arc(initialI,tranA),
                                                 Arc(tranA,final)]),
                                     label = "weighted_transition_with_id" )
        net = self.parser.createNet("weighted_transition_with_id",
                                    "I -> {a__1 0.4} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_weighted_transition_with_dupes(self):
        tranA1 = Transition("a",weight=0.4,tid=1)
        tranA2 = Transition("a",weight=0.5,tid=2)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tranA1,tranA2]),
                                     arcs = set([Arc(initialI,tranA1),
                                                 Arc(tranA1,final),
                                                 Arc(initialI,tranA2),
                                                 Arc(tranA2,final)]),
                                     label = "weighted_transition_with_dupes" )
        net = self.parser.createNet("weighted_transition_with_dupes",
                                    "I -> {a__1 0.4} -> F")
        self.parser.addToNet(net,   "I -> {a__2 0.5} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_id_backrefs(self):
        tranA1 = Transition("a",tid=1)
        tranA2 = Transition("a",tid=2)
        tranB  = Transition("b",tid=4)
        p1    = Place("p1",3)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,p1,final]),
                                     transitions = set([tranA1,tranA2,tranB]),
                                     arcs = set([Arc(initialI,tranA1),
                                                 Arc(tranA1,final),
                                                 Arc(initialI,tranA2),
                                                 Arc(tranA2,final),
                                                 Arc(tranA2,p1),
                                                 Arc(p1,tranB),
                                                 Arc(tranB,final)]),
                                     label = "id_backrefs" )
        net = self.parser.createNet("id_backrefs",
                                    "I -> {a__1} -> F")
        self.parser.addToNet(net,   "I -> {a__2} -> F")
        self.parser.addToNet(net,   "I -> {a__2} -> p1 -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_id_backrefs_weighted(self):
        tranA1 = Transition("a",tid=1,weight=0.4)
        tranA2 = Transition("a",tid=2,weight=0.5)
        tranB  = Transition("b",tid=4)
        p1    = Place("p1",3)
        final = Place("F",2)
        expected = LabelledPetriNet( places = set([initialI,p1,final]),
                                     transitions = set([tranA1,tranA2,tranB]),
                                     arcs = set([Arc(initialI,tranA1),
                                                 Arc(tranA1,final),
                                                 Arc(initialI,tranA2),
                                                 Arc(tranA2,final),
                                                 Arc(tranA2,p1),
                                                 Arc(p1,tranB),
                                                 Arc(tranB,final)]),
                                     label = "id_backrefs_weighted" )
        net = self.parser.createNet("id_backrefs_weighted",
                                    "I -> {a__1 0.4} -> F")
        self.parser.addToNet(net,   "I -> {a__2 0.5} -> F")
        self.parser.addToNet(net,   "I -> {a__2 0.5} -> p1 -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition_above_ten(self):
        tranA = Transition("a",weight=10.4,tid=2)
        final = Place("F",3)
        expected = LabelledPetriNet( places = set([initialI,final]),
                                     transitions = set([tranA]),
                                     arcs = set([Arc(initialI,tranA),
                                                 Arc(tranA,final)]),
                                     label = "weighted_transition_above_ten" )
        net = self.parser.createNet("weighted_transition_above_ten",
                                    "I -> {a 10.4} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_weighted_transition_default_weight(self):
        tranA = Transition("a",tid=2)
        final = Place("F",3)
        expected = LabelledPetriNet( 
                    places = set([initialI,final]),
                    transitions = set([tranA]),
                    arcs = set([Arc(initialI,tranA),
                                Arc(tranA,final)]),
                    label = "weighted_transition_default_weight" )
        net = self.parser.createNet("weighted_transition_default_weight",
                                    "I -> {a} -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_two_transition_fragment(self):
        expected = MutableLabelledPetriNet("two_transition_fragment")
        initialPlace = Place("initialPlace",1)
        expected.addPlace(initialPlace)
        t1 = Transition("transition1",2)
        expected.addTransition(t1)
        mp = Place("mp",3)
        expected.addPlace(mp)
        t2 = Transition("transition2",4)
        expected.addTransition(t2)
        finalPlace = Place("finalPlace",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, t1)
        expected.addArcForNodes(t1,mp)
        expected.addArcForNodes(mp, t2)
        expected.addArcForNodes(t2,finalPlace)
        net = MutableLabelledPetriNet("two_transition_fragment")
        self.parser.addToNet(net, 
            "initialPlace -> [transition1] -> mp -> [transition2] -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_trailing_whitespace(self):
        expected = MutableLabelledPetriNet("trailing_whitespace")
        initialPlace = Place("initialPlace",1)
        expected.addPlace(initialPlace)
        t1 = Transition("transition1",2)
        expected.addTransition(t1)
        mp = Place("mp",3)
        expected.addPlace(mp)
        t2 = Transition("transition2",4)
        expected.addTransition(t2)
        finalPlace = Place("finalPlace",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, t1)
        expected.addArcForNodes(t1,mp)
        expected.addArcForNodes(mp, t2)
        expected.addArcForNodes(t2,finalPlace)
        net = MutableLabelledPetriNet("trailing_whitespace")
        self.parser.addToNet(net, 
            "initialPlace -> [transition1] -> mp -> [transition2] -> finalPlace ")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_blog_example(self):
        expected = MutableLabelledPetriNet("blog_example")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta = Transition("a",2)
        expected.addTransition(ta)
        tb = Transition("b",4)
        expected.addTransition(tb)
        finalPlace = Place("F",3)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta)
        expected.addArcForNodes(ta,finalPlace)
        expected.addArcForNodes(initialPlace, tb)
        expected.addArcForNodes(tb,finalPlace)
        parser = PetriNetFragmentParser()
        # This is equivalent to a single net
	#     [a]
	# I -/   \-> F
	#    \[b]/
        net = parser.createNet("blog_example",
                             "I -> [a] -> F")
        parser.addToNet(net, "I -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))
        # loop example
        net = parser.createNet("net",
		               "I -> [a] -> p1 -> [b] -> F")
        parser.addToNet(net,               "p1 -> [c] -> p1")
        # no assert for the loop here or in the Java version ...

    def test_multi_edge(self):
        expected = MutableLabelledPetriNet("multi_edge")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta = Transition("a",2)
        expected.addTransition(ta)
        tb = Transition("b",4)
        expected.addTransition(tb)
        finalPlace = Place("F",3)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta)
        expected.addArcForNodes(ta,finalPlace)
        expected.addArcForNodes(initialPlace, tb)
        expected.addArcForNodes(tb,finalPlace)
        parser = PetriNetFragmentParser()
        # This is equivalent to a single net
	#     [a]
	# I -/   \-> F
	#    \[b]/
        net = parser.createNet("multi_edge",
                             "I -> [a] -> F")
        parser.addToNet(net, "I -> [b] -> F")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    # No equivalent tests for the accepting net, as it's more of an artifact of 
    # the Java class hierarchy in ProM
        

    def test_silent_transition(self):
        expected = MutableLabelledPetriNet("silent_transition")
        initialPlace = Place("initialPlace",1)
        expected.addPlace(initialPlace)
        t1 = Transition("transition1",2)
        expected.addTransition(t1)
        mp = Place("mp",3)
        expected.addPlace(mp)
        t2 = silentTransition(tid=4)
        expected.addTransition(t2)
        finalPlace = Place("finalPlace",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, t1)
        expected.addArcForNodes(t1,mp)
        expected.addArcForNodes(mp, t2)
        expected.addArcForNodes(t2,finalPlace)
        net = MutableLabelledPetriNet("silent_transition")
        self.parser.addToNet(net, 
            "initialPlace -> [transition1] -> mp -> [tau] -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_silent_weighted_transition(self):
        expected = MutableLabelledPetriNet("silent_weighted_transition")
        initialPlace = Place("initialPlace",1)
        expected.addPlace(initialPlace)
        t1 = Transition("transition1",2)
        expected.addTransition(t1)
        mp = Place("mp",3)
        expected.addPlace(mp)
        t2 = silentTransition(tid=4)
        expected.addTransition(t2)
        finalPlace = Place("finalPlace",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, t1)
        expected.addArcForNodes(t1,mp)
        expected.addArcForNodes(mp, t2)
        expected.addArcForNodes(t2,finalPlace)
        net = MutableLabelledPetriNet("silent_weighted_transition")
        self.parser.addToNet(net, 
            "initialPlace -> {transition1} -> mp -> {tau} -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_silent_transition_with_ids(self):
        expected = MutableLabelledPetriNet("silent_transition")
        initialPlace = Place("initialPlace",1)
        expected.addPlace(initialPlace)
        t1 = Transition("transition1",2)
        expected.addTransition(t1)
        mp = Place("mp",3)
        expected.addPlace(mp)
        tau1 = silentTransition(tid=1)
        expected.addTransition(tau1)
        tau2 = silentTransition(tid=2)
        expected.addTransition(tau2)
        mp2 = Place("mp2",4)
        expected.addPlace(mp2)
        finalPlace = Place("finalPlace",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, t1)
        expected.addArcForNodes(t1,mp)
        expected.addArcForNodes(mp, tau1)
        expected.addArcForNodes(tau1,mp2)
        expected.addArcForNodes(mp2,tau2)
        expected.addArcForNodes(tau2,finalPlace)
        net = MutableLabelledPetriNet("silent_transition")
        self.parser.addToNet(net, 
            "initialPlace -> [transition1] -> mp -> [tau__1] -> mp2 -> [tau__2] -> finalPlace")
        self.assertEqual( expected, net, verbosecmp(expected,net))

    def test_place_with_id(self):
        expected = MutableLabelledPetriNet("place_with_id")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta = Transition("a",2)
        expected.addTransition(ta)
        finalPlace = Place("F",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta)
        expected.addArcForNodes(ta,finalPlace)
        net = MutableLabelledPetriNet("place_with_id")
        self.parser.addToNet(net, "I -> [a] -> F__5")
        self.assertEqual( expected, net, verbosecmp(expected,net))


    def test_place_with_id_lookup(self):
        expected = MutableLabelledPetriNet("place_with_id")
        initialPlace = Place("I",1)
        expected.addPlace(initialPlace)
        ta = Transition("a",2)
        expected.addTransition(ta)
        tb = Transition("b",3)
        expected.addTransition(tb)
        finalPlace = Place("F",5)
        expected.addPlace(finalPlace)
        expected.addArcForNodes(initialPlace, ta)
        expected.addArcForNodes(ta,finalPlace)
        expected.addArcForNodes(initialPlace, tb)
        expected.addArcForNodes(tb,finalPlace)
        net = MutableLabelledPetriNet("place_with_id")
        self.parser.addToNet(net, "I -> [a] -> F__5")
        self.parser.addToNet(net, "I -> [b] -> F__5")
        self.assertEqual( expected, net, verbosecmp(expected,net))



