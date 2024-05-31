
import unittest
from pmkoalas.dtlog import *

class DTLogTest(unittest.TestCase):
    def test_convert_empty(self):
        self.assertEqual( EventLog([]), convert() )

    def test_convert_single_trace(self):
        self.assertEqual( EventLog([Trace(['a'])]), convert("a") )

    def test_convert_single_trace_multi_event(self):
        self.assertEqual( Trace(['a','b']), convertTrace("a b") )
        self.assertEqual( Trace(['d','a','b']), convertTrace("d a b") )
        self.assertEqual( Trace(['jill','alex','thingy']), 
                          convertTrace("jill alex thingy") )
        self.assertEqual( Trace(['a','b']), 
                          convertTrace("a-b", delimiter='-') )

    def test_convert_single(self):
        self.assertEqual( EventLog([Trace(['a'])]), convert("a") )
        self.assertEqual( EventLog([Trace(['a','b'])]), convert("a b") )

    def test_convert_triple(self):
        self.assertEqual( EventLog([Trace(['a','b']),
                                    Trace(['a']), 
                                    Trace(['a','b'])]), 
                          convert("a b","a","a b" ) )
    
    def test_delimiter_on_convert(self):
        self.assertEqual(
            EventLog([Trace(['a','b','c']), Trace(['a','d','c'])]),
            convert("a-b-c","a-d-c",delimiter="-")
        )

    # def test_mut_aug(self):
    #     self.assertEqual(
    #         EventLog( [ Trace(['a','b','c'])] *5 ),
    #         convert("a b c || ^5")
    #     )
    #     self.assertEqual(
    #         EventLog( [Trace(['a','b','d'])] + [ Trace(['a','b','c'])] *5 ),
    #         gen_log("a b c || ^5", "a b d")
    #     )

    # def test_no_aug(self):
    #     self.assertEqual(
    #         EventLog( [Trace(['a','b','c']), Trace(['a','b','b'])] ),
    #         gen_log("a b c ||", "a b b ||")
    #     )

    def test_data_issue_aug(self):
        pass

if __name__ == '__main__':
    unittest.main()


