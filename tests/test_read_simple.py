import unittest
from os import path 

from koalas.read import read_xes_simple
from koalas.simple import EventLog,Trace

SSMALL = path.join(".","tests","small_01.xes")
WSMALL = path.join(".","tests","small_02.xes")
OSMALL = path.join(".","tests","small_03.xes")

class DTLogTest(unittest.TestCase):

    def test_successful_read(self):
        try:
            log = read_xes_simple(SSMALL, debug=False) 
        except:
            self.fail("Failed to parse log")

        real_log = EventLog( [
                Trace(["A","B","C","D","E"]),
                Trace(["A","B","C","D","E"]),
                Trace(["A","B","C","D","D"]),
                Trace(["A","A","A","B","E"]),
                Trace(["A","B","C","E","E"]),
            ])
        self.assertEqual(log, real_log)

    def test_unsucessful_read(self):
        try:
            log = read_xes_simple(WSMALL, debug=False)
        except:
            return
        self.fail()

    def test_unsuccessful_label_change(self):
        try:
            log = read_xes_simple(SSMALL, label_attribute="foo:bah", debug=False) 
        except:
            return 
        self.fail("Should fail when label attribute is not found!")

    def test_label_change(self):
        try:
            log = read_xes_simple(OSMALL, label_attribute="name", debug=False) 
        except:
            self.fail("Failed to parse log after changing label attribute!")

        real_log = EventLog( [
                Trace(["E","D","C","B","A"]),
                Trace(["E","D","C","B","A"]),
                Trace(["D","D","C","B","A"]),
                Trace(["E","B","A","A","A"]),
                Trace(["E","E","C","B","A"]),
            ])
        self.assertEqual(log, real_log)

    def test_unsucessful_sort_change(self):
        try:
            log = read_xes_simple(SSMALL, sort_attribute="foo:bah", debug=False) 
        except:
            return 
        self.fail("Should fail when sort attribute is not found!")


if __name__ == '__main__':
    unittest.main()