
import string
import tempfile
import unittest

from pmkoalas.models.petrinet import Place, Transition, Arc
from pmkoalas.models.pnfrag import *
from logging import *


expectedXML = '''<pnml>
  <net type="('http://www.pnml.org/version-2009/grammar/pnmlcoremodel',)" id="dotTest">
    <page id="page1">
      <place id="4">
        <name>
          <text>Student</text>
        </name>
      </place>
      <place id="3">
        <name>
          <text>Sweep</text>
        </name>
      </place>
      <place id="1">
        <name>
          <text>I</text>
        </name>
      </place>
      <transition id="2">
        <name>
          <text>tau</text>
        </name>
        <toolspecific tool="StochasticPetriNet" version="0.2" invisible="True" priority="1" weight="2.0" distributionType="IMMEDIATE" />
      </transition>
      <arc source="2" target="4" id="1" />
      <arc source="1" target="2" id="2" />
      <arc source="2" target="3" id="3" />
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

    def test_repr_transition(self):
        # test that transitions can be reproduced
        t = Transition("t1")
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2, "reproduced transition does not match given transition.")
        t = Transition("t1", silent=True)
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2, "reproduced transition does not match given transition.")
        t = Transition("t1", weight=0.5)
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2, "reproduced transition does not match given transition.")
        t = Transition("t1", weight=0.25,silent=True)
        t2 = eval(t.__repr__())
        self.assertEqual(t, t2, "reproduced transition does not match given transition.")


    def test_exportToDOT(self):
        parser = PetriNetFragmentParser()
        net1 = parser.createNet("dotTest","I -> {tau 2.0} -> Sweep")
        parser.addToNet(net1,"I -> {tau 2.0} -> Student")
        dotStr = exportToDOT(net1)
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
        net1 = parser.createNet("dotTest","I -> {tau 2.0} -> Sweep")
        parser.addToNet(net1,"I -> {tau 2.0} -> Student")
        xmlStr = exportToPNMLStr(net1)
        debug('=================\n')
        debug(f"\n{xmlStr}\n")
        with tempfile.NamedTemporaryFile(delete=True) as outfile:
            debug(outfile.name)
            exportToPNML( net1, outfile ) 
        # can't guarantee output order
        self.assertCharactersEqual(expectedXML,xmlStr)

