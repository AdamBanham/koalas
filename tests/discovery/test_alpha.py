import unittest
from copy import deepcopy

from pmkoalas.discovery.alpha_miner import AlphaMinerInstance
from pmkoalas.discovery.alpha_miner import AlphaRelation,AlphaPair
from pmkoalas.discovery.alpha_miner import AlphaPlace,AlphaFlowRelation
from pmkoalas.discovery.alpha_miner import AlphaTransition
from pmkoalas.discovery.alpha_miner import AlphaSinkPlace,AlphaStartPlace
from pmkoalas.models.petrinet import Place,Transition,Arc
from pmkoalas.dtlog import convert

# simple log tests
LOG = convert( 
            "a b d",
            "a c d",
            "a b",
            "a c",
            "a b d e b d",
            "a c d e c d"
        )
START_ACTS = set(["a"])
END_ACTS = set(["d", "b", "c"])
ACTS = set(["a", "b", "c", "d", "e"])
MATRIX = { 
    "a" : {
        "a" : AlphaRelation("a","a",[]),
        "b" : AlphaRelation("a","b",[("a","b")]),
        "c" : AlphaRelation("a","c",[("a","c")]),
        "d" : AlphaRelation("a","d",[]),
        "e" : AlphaRelation("a","e",[])
    },
    "b" : {
        "a" : AlphaRelation("b","a",[("a","b")]),
        "b" : AlphaRelation("b","b",[]),
        "c" : AlphaRelation("b","c",[]),
        "d" : AlphaRelation("b","d",[("b","d")]),
        "e" : AlphaRelation("b","e",[("e","b")])
    },
    "c" : {
        "a" : AlphaRelation("c","a",[("a","c")]),
        "b" : AlphaRelation("c","b",[]),
        "c" : AlphaRelation("c","c",[]),
        "d" : AlphaRelation("c","d",[("c","d")]),
        "e" : AlphaRelation("c","e",[("e","c")])
    },
    "d" : {
        "a" : AlphaRelation("d","a",[]),
        "b" : AlphaRelation("d","b",[("b","d")]),
        "c" : AlphaRelation("d","c",[("c","d")]),
        "d" : AlphaRelation("d","d",[]),
        "e" : AlphaRelation("d","e",[("d","e")])
    },
    "e" : {
        "a" : AlphaRelation("e","a",[]),
        "b" : AlphaRelation("e","b",[("e","b")]),
        "c" : AlphaRelation("e","c",[("e","c")]),
        "d" : AlphaRelation("e","d",[("d","e")]),
        "e" : AlphaRelation("e","e",[])
    }
}

# following p173 and L5 in Process Mining (2016;2ND ED)
BOOK_LOG = convert( 
    "a b e f",
    "a b e f",
    "a b e c d b f",
    "a b e c d b f",
    "a b e c d b f",
    "a b c e d b f",
    "a b c e d b f",
    "a b c d e b f",
    "a b c d e b f",
    "a b c d e b f",
    "a b c d e b f",
    "a e b c d b f",
    "a e b c d b f",
    "a e b c d b f",
)
BOOK_TL = set(["a", "b", "c", "d", "e", "f"])
BOOK_TL_OUT = set([ AlphaTransition(t) for t in BOOK_TL])
BOOK_TI = set(["a"])
BOOK_TO = set(["f"])
BOOK_XL = set([ 
    AlphaPair(set(["a"]),set(["b"])),
    AlphaPair(set(["a"]), set(["e"])),
    AlphaPair(set(["b"]), set(["c"])),
    AlphaPair(set(["b"]), set(["f"])),
    AlphaPair(set(["c"]), set(["d"])),
    AlphaPair(set(["d"]), set(["b"])),
    AlphaPair(set(["e"]), set(["f"])),
    AlphaPair(set(["a","d"]), set(["b"])),
    AlphaPair(set(["b"]), set(["c","f"])),
])
BOOK_YL = [
    AlphaPair(set(["a"]), set(["e"])),
    AlphaPair(set(["c"]), set(["d"])),
    AlphaPair(set(["e"]), set(["f"])),
    AlphaPair(set(["a","d"]), set(["b"])),
    AlphaPair(set(["b"]), set(["c","f"])),
]
BOOK_PL = [ 
    AlphaPlace(BOOK_YL[0].__str__(), BOOK_YL[0].left, BOOK_YL[0].right),
    AlphaPlace(BOOK_YL[1].__str__(), BOOK_YL[1].left, BOOK_YL[1].right),
    AlphaPlace(BOOK_YL[2].__str__(), BOOK_YL[2].left, BOOK_YL[2].right),
    AlphaPlace(BOOK_YL[3].__str__(), BOOK_YL[3].left, BOOK_YL[3].right),
    AlphaPlace(BOOK_YL[4].__str__(), BOOK_YL[4].left, BOOK_YL[4].right),
    AlphaStartPlace(),
    AlphaSinkPlace(),
]
BOOK_FL = set([ 
    AlphaFlowRelation("1", AlphaTransition("a"), BOOK_PL[0]),
    AlphaFlowRelation("2", BOOK_PL[0], AlphaTransition("e")),
    AlphaFlowRelation("3", AlphaTransition("c"), BOOK_PL[1]),
    AlphaFlowRelation("4", BOOK_PL[1], AlphaTransition("d")),
    AlphaFlowRelation("5", AlphaTransition("e"), BOOK_PL[2]),
    AlphaFlowRelation("6", BOOK_PL[2], AlphaTransition("f")),
    AlphaFlowRelation("7", AlphaTransition("a"), BOOK_PL[3]),
    AlphaFlowRelation("8", AlphaTransition("d"), BOOK_PL[3]),
    AlphaFlowRelation("9", BOOK_PL[3], AlphaTransition("b")),
    AlphaFlowRelation("10", AlphaTransition("b"), BOOK_PL[4]),
    AlphaFlowRelation("11", BOOK_PL[4], AlphaTransition("c")),
    AlphaFlowRelation("12", BOOK_PL[4], AlphaTransition("f")),
    AlphaFlowRelation("13", BOOK_PL[5], AlphaTransition("a")),
    AlphaFlowRelation("14", AlphaTransition("f"), BOOK_PL[6]),    
])
BOOK_YL = set(BOOK_YL)
BOOK_PL = set(BOOK_PL)
BOOK_LPN_PL = set([
    Place(p.name) 
    for p
    in BOOK_PL
])
BOOK_LPN_TL = set([
    Transition(t)
    for t in BOOK_TL
])
place_nodes = dict( 
    (p.name, p)
    for p in BOOK_LPN_PL
)
transition_nodes = dict(
    (t.name, t)
    for t in BOOK_LPN_TL
)
BOOK_LPN_FL = set([
    Arc(place_nodes[f.src.name], transition_nodes[f.tar.name])
    if isinstance(f.src, AlphaPlace) else
    Arc(transition_nodes[f.src.name], place_nodes[f.tar.name])
    for f in BOOK_FL
])

class SingleThreadAlphaTest(unittest.TestCase):

    def setUp(self):
        self.miner = AlphaMinerInstance()

    def test_alpha_pair_hash(self):
        pair = AlphaPair(set(["a"]), set(["b"]))
        self.assertEqual(hash(pair), hash(pair))

    def test_alpha_pair_hash_in_set(self):
        tester = set()
        pair = AlphaPair(set(["a", "d"]), set(["b"]))
        tester.add(pair)
        self.assertEqual(1, len(tester))
        pair = AlphaPair(set(["d", "a"]), set(["b"]))
        tester.add(pair)
        self.assertEqual(1, len(tester))
        o_tester = set()
        o_tester.add(pair)
        tester.update(o_tester)
        self.assertEqual(1, len(tester))

    def test_creation(self):
        miner = AlphaMinerInstance(min_inst=5)
        miner = AlphaMinerInstance()
        miner = deepcopy(miner)

    def test_footprint_matrix(self):
        miner = self.miner
        matrix = miner.mine_footprint_matrix(LOG)
        # test that footprint matrix has the right follows
        # test that footprint matrix has the right relations
        for col in ACTS:
            for row in ACTS:
                crelation = matrix[col][row]
                rrelation = MATRIX[col][row]
                # test one
                self.assertEqual(crelation._follows, 
                    rrelation._follows,
                    "computed and expected follows differ :: "+
                    f"{crelation._follows} vs {rrelation._follows}"
                )
                # test two
                self.assertEqual(crelation.relation(), 
                    rrelation.relation(),
                    "computed and expected alpha relation differ :: "+
                    f"{crelation} vs {rrelation}"
                )


    def test_step_one(self):
        # simple test
        miner = self.miner
        out = miner._step_one(LOG)
        self.assertEqual(out, ACTS)

        # following p173 and L5 in Process Mining (2016;2ND ED)
        out = miner._step_one(BOOK_LOG)
        self.assertEqual(out, BOOK_TL)

    def test_step_two(self):
        # simple test
        miner = self.miner
        out = miner._step_two(LOG)
        self.assertEqual(out, START_ACTS)  

        # following p173 and L5 in Process Mining (2016;2ND ED)
        out = miner._step_two(BOOK_LOG)
        self.assertEqual(out, BOOK_TI)

    def test_step_three(self):
        # simple test
        miner = self.miner
        out = miner._step_three(LOG)
        self.assertEqual(out, END_ACTS) 

        # following p173 and L5 in Process Mining (2016;2ND ED)
        out = miner._step_three(BOOK_LOG)
        self.assertEqual(out, BOOK_TO)

    def test_step_four(self):
        miner = self.miner
        # following p173 and L5 in Process Mining (2016;2ND ED) 
        out = miner._step_four(BOOK_LOG)
        self.assertEqual(out, BOOK_XL)
         

    def test_step_five(self):
        miner = self.miner
        # following p173 and L5 in Process Mining (2016;2ND ED) 
        out = miner._step_five(BOOK_LOG, BOOK_XL)
        self.assertEqual(out, BOOK_YL) 

    def test_step_six(self):
        miner = self.miner
        # following p173 and L5 in Process Mining (2016;2ND ED) 
        out = miner._step_six(BOOK_XL, BOOK_YL)
        self.assertEqual(out, BOOK_PL) 

    def test_step_seven(self):
        miner = self.miner
        # following p173 and L5 in Process Mining (2016;2ND ED) 
        out = miner._step_seven(BOOK_LOG, BOOK_PL, BOOK_TI, BOOK_TO)
        self.assertEqual(out, BOOK_FL) 

    def test_mine(self):
        miner = self.miner
        # following p173 and L5 in Process Mining (2016;2ND ED) 
        net = miner.discover(BOOK_LOG)
        for p in net.places:
            found_match = False
            for o in BOOK_LPN_PL:
                if p.name == o.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Place ({p}) not found in expected places :\n{BOOK_LPN_PL}")
        for t in net.transitions:
            found_match = False
            for o in BOOK_LPN_TL:
                if t.name == t.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Transition ({t}) not found in expected transitions :\n{BOOK_LPN_TL}")
        for a in net.arcs:
            found_match = False
            for o in BOOK_LPN_FL:
                if o.from_node.name == a.from_node.name and o.to_node.name == a.to_node.name:
                    found_match = True
                    break
            self.assertTrue(found_match, 
                f"Arc ({a}) not found in expected arcs :\n{BOOK_LPN_FL}")
            
class OptimisedAlphaTest(SingleThreadAlphaTest):
    """
    Reuse the tests from SingleThreadAlphaTest to test that the optimised
    version returns the same results.
    """

    def setUp(self):
        from pmkoalas._logging import setLevel
        from logging import INFO
        self.miner = AlphaMinerInstance(optimised=True)

    def tearDown(self) -> None:
        from pmkoalas._logging import setLevel
        from logging import ERROR
        setLevel(ERROR)
