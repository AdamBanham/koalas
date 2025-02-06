import unittest

from pmkoalas.models.transitionsystem import generate_marking_system
from pmkoalas.models.petrinet import parse_pnml_into_lpn

from os.path import join 

EXAMPLES_DIR = join("tests","enhancement", "examples")
EXAMPLE_PNML = join(EXAMPLES_DIR, "example_parallel_net.pnml")
NET = parse_pnml_into_lpn(EXAMPLE_PNML)

class MarkingSystemTest(unittest.TestCase):

    def test_making_system(self):
        sys = generate_marking_system(NET)
        self.assertEqual(len(sys.initial_states()), 1)
        self.assertEqual(len(sys.final_states()), 1)
        self.assertEqual(len(sys.transitions), 34)
        self.assertEqual(len(sys.states), 18)
        self.assertEqual(len(sys.events), 10)