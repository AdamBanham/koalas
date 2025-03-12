import unittest
from os import path 
from datetime import datetime

from pmkoalas.read import read_xes_simple,read_xes_complex
from pmkoalas.simple import EventLog,Trace
from pmkoalas.complex import ComplexEventLog, ComplexTrace, ComplexEvent
from pmkoalas._logging import info

SSMALL = path.join(".","tests","small_01.xes")
WSMALL = path.join(".","tests","small_02.xes")
OSMALL = path.join(".","tests","small_03.xes")
DSMALL = path.join(".","tests","small_04.xes")

class DTLogTest(unittest.TestCase):

    def test_successful_read(self):
        try:
            log = read_xes_complex(SSMALL) 
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
            log = read_xes_complex(WSMALL)
        except:
            return
        self.fail()

    def test_unsuccessful_label_change(self):
        try:
            log = read_xes_complex(SSMALL, label_attribute="foo:bah") 
        except:
            return 
        self.fail("Should fail when label attribute is not found!")

    def test_label_change(self):
        try:
            log = read_xes_complex(OSMALL, label_attribute="name") 
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

    def test_data_mappings(self):
        try:
            log = read_xes_complex(DSMALL) 
        except:
            self.fail("Failed to parse log")

        real_log = ComplexEventLog(
            [ 
                ComplexTrace( 
                    [ 
                        ComplexEvent(
                            'A',
                            {
                                'time:timestamp' : datetime.fromisoformat("2122-01-01T01:00:00.000+10:00"),
                                'res' : 0,
                                'life' : False,
                            }
                        ),
                        ComplexEvent(
                            'B',
                            {
                                'time:timestamp' : datetime.fromisoformat("2122-01-01T02:00:00.000+10:00"),
                                'res' : 1,
                                'cost:life' : 0.246,
                                'life' : False,
                            }
                        ),
                        ComplexEvent(
                            'C',
                            {
                                'time:timestamp' : datetime.fromisoformat("2122-01-01T03:00:00.000+10:00"),
                                'res' : 1,
                                'life' : True
                            }
                        )
                    ],
                    data = { 'concept:name' : 'trace_01', 'trace:cost' : 10}
                )
            ],
            data= {'concept:name' : 'A simple complex log',
                   'extracted' : datetime.fromisoformat("2122-01-05T01:00:00.000+10:00"),
                   'exporter:ver' : 1,
                   'percent:life' : 0.754,
                   'life' : True }
        )
        self.maxDiff = None
        self.assertEqual(log.__repr__(), real_log.__repr__())

    def nottest_read_bad(self):
        with self.failUnlessRaises(Exception): 
            log = read_xes_complex(path.join(".","tests","small_bad.xes")) 
            info(f"{log}")

if __name__ == '__main__':
    unittest.main()

