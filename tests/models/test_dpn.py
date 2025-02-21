import unittest
import tempfile
from os.path import join 

TEST_DPN = join(".","tests", "models", "tester_dpn.pnml")

from pmkoalas.models.petrinets.read import parse_pnml_for_dpn
from pmkoalas.models.petrinets.export import export_net_to_pnml


class TestPetriNetWithData(unittest.TestCase):

    def test_parse(self):
        try:
            dpn = parse_pnml_for_dpn(TEST_DPN)
        except Exception as e:
            self.fail("Failed to parse DPN :: " + str(e))

    def test_repr(self):
        # imports needed for the eval of the repr
        from pmkoalas.models.petrinets.pn import Place, Arc 
        from pmkoalas.models.petrinets.dpn import PetriNetWithData,GuardedTransition
        from pmkoalas.models.petrinets.guards import Guard,Expression
        dpn = parse_pnml_for_dpn(TEST_DPN).net
        other_dpn = eval(dpn.__repr__())
        self.assertEqual(dpn, other_dpn)

    def test_exporting(self):
        dpn = parse_pnml_for_dpn(TEST_DPN)
        with tempfile.TemporaryDirectory() as outdir:
            export_net_to_pnml(dpn, join(outdir, "dpn"))
            other_dpn = parse_pnml_for_dpn(join(outdir, "dpn"))
            self.assertEqual(dpn.net.transitions, other_dpn.net.transitions)
            self.assertEqual(dpn.net.places, other_dpn.net.places)
            self.assertEqual(dpn.net.arcs, other_dpn.net.arcs)
            self.assertEqual(dpn.net, other_dpn.net)

