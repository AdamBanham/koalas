import unittest
from pmkoalas._struct import OutOfMemoryQueue, OutOfMemorySet
from pmkoalas.conformance.tokenreplay import PetriNetFiringSequence
from pmkoalas.models.petrinet import parse_pnml_for_dpn
from pmkoalas._logging import info

class TokenplayTestWithNoMem(unittest.TestCase):

    def test_queue(self):

        model = parse_pnml_for_dpn("tests/conformance/test_dpn_a.pnml")
        initial_marking = model.initial_marking
        final_marking = model.final_marking
        max_length = 5

        completed = OutOfMemorySet()
        incomplete = OutOfMemoryQueue()
        incomplete.append(
            PetriNetFiringSequence(initial_marking, list(), final_marking)
        )
        seen = OutOfMemorySet()
        while len(incomplete) > 0:
            tmp = OutOfMemoryQueue()
            for select in incomplete:
                for firing in select.next():
                    pot = select.fire(firing)
                    if len(pot) <= max_length:
                        tmp.append(pot)
            incomplete = OutOfMemoryQueue()
            for pot in tmp:
                if pot not in seen:
                    if pot.reached_final():
                        completed.add(pot)
                    else:
                        incomplete.append(pot)
                    seen.add(pot)
        info(f"Completed: {len(completed)}")
        info(f"Incomplete: {len(incomplete)}")
        info(f"Seen: {len(seen)}")
