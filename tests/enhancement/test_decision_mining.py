import unittest

from pmkoalas.enhancement.decision_mining import mine_guards_for_lpn
from pmkoalas.models.petrinet import parse_pnml_into_lpn
from pmkoalas.read import read_xes_complex 

from os.path import join
from os import environ

EXAMPLES_DIR = join("tests","enhancement", "examples")
RF_PNML_FILE = join(EXAMPLES_DIR, "road_fines_normative_model.pnml")
RF_LOG_FILE = join(EXAMPLES_DIR, "roadfines_big_sampled.xes")

SKIP_SLOW = eval(environ['SKIP_SLOW_TESTS'])

class DecisionMiningTests(unittest.TestCase):

    def setUp(self):
        self.log = read_xes_complex(RF_LOG_FILE)
        self.lpn = parse_pnml_into_lpn(RF_PNML_FILE)

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_postset_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            classification="postset")
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_marking_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            classification="marking")
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_regions_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            classification="regions")
    
    def tearDown(self):
        del self.log 
        del self.lpn