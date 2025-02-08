import unittest

from pmkoalas.conformance.alignments import AlignmentMove, AlignmentMoveType
from pmkoalas.conformance.alignments import Alignment

from pmkoalas.models.pnfrag import parse_net_fragments
from pmkoalas.complex import ComplexEvent, ComplexTrace
from pmkoalas.models.petrinet import Transition, Place

class AlignmentsTest(unittest.TestCase):

    def test_move_types(self):
        move = AlignmentMove(
            AlignmentMoveType.LOG,
            None,
            "A",
            None, 
            None
        )
        self.assertTrue(move.is_log())
        move = AlignmentMove(
            AlignmentMoveType.MODEL,
            None,
            "A",
            None, 
            None
        )
        self.assertTrue(move.is_model())
        move = AlignmentMove(
            AlignmentMoveType.SYNC,
            None,
            "A",
            None, 
            None
        )
        self.assertTrue(move.is_sync())

    def test_move_getlog(self):
        move = AlignmentMove(
            AlignmentMoveType.LOG,
            None,
            "A",
            None, 
            None
        )
        self.assertEqual(move.get_event(), ComplexEvent("A", dict()))
        move = AlignmentMove(
            AlignmentMoveType.SYNC,
            None,
            "A",
            None, 
            None
        )
        self.assertEqual(move.get_event(), ComplexEvent("A", dict()))
        move = AlignmentMove(
            AlignmentMoveType.MODEL,
            None,
            None,
            None, 
            None
        )
        with self.assertRaises(ValueError):
            move.get_event()
        

    def test_move_getmodel(self):
        trans = Transition("A")
        move = AlignmentMove(
            AlignmentMoveType.MODEL,
            trans,
            "A",
            None, 
            None
        )
        self.assertEqual(move.get_transition(), trans)
        move = AlignmentMove(
            AlignmentMoveType.SYNC,
            trans,
            "A",
            None, 
            None
        )
        self.assertEqual(move.get_transition(), trans)
        move = AlignmentMove(
            AlignmentMoveType.LOG,
            None,
            "A",
            None, 
            None
        )
        with self.assertRaises(ValueError):
            move.get_transition()

    def test_alignment(self):
        net = parse_net_fragments("foobar",
            "i -> [B] -> p1 -> [C] -> s"                
        )
        net.set_initial_marking({
            Place("i", 1) : 1
        })
        net.set_final_marking({
            Place("s", 5) : 1
        })
        transB = [ t for t in net.transitions if t.name == "B" ][0]
        transC = [ t for t in net.transitions if t.name == "C" ][0]
        moves = [
            AlignmentMove(
                AlignmentMoveType.LOG,
                None,
                "A",
                net.initial_marking, 
                None
            ),
            AlignmentMove(
                AlignmentMoveType.MODEL,
                transB,
                "B",
                net.initial_marking, 
                None
            ),
            AlignmentMove(
                AlignmentMoveType.SYNC,
                transC,
                "C",
                net.initial_marking.remark(transB), 
                None
            ),
        ]

        ali = Alignment(moves)

        self.assertEqual(ali.moves(), moves)
        self.assertEqual(ali.projected_path(), [transB, transC])
        self.assertEqual(ali.projected_trace(), ["A", "C"])

        trace = ComplexTrace(
            [ ComplexEvent("A", dict(
                {"y": "bar"}
            )),
              ComplexEvent("C", dict(
                  {"x": 1}
              ))],
            dict()
        )

        expected = [
            ComplexEvent("A", dict(
                {}
            )),
             ComplexEvent("missing", dict(
                {"y": "bar"}
            )),
            ComplexEvent("C", dict(
                {"y": "bar"}
            ))
        ]
        actual = ali.contextualise(trace)
        actualD = [ m.state for m in actual ]
        self.assertEqual(actualD, expected)

