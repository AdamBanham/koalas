import unittest

from pmkoalas.enhancement.classification_problems import find_classification_problems
from pmkoalas.models.petrinet import parse_pnml_into_lpn

from os.path import join 

EXAMPLES_DIR = join("tests","enhancement", "examples")
EXAMPLE_PNML = join(EXAMPLES_DIR, "example_parallel_net.pnml")
NET = parse_pnml_into_lpn(EXAMPLE_PNML)

class ClassificationProblemsTest(unittest.TestCase):

    def test_postset(self):
        problems = find_classification_problems(NET, type="postset") 
        self.assertEqual(len(problems), 2)

    def test_marking(self):
        problems = find_classification_problems(NET, type="marking")  
        self.assertEqual(len(problems), 11)

    def test_regions(self):
        problems = find_classification_problems(NET, type="regions") 
        self.assertEqual(len(problems), 7)

    def test_single_bag(self):
        problems = find_classification_problems(NET, type="single-bag") 
        self.assertEqual(len(problems), 1)