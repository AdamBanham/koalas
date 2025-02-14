
import string
import tempfile
import unittest
from random import choice

from pmkoalas.models.petrinets.pn import Place, Transition, Arc
from pmkoalas.models.petrinets.dot import convert_net_to_dot
from pmkoalas.models.petrinets.export import convert_net_to_xmlstr
from pmkoalas.models.petrinets.export import export_net_to_pnml
from pmkoalas.models.petrinets.read import parse_pnml_into_lpn
from pmkoalas.models.pnfrag import *
from logging import *


expectedXML = '''<pnml>
  <net type="http://www.pnml.org/version-2009/grammar/pnmlcoremodel" id="dotTest">
    <name>
      <text>dotTest</text>
    </name>
    <page id="page1">
      <place id="place-4">
        <name>
          <text>Student</text>
        </name>
      </place>
      <place id="place-3">
        <name>
          <text>Sweep</text>
        </name>
      </place>
      <place id="place-1">
        <name>
          <text>I</text>
        </name>
      </place>
      <transition id="transition-2" invisible="true">
        <name>
          <text>tau</text>
        </name>
        <toolspecific tool="StochasticPetriNet" version="0.2" invisible="True" priority="1" weight="2.0" distributionType="IMMEDIATE" />
      </transition>
      <arc source="transition-2" target="place-3" id="arc-1" />
      <arc source="place-1" target="transition-2" id="arc-2" />
      <arc source="transition-2" target="place-4" id="arc-3" />
    </page>
  </net>
</pnml>
'''

class PetriNetTest(unittest.TestCase):

    # Note many tests on the construction and operation of Petri nets are in 
    # test_pnfrag

    def test_repr_place(self):
        # test that places can be reproduced
        p = Place("p1")
        p2 = eval(p.__repr__())
        self.assertEqual(p, p2, "reproduced places does not match given place.")

    def test_hash_place(self):
        # test hashing works
        p = Place("p1")
        p2 = Place("z1")
        try:
            p.__hash__()
            p2.__hash__()
        except Exception as e:
            self.fail("Failed to compute hashes for places")
        vp = 1 
        vp2 = 2
        mapping = dict()
        mapping[p] = vp 
        mapping[p2] = vp2 
        self.assertEqual(mapping[p], vp)
        self.assertEqual(mapping[p2], vp2)       

    def test_repr_transition(self):
        # test that transitions can be reproduced
        t = Transition("t1")
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2)
        t = Transition("t1", silent=True)
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2)
        t = Transition("t1", weight=0.5)
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2)
        t = Transition("t1", weight=0.25,silent=True)
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2)

    def test_hash_transition(self):
        # test hashing works
        p = Transition("t1")
        p2 = Transition("t2",weight=0.5, silent=True)
        try:
            p.__hash__()
            p2.__hash__()
        except Exception as e:
            self.fail("Failed to compute hashes for places")
        vp = 1 
        vp2 = 2
        mapping = dict()
        mapping[p] = vp 
        mapping[p2] = vp2 
        self.assertEqual(mapping[p], vp)
        self.assertEqual(mapping[p2], vp2)

    def test_repr_arc(self):
        # test that arcs can be reproduced
        t = Transition("t1")
        t2 = Transition("t2", weight=1.0, silent=True)
        p = Place("p1")
        p2 = Place("p2")
        # testing
        arc = Arc(p, t)
        arc2 = eval(arc.__repr__())
        self.assertEqual(arc, arc2)
        arc = Arc(t, p2)
        arc2 = eval(arc.__repr__())
        self.assertEqual(arc, arc2)
        arc = Arc(p, t2)
        arc2 = eval(arc.__repr__())
        self.assertEqual(arc, arc2)
        arc = Arc(t2, p2)
        arc2 = eval(arc.__repr__())
        self.assertEqual(arc, arc2)

    def test_place_eq(self):
        p1 = Place("I", pid="1")
        p1a = Place("I", pid="1")
        self.assertEqual(p1, p1a, "places with same name and pid are not equal")
        p2 = Place("F", pid="3")
        p2a = Place("F", pid="3")
        self.assertEqual(p2, p2a, "places with same name and pid are not equal")
        groupa = set([p1, p2])
        groupb = set([p1a, p2a])
        self.assertEqual(groupa, groupb, "groups of places are not equal")

    def test_repr_net(self):
        # test that nets can be reproduced
        net = LabelledPetriNet(
          places=[
            Place("p1",pid="f9da4b8b-2ebe-4384-a2f1-ae484cf898c8"),
            Place("p2",pid="1da99779-a974-40b3-9573-bf34ab4c43cc"),
          ],
          transitions=[
            Transition("t1",tid="24747a8f-0f98-4f2a-9694-1a6687c01334",
                       weight=1.0,silent=False),
          ],
          arcs=[
            Arc(from_node=Place("p1",
                        pid="f9da4b8b-2ebe-4384-a2f1-ae484cf898c8"),
                to_node=Transition("t1",
                        tid="24747a8f-0f98-4f2a-9694-1a6687c01334",
                                  weight=1.0,silent=False)
            ),
            Arc(from_node=Transition("t1",
                        tid="24747a8f-0f98-4f2a-9694-1a6687c01334",
                                    weight=1.0,silent=False),
                to_node=Place("p1",
                        pid="f9da4b8b-2ebe-4384-a2f1-ae484cf898c8")),
          ],
          name='Petri net'
        )
        net2 = eval(net.__repr__())
        self.assertEqual(net, net2, "reproduced net does not match given net")

    def test_references_on_net(self):
        # test that references to containers are not reused
        places = set( Place(f"p{i}") for i in range(5))
        transitions = set( Transition(f"t{i}") for i in range(6))
        arcs = set()
        net = LabelledPetriNet(places=places, transitions=transitions, 
                arcs=arcs)
        # check that removing or adding to original or returned 
        # does not change anything
        ## add a place
        onet = eval(net.__repr__())
        places.add(Place("p7"))
        self.assertNotEqual(places, net.places, 
                "reference container is reused on structure.")
        self.assertEqual(net, onet, "struture has changed.")
        ## remove transition
        transitions = [t for t in transitions if not t.name.endswith('5') ]
        self.assertNotEqual(net.transitions, transitions, 
                "reference container is reused on structure.")
        self.assertEqual(net, onet, "structure has changed.")
        ## add a arc
        p = choice(list(places))
        t = choice(list(transitions))
        arc = Arc(p, t)
        arcs.add(arc)
        self.assertNotEqual(net.arcs, arcs, 
                "reference container is reused on structure.")
        self.assertEqual(net, onet, "structure has changed.")

    def test_exportToDOT(self):
        parser = PetriNetFragmentParser()
        net1 = parser.create_net("dotTest","I -> {tau 2.0} -> Sweep")
        parser.add_to_net(net1,"I -> {tau 2.0} -> Student")
        dotStr = convert_net_to_dot(net1)
        # Not a rigorous check, just a way to check it doesn't throw exceptions
        # by plugging manually into DOT
        debug(dotStr)

    def assertCharactersEqual(self, s1, s2):
        # Crude, structure insensitive check that all the expected 
        # characters are in both strings after stripping whitespace
        remove = string.punctuation + string.whitespace
        mapping = {ord(c): None for c in remove}
        debug(f'Mapping: \n{mapping}')
        self.assertEqual ( sorted(s1.translate(mapping)), 
                           sorted(s2.translate(mapping)) )

    def test_exportToXML(self):
        parser = PetriNetFragmentParser()
        net1 = parser.create_net("dotTest","I -> {tau 2.0} -> Sweep")
        parser.add_to_net(net1,"I -> {tau 2.0} -> Student")
        debug(net1)
        xmlStr = convert_net_to_xmlstr(net1)
        debug(xmlStr)
        debug('=================\n')
        debug(f"\n{xmlStr}\n")
        with tempfile.NamedTemporaryFile(delete=True) as outfile:
            debug(outfile.name)
            export_net_to_pnml( net1, outfile ) 
        # can't guarantee output order
        self.assertCharactersEqual(expectedXML,xmlStr)

    def test_reading_pnml(self):
        net1 = LabelledPetriNet(
            [Place("I", "place-1"), Place("p2","place-2"), 
             Place("F", "place-3")],
            [ Transition("tau", "transition-1", 1, True),
             Transition("a", "transition-2", 1, False) ],
            [
                Arc(Place("I", "place-1"), Transition("tau", "transition-1", 1, True)),
                Arc(Transition("tau", "transition-1", 1, True), Place("p2", "place-2")),
                Arc(Place("p2", "place-2"), Transition("a", "transition-2", 1, False)),
                Arc(Transition("a", "transition-2", 1, False), Place("F", "place-3"))
            ],
            "tester"
        )
        with tempfile.TemporaryDirectory() as outdir:
            export_net_to_pnml( net1, outdir + "/dotTest.pnml" ) 
            net2 = parse_pnml_into_lpn(outdir + "/dotTest.pnml")
        self.assertEqual(net1, net2, 
          "Exported and re-imported nets are not equal")


