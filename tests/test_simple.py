import unittest
from koalas.simple import Trace,EventLog
from koalas.generate import gen_log

class TraceTest(unittest.TestCase):
    def test_init(self):
        t = Trace(['a','c'])
 
    def test_str(self):
        self.assertEqual( '<b>', str(Trace(['b']) ) )
        self.assertEqual( '<a,b>', str(Trace(['a','b']) ) )
        self.assertEqual( '<>', str(Trace([]) ) )

    def test_trace_activities(self):
        t = Trace(['a','b','c'])
        self.assertEqual(t.seen_activities(), set(['a','b','c']))
        t = Trace([])
        self.assertEqual(t.seen_activities(), set([]))

    def test_lang_activities(self):
        log = gen_log("a b c", "a b", "c", "")
        self.assertEqual(log.seen_activities(), 
            set(['a','b','c'])
        )
        log = EventLog([])
        self.assertEqual(log.seen_activities(), set())

    def test_lang_start_activities(self):
        log = gen_log("a b c", "b c", "c")
        self.assertEqual(log.seen_start_activities(),
            set(['a', 'b', 'c'])
        )
        log = gen_log("a b c", "a b", "a b c")
        self.assertEqual(log.seen_start_activities(), 
            set(['a'])
        )

    def test_lang_end_activities(self):
        log = gen_log("a b c", "b c", "c")
        self.assertEqual(log.seen_end_activities(),
            set(["c"])
        )
        log = gen_log("a b c", "a b", "a", "d")
        self.assertEqual(log.seen_end_activities(),
            set(['c','b','a', 'd'])
        )

if __name__ == '__main__':
    unittest.main()

