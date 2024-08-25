import unittest
import tempfile
from os.path import join 

TEST_DPN = join(".","tests", "models", "tester_dpn.pnml")

from pmkoalas.models.petrinet import *
from pmkoalas.models.guards import Guard,Expression

class TestPetriNetWithData(unittest.TestCase):

    def test_parse(self):
        try:
            dpn = parse_pnml_for_dpn(TEST_DPN)
        except Exception as e:
            self.fail("Failed to parse DPN :: " + str(e))

    def test_repr(self):
        dpn = parse_pnml_for_dpn(TEST_DPN)
        other_dpn = eval(dpn.__repr__())
        self.assertEqual(dpn == other_dpn, True)

    def test_exporting(self):
        dpn = parse_pnml_for_dpn(TEST_DPN)
        with tempfile.TemporaryDirectory() as outdir:
            export_net_to_pnml(dpn, join(outdir, "dpn"))
            other_dpn = parse_pnml_for_dpn(join(outdir, "dpn"))
            self.assertEqual(dpn.transitions, other_dpn.transitions)
            self.assertEqual(dpn.places, other_dpn.places)
            self.assertEqual(dpn.arcs, other_dpn.arcs)
            self.assertEqual(dpn, other_dpn)

