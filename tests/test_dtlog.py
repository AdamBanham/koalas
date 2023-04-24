
import unittest
from pmkoalas.dtlog import *

class DTLogTest(unittest.TestCase):
    def test_convert_empty(self):
        self.assertEqual( EventLog([]), convert() )

    def test_convert_single_trace(self):
        self.assertEqual( Trace(['a']), convertTrace("a" ) )

    def test_convert_single_trace_multi_event(self):
        self.assertEqual( Trace(['a','b']), convertTrace("a b" ) )
        self.assertEqual( Trace(['d','a','b']), convertTrace("d a b" ) )
        self.assertEqual( Trace(['jill','alex','thingy']), 
                          convertTrace("jill alex thingy" ) )
        self.assertEqual( Trace(['a','b']), 
                          convertTrace("a-b", delimiter='-' ) )

    def test_convert_single(self):
        self.assertEqual( EventLog([Trace(['a'])]), convert("a" ) )
        self.assertEqual( EventLog([Trace(['a','b'])]), convert("a b" ) )

    def test_convert_triple(self):
        self.assertEqual( EventLog([Trace(['a','b']),
                                    Trace(['a']), 
                                    Trace(['a','b'])]), 
                          convert("a b","a","a b" ) )



if __name__ == '__main__':
    unittest.main()


