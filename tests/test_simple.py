import unittest
from koalas.simple import Trace


class TraceTest(unittest.TestCase):
    def test_init(self):
        t = Trace(['a','c'])
 
    def test_str(self):
        self.assertEqual( '<b>', str(Trace(['b']) ) )
        self.assertEqual( '<a,b>', str(Trace(['a','b']) ) )
        self.assertEqual( '<>', str(Trace([]) ) )



if __name__ == '__main__':
    unittest.main()

