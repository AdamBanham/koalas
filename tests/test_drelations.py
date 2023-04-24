import unittest
from logging import DEBUG

from pmkoalas.dtlog import convert
from pmkoalas.directly import DirectlyFollowPair as DFPair, FollowLanguage
from pmkoalas.directly import DIRECTLY_END,DIRECTLY_SOURCE
from pmkoalas.simple import EventLog

empty_lang = convert()

simple_lang = convert(
    "a b c",
    "a b c",
    "a d c"
)
simple_pairs = [ 
    DFPair(DIRECTLY_SOURCE, "a", 3),
    DFPair("a", "b", 2),
    DFPair("a", "d", 1),
    DFPair("b", "c", 2),
    DFPair("d", "c", 1),
    DFPair("c", DIRECTLY_END, 3),
]

many_starts = convert(
    "a e",
    "b e",
    "c e",
    "d e"
)
many_starts_pairs = [ 
    DFPair(DIRECTLY_SOURCE, "a", 1),
    DFPair(DIRECTLY_SOURCE, "b", 1),
    DFPair(DIRECTLY_SOURCE, "c", 1),
    DFPair(DIRECTLY_SOURCE, "d", 1),
    DFPair("a", "e", 1),
    DFPair("b", "e", 1),
    DFPair("c", "e", 1),
    DFPair("d", "e", 1),
    DFPair("e", DIRECTLY_END, 4),
]

many_ends = convert(
    "a b",
    "a c",
    "a d",
    "a e"
)
many_ends_pairs = [ 
    DFPair(DIRECTLY_SOURCE, "a", 4),
    DFPair("a", "b", 1),
    DFPair("a", "c", 1),
    DFPair("a", "d", 1),
    DFPair("a", "e", 1),
    DFPair("b", DIRECTLY_END, 1),
    DFPair("c", DIRECTLY_END, 1),
    DFPair("d", DIRECTLY_END, 1),
    DFPair("e", DIRECTLY_END, 1),
]

empty_traces_lang = convert(
    "a b c",
    "a b c",
    "a d c",
    "",
    "",
    ""
)
empty_traces_pairs = [ 
    DFPair(DIRECTLY_SOURCE, "a", 3),
    DFPair("a", "b", 2),
    DFPair("a", "d", 1),
    DFPair("b", "c", 2),
    DFPair("d", "c", 1),
    DFPair("c", DIRECTLY_END, 3),
]

addition_pairs = [ 
    DFPair(DIRECTLY_SOURCE, "a", 6),
    DFPair("a", "b", 4),
    DFPair("a", "d", 2),
    DFPair("b", "c", 4),
    DFPair("d", "c", 2),
    DFPair("c", DIRECTLY_END, 6),
]

class DTLogTest(unittest.TestCase):


    def check_flow_lang(self,log:EventLog,size:int,pairs, 
     debug=False):
        try:
            # check for computable and size
            flang = log.directly_follow_relations(debug=debug,
             debug_level=DEBUG) 
            self.assertEqual(len(flang), size, 
             f"expected language to be of size {size}")
            # check pairs
            self.check_directly_pairs(flang, pairs) 
        except Exception:
            self.fail()  

    def check_directly_pairs(self,flang:FollowLanguage, pairs):
        # check pairs
        computed_pairs = list(flang._relations.values())
        for pair in pairs:
            self.assertTrue(pair in pairs, f"missing pair :: {pair}")
            val = computed_pairs.index(pair)
            val = computed_pairs[val]
            self.assertTrue(val.frequency() == pair.frequency(), 
                f"{pair} :: expected frequency of {pair.frequency()}" \
                + f", but got {val.frequency()}") 

    def test_empty_lang(self):
        try:
            flang = empty_lang.directly_follow_relations()
            self.assertEqual(len(flang), 0, 
            "expected language to be empty")
        except Exception:
            self.fail()

    def test_simple_lang(self):
        self.check_flow_lang(simple_lang, 6 , simple_pairs)

    def test_many_starts(self):
        self.check_flow_lang(many_starts, len(many_starts_pairs),
         many_starts_pairs) 

    def test_many_ends(self):
        self.check_flow_lang(many_ends, len(many_ends_pairs),
         many_ends_pairs) 

    def test_empty_traces(self):
        self.check_flow_lang(empty_traces_lang, len(empty_traces_pairs),
         empty_traces_pairs)  

    def test_addition(self):
        flang = simple_lang.directly_follow_relations()
        double_flang = flang + flang
        self.check_directly_pairs(double_flang, addition_pairs) 