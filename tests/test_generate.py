import unittest
from pmkoalas.generate import *
from pmkoalas.simple import Trace
from random import randint

class DTLogTest(unittest.TestCase):

    def test_generate_trace(self):
        ret = generate_trace("a b c")
        for t in ret:
            self.assertEqual(Trace(["a","b","c"]), t , "unable to generate trace.") 

    def test_generate_mut_aug(self):
        for _ in range(10):
            mut = randint(4,100)
            ret = generate_trace(f"a b c || ^{mut}")
            self.assertEqual(len([t for t in ret]), mut, 
                    "mut aug not producing the correct number of traces.")
            for t in ret:
                self.assertEqual(Trace(["a","b","c"]), t , 
                                 "unsuitable trace generated")  

    def test_generate_issue_aug(self):
        ret = generate_trace("a b c || %d100")
        for t in ret:
            self.assertNotEqual(Trace(["a","b","c"]), t, 
                f"data issue did not change anything :: {t}"
            ) 
    
    def test_generate_issue_impossible(self):
        with self.assertRaises(DataIssueImpossible):
            ret = generate_trace("a || %d25")
        with self.assertRaises(DataIssueImpossible):
            ret = generate_trace("a a a a || %d25")

    def test_compunding_augs(self):
        ret = generate_trace("a b c d e || ^1000 d%25") 
        # test length
        self.assertEqual(len([t for t in ret]), 1000, 
                    "mut aug not producing the correct number of traces.")
        # test that a data issue happen (some small chance for it not happening)
        issue = False
        for t in ret:
            issue = issue or Trace(["a","b","c"]) != t
            if (issue):
                break
        self.assertEqual(issue, True, "data issue did not happen.")

    def test_generate_log(self):
        try : 
            log = generate_log("a b c")
            self.assertEqual(len(log), 1)
            log = generate_log("a b c || ^5")
            self.assertEqual(len(log), 5)
            self.assertEqual(log.language(), set([Trace(["a","b","c"])]))
            log = generate_log("a b c", "a b c || %d100")
            found_same = False
            found_diff = False
            for t,_ in log:
                if t == Trace(["a","b","c"]):
                    found_same = True 
                if t != Trace(["a","b","c"]):
                    found_diff = True 
            self.assertEqual(found_same and found_diff, True,
                             "Unable to produce log with desired properties.")
            log = generate_log( 
                "a b c || ^25",
                "a b c d e || ^25",
                "a b c || ^25 %d25",
                "a b c d e || ^25 %d33"
            )
            self.assertEqual(len(log), 100)
        except Exception as e:
            self.fail(f"unable to generate log as :: {e}") 

    def test_generate_from_grammar(self):
        pass