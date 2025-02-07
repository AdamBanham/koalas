import unittest

from pmkoalas.enhancement.decision_mining import mine_guards_for_lpn
from pmkoalas.models.petrinet import parse_pnml_into_lpn
from pmkoalas.read import read_xes_complex 
from pmkoalas._logging import setLevel

from os.path import join
from os import environ
from logging import INFO, ERROR

EXAMPLES_DIR = join("tests","enhancement", "examples")
RF_PNML_FILE = join(EXAMPLES_DIR, "road_fines_normative_model.pnml")
RF_LOG_FILE = join(EXAMPLES_DIR, "roadfines_big_sampled.xes")

SKIP_SLOW = eval(environ['SKIP_SLOW_TESTS'])

class DecisionMiningTests(unittest.TestCase):

    def setUp(self):
        self.log = read_xes_complex(RF_LOG_FILE)
        self.lpn = parse_pnml_into_lpn(RF_PNML_FILE)
        setLevel(INFO)

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_postset_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            identification="postset")
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_marking_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            identification="marking")
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_regions_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            identification="regions")
    
    def tearDown(self):
        del self.log 
        del self.lpn
        setLevel(ERROR)