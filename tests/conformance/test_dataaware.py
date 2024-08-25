import unittest

from os.path import join 
from os import environ

from pmkoalas.read import read_xes_complex
from pmkoalas.models.petrinet import parse_pnml_for_dpn
from pmkoalas.conformance.dataaware import compute_guard_precision
from pmkoalas.conformance.dataaware import compute_guard_recall
from pmkoalas.conformance.dataaware import compute_determinism

CONF_FOLD = join(".","tests","conformance")
LOG_LOC = join(CONF_FOLD,"test_log.xes")
SKIP_SLOW = eval(environ['SKIP_SLOW_TESTS'])

class DataawareTests(unittest.TestCase):
    
    def setUp(self) -> None:
        self.TEST_LOG = read_xes_complex(LOG_LOC)
        self.DPN_A = parse_pnml_for_dpn(join(CONF_FOLD, "test_dpn_a.pnml"))
        self.DPN_B = parse_pnml_for_dpn(join(CONF_FOLD, "test_dpn_b.pnml"))
        self.DPN_C = parse_pnml_for_dpn(join(CONF_FOLD, "test_dpn_c.pnml"))
        self.DPN_D = parse_pnml_for_dpn(join(CONF_FOLD, "test_dpn_d.pnml"))
        return super().setUp()
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_computation_grec_unopt(self):
        try :
            compute_guard_recall(self.TEST_LOG, self.DPN_B, optimised=False) 
        except Exception as e:
            self.fail("failed computation for grec using unoptimised prod :: "
                      + str(e)
            )
    
    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_computation_grec_opt(self):
        try :
            compute_guard_recall(self.TEST_LOG, self.DPN_B, optimised=True) 
        except Exception as e:
            self.fail("failed computation for grec using optimised prod :: "
                      + str(e)
            ) 

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_computation_gprec_unopt(self):
        try :
            compute_guard_precision(self.TEST_LOG, self.DPN_B, optimised=False) 
        except Exception as e:
            self.fail("failed computation for gprec using unoptimised prod :: "
                      + str(e)
            )  

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_computation_gprec_opt(self):
        try :
            compute_guard_precision(self.TEST_LOG, self.DPN_B, optimised=True)  
        except Exception as e:
            self.fail("failed computation for gprec using optimised prod :: "
                      + str(e)
            )  

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_opt_grec_is_equivalent(self):
        opt_measure = compute_guard_recall(
            self.TEST_LOG, self.DPN_A)
        unopt_measure = compute_guard_recall(
            self.TEST_LOG, self.DPN_A, optimised=False) 
        self.assertEqual(opt_measure, unopt_measure, 
            "optimised and unoptimised routines for grec disagree on measurements"
            +f" :: opt-{opt_measure} vs unopt-{unopt_measure}")

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_opt_gprec_is_equivalent(self):
        opt_measure = compute_guard_precision(
            self.TEST_LOG, self.DPN_C)
        unopt_measure = compute_guard_precision(
            self.TEST_LOG, self.DPN_C, optimised=False) 
        self.assertEqual(opt_measure, unopt_measure, 
            "optimised and unoptimised routines for gprec disagree on measurements"
            +f" :: opt-{opt_measure} vs unopt-{unopt_measure}") 

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_max_of_grec(self):
        measure = compute_guard_recall(self.TEST_LOG, self.DPN_C)
        self.assertEqual(measure, 1.0, "grec failed to return 1.0 (maxx) when"
                         + " expected to.") 

    @unittest.skipIf(SKIP_SLOW, "testing can take up to 20s")
    def test_max_of_gprec(self):
        measure = compute_guard_precision(self.TEST_LOG, self.DPN_A)
        self.assertEqual(measure, 1.0, "gprec failed to return 1.0 (maxx) when"
                         + " expected to.")  
        
    def test_determinism_max(self):
        measure = compute_determinism(self.DPN_A)
        self.assertEqual(measure, 1.0, "expected a measure of 1.0")
        measure = compute_determinism(self.DPN_B)
        self.assertEqual(measure, 1.0, "expected a measure of 1.0")

    def test_determinism_mid(self):
        measure = compute_determinism(self.DPN_C)
        self.assertEqual(measure, 3.0/6.0, "expected a measure of roughly 1/2")

    def test_determinism_min(self):
        measure = compute_determinism(self.DPN_D)
        self.assertEqual(measure, 0.0, "expected a measure of 0.0")