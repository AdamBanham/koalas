import unittest

from pmkoalas.models.petrinet import parse_pnml_into_lpn
from pmkoalas.models.petrinet import export_net_to_pnml
from pmkoalas.models.petrinet import BuildablePetriNet

from tempfile import TemporaryDirectory
from os.path import join

MODEL_ONE = join(".", "tests", "models", "examples", "ax3_model_1.pnml")

class ExportingAndReadingNets(unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def test_petri_net(self):
        m1 = parse_pnml_into_lpn(MODEL_ONE, use_localnode_id=True)
        with TemporaryDirectory() as dir:
            export_net_to_pnml(m1, join(dir, "test.pnml"), include_prom_bits=True)
            m2 = parse_pnml_into_lpn(join(dir, "test.pnml"), use_localnode_id=True)
        self.assertEqual(m1.name, m2.name)
        self.assertEqual(m1.places, m2.places)
        self.assertEqual(m1.transitions, m2.transitions)
        self.assertEqual(m1.arcs, m2.arcs)
        self.assertEqual(m1.initial_marking, m2.initial_marking)
        self.assertEqual(m1.final_marking, m2.final_marking)

    def test_petri_net_nolocal(self):
        m1 = parse_pnml_into_lpn(MODEL_ONE, use_localnode_id=False)
        with TemporaryDirectory() as dir:
            export_net_to_pnml(m1, join(dir, "test.pnml"), include_prom_bits=True)
            m2 = parse_pnml_into_lpn(join(dir, "test.pnml"), use_localnode_id=False)
        self.assertEqual(m1.name, m2.name)
        self.assertEqual(m1.places, m2.places)
        self.assertEqual(m1.transitions, m2.transitions)
        self.assertEqual(m1.arcs, m2.arcs)
        self.assertEqual(m1.initial_marking, m2.initial_marking)
        self.assertEqual(m1.final_marking, m2.final_marking)