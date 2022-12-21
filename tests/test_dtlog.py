
import unittest
from koalas.simple import EventLog,Trace
from koalas.generate import gen_log, gen_trace

class DTLogTest(unittest.TestCase):
    def test_convert_empty(self):
        self.assertEqual( EventLog([]), gen_log() )

    def test_convert_single_trace(self):
        self.assertEqual( Trace(['a']), gen_trace("a") )

    def test_convert_single_trace_multi_event(self):
        self.assertEqual( Trace(['a','b']), gen_trace("a b") )
        self.assertEqual( Trace(['d','a','b']), gen_trace("d a b") )
        self.assertEqual( Trace(['jill','alex','thingy']), 
                          gen_trace("jill alex thingy") )
        self.assertEqual( Trace(['a','b']), 
                          gen_trace("a-b", delimiter='-') )

    def test_convert_single(self):
        self.assertEqual( EventLog([Trace(['a'])]), gen_log("a") )
        self.assertEqual( EventLog([Trace(['a','b'])]), gen_log("a b") )

    def test_convert_triple(self):
        self.assertEqual( EventLog([Trace(['a','b']),
                                    Trace(['a']), 
                                    Trace(['a','b'])]), 
                          gen_log("a b","a","a b" ) )



if __name__ == '__main__':
    unittest.main()


