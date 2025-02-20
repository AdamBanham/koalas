import unittest

from pmkoalas.models.pnfrag import parse_net_fragments
from pmkoalas.simple import Trace
from pmkoalas._logging import setLevel, info
from logging import INFO,ERROR
from pmkoalas.models.petrinets.pn import Place, LabelledPetriNet
from pmkoalas.models.petrinets.pn import AcceptingPetriNet, PetriNetMarking
from pmkoalas.models.petrinets.pn import get_execution_semantics
from pmkoalas.conformance.tokenreplay import generate_traces_from_lpn

test_lpn = parse_net_fragments(
    "test_lpn_seq",
    "I__1 -> [A] -> p1__2 -> [B] -> p2__3 -> [C] -> F__4"
)
test_lpn = AcceptingPetriNet(
    test_lpn,
    PetriNetMarking({Place("I", 1):1}),
    [PetriNetMarking({Place("F",4):1})]
)
test_lpn_par = parse_net_fragments(
    "test_lpn_par",
    "I__1 -> [A] -> p1__2 -> [B] -> p2__3 -> [C] -> F__4",
    "I__1 -> [A] -> p5__5 -> [D] -> p6__6 -> [C] -> F__4"
)
test_lpn_par = AcceptingPetriNet(
    test_lpn_par,
    PetriNetMarking({Place("I", 1):1}),
    [PetriNetMarking({Place("F",4):1})]
)

class MatchingTests(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        
    def tearDown(self) -> None:
        super().tearDown()

    def test_generate_max_len(self):
        exnet = get_execution_semantics(test_lpn)
        log = generate_traces_from_lpn(exnet, 3)
        self.assertEqual(1,len(log))
        self.assertEqual(set([Trace(["A","B","C"])]), log.language())
        log = generate_traces_from_lpn(exnet, 3, True)
        self.assertEqual(set([Trace(["A","B","C"])]), log.language())
        log = generate_traces_from_lpn(exnet, 2)
        self.assertEqual(set([Trace(["A","B",])]), log.language())
        log = generate_traces_from_lpn(exnet, 2, strict=True)
        self.assertEqual(set(), log.language())

    def test_parallel_gen(self):
        exnet = get_execution_semantics(test_lpn_par)
        log = generate_traces_from_lpn(exnet, 4)
        self.assertEqual(2,len(log))
        self.assertEqual(
            set([Trace(['A','D','B','C']), Trace(['A','B','D','C'])]),
            log.language()
        )
