import unittest

from pmkoalas.simple import Trace, EventLog
from pmkoalas.dtlog import convert

from pmkoalas.conformance.matching import Path, Skipper, cost_of_path
from pmkoalas.conformance.matching import find_least_costy_paths
from pmkoalas.conformance.matching import ManyMatching, ExpontentialPathWeighter
from pmkoalas.conformance.matching import construct_many_matching

from pmkoalas.models.transitiontree import TransitionTreeRoot
from pmkoalas.models.transitiontree import TransitionTreeVertex
from pmkoalas.models.transitiontree import TransitionTreeFlow
from pmkoalas.models.transitiontree import TransitionTree

# dummy tree
TROOT = TransitionTreeRoot()
TVERTS = [
    TROOT,
    TransitionTreeVertex(2,Trace(["a"])),
    TransitionTreeVertex(3,Trace(["a", "b"])),
    TransitionTreeVertex(4,Trace(["a", "c"])),
    TransitionTreeVertex(5,Trace(["a", "d"])),
    TransitionTreeVertex(6,Trace(["a", "d", "e"]),end=True),
    TransitionTreeVertex(7,Trace(["a", "d", "f"]),end=True),
    TransitionTreeVertex(8,Trace(["a", "c", "e"]),end=True),
    TransitionTreeVertex(9,Trace(["a", "b", "z"]),end=True),
]
TFLOWS = [
    TransitionTreeFlow(
        TVERTS[0], "a", TVERTS[1]
    ),
    TransitionTreeFlow(
        TVERTS[1], "b", TVERTS[2]
    ),
    TransitionTreeFlow(
        TVERTS[1], "c", TVERTS[3]
    ),
    TransitionTreeFlow(
        TVERTS[1], "d", TVERTS[4]
    ),
    TransitionTreeFlow(
        TVERTS[4], "e", TVERTS[5]
    ),
    TransitionTreeFlow(
        TVERTS[4], "f", TVERTS[6]
    ),
    TransitionTreeFlow(
        TVERTS[3], "e", TVERTS[7]
    ),
    TransitionTreeFlow(
        TVERTS[2], "z", TVERTS[8]
    ),
]
DUMMY_TREE = TransitionTree(
    set(TVERTS),
    TROOT,
    set(TFLOWS)
)

# testing variants and logs
blank_path = Path([])
skipper_path = Path([Skipper(),Skipper(),Skipper()])
variant_one = Trace(["a","e","f"])
vpath_one = Path([
    Skipper(),
    TFLOWS[0],
    TFLOWS[2]
])
vpath_two = Path([
    TFLOWS[0],
    TFLOWS[3],
    TFLOWS[5]
])
variant_two = Trace(["a","d","f"])
variant_three = Trace(["z","a","c"])

class MatchingTests(unittest.TestCase):

    def test_cost_of_path(self):
        self.assertEqual(
            cost_of_path(blank_path, variant_one),
            4
        )
        self.assertEqual(
            cost_of_path(skipper_path, variant_one),
            7
        )
        self.assertEqual(
            cost_of_path(vpath_one, variant_one),
            5
        )
        self.assertEqual(
            cost_of_path(vpath_two, variant_one),
            1
        )
        self.assertEqual(
            cost_of_path(vpath_two, variant_two),
            0
        )

    def test_find_least_costy(self):
        self.assertEqual(
            find_least_costy_paths(
                set([blank_path,skipper_path,vpath_one,vpath_two]),
                variant_two
            ),
            set([vpath_two])
        ) 

    def test_construction(self):
        try :
            matcher = construct_many_matching(
                EventLog([variant_one,variant_two,variant_three]),
                DUMMY_TREE
            )
        except Exception as e:
            self.fail("Failed to construct many matching :: "+str(e))

    def test_subdistribution(self):
        matcher = construct_many_matching(
                EventLog([variant_one,variant_two,variant_three]),
                DUMMY_TREE
            ) 
        # test that for variant one and three we have a subdistribution
        # when using the weighter
        cands = matcher[variant_one]
        weighter = ExpontentialPathWeighter(cands)
        wsum = sum([ weighter(cand, variant_one) for cand in cands])
        self.assertLess(wsum, 1.0)
        cands = matcher[variant_three]
        weighter = ExpontentialPathWeighter(cands)
        wsum = sum([ weighter(cand, variant_three) for cand in cands])
        self.assertLess(wsum, 1.0)

    def test_fulldistribution(self):
        matcher = construct_many_matching(
                EventLog([variant_one,variant_two,variant_three]),
                DUMMY_TREE
            ) 
        # test that for variant two, we have a full-distribution
        # when using the weighter
        cands = matcher[variant_two]
        weighter = ExpontentialPathWeighter(cands)
        wsum = sum([ weighter(cand, variant_two) for cand in cands])
        self.assertEqual(wsum, 1.0)