import unittest

from pmkoalas.enhancement.decision_mining import mine_guards_for_lpn
from pmkoalas.models.petrinet import parse_pnml_into_lpn
from pmkoalas.models.petrinet import export_net_to_pnml
from pmkoalas.conformance.alignments import find_alignments_for_variants
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
        if (not SKIP_SLOW):
            self.ali = find_alignments_for_variants(self.log, self.lpn, 'pm4py')

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_postset_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="postset",
            expansion='earnest')
        export_net_to_pnml(dpn, 
            "postset_earnst.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="postset", 
            expansion='shortcut')
        export_net_to_pnml(dpn, 
            "postset_shortcut.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log,
            alignment=self.ali,
            identification="postset", 
            expansion='duplicate')
        export_net_to_pnml(dpn, 
            "postset_duplicate.pnml",
            include_prom_bits=True)
    
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_marking_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="marking",
            expansion='earnest')
        export_net_to_pnml(dpn, 
            "marking_earnst.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="marking",
            expansion='shortcut')
        export_net_to_pnml(dpn, 
            "marking_shortcut.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="marking",
            expansion='duplicate')
        export_net_to_pnml(dpn, 
            "marking_duplicate.pnml",
            include_prom_bits=True)
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 90s")
    def test_regions_mining(self):
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="regions",
            expansion='earnest')
        export_net_to_pnml(dpn, 
            "regions_earnst.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="regions",
            expansion='shortcut')
        export_net_to_pnml(dpn, 
            "regions_shortcut.pnml",
            include_prom_bits=True)
        
        dpn = mine_guards_for_lpn(self.lpn, self.log, 
            alignment=self.ali,
            identification="regions",
            expansion='duplicate')
        export_net_to_pnml(dpn, 
            "regions_duplicate.pnml",
            include_prom_bits=True)
    
    def tearDown(self):
        del self.log 
        del self.lpn