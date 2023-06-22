"""
This module includes functions to quickly generate koalas 
event logs, traces, and events in both simple and complex forms.

Simple Form Objects
-------------------
gen_log\n
gen_trace\n

Complex Form Objects
--------------------
Coming soon...


Grammar
-------
<system> :: <log> | <domain> <log> | <log> <issue> | <domain> <log> <issue>

<log> :: [Patterns]{<nonzero>} <trace>
<trace> :: [ <event> ]{<nonzero>} | [<event>]{<nonzero>} <trace>
<event> :: <event> <event>| <word> | <word>{<data>}
<word> :: <ascii> | <ascii><word>
<data> :: <attr> | <attr>|<shift> | <data>,<data>
<attr> :: d_<alldigits>
<shift> :: <limit> | <lshift> | <rshift> | <mshift>
<lshift> :: <halfnumber>%-left
<rshift> :: <halfnumber>%-right 
<mshift> :: <halfnumber>%-m-<halfnumber>%
<limit> :: <<<number> | >><number>
<halfnumber> :: <halfdigits> | <halfdigits><halfdigits>
<number> :: <alldigits> | <number><number>
<nonzero> :: <nonzerodigits> | <nonzero><nonzero>
<alldigits> :: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 9 
<nonzerodigits> :: 1 | 2 | 3 | 4 | 5 | 6 | 8 | 9 
<halfdigits> :: 0 | 1 | 2 | 3 | 4 | 5
<ascii> :: a | b | c | ... | x | y | z ** any ascii symbol

<domain> :: [Domains] <atttribute>
<attribute> :: <attribute> <attribute> | <attr>-<type> | <attr>-<type>-<dist>
<type> :: int | float | string | bool
<dist> :: <disttype> | <disttype>-<number>
<disttype> :: normal | uniform


"""
from typing import Iterable,List
from enum import Enum
from abc import ABC,abstractmethod
from copy import deepcopy
from random import randint, choice

from pmkoalas.simple import EventLog, Trace


DEFAULT_DELIM=" "
DEFAULT_AUG_SPLIT = "||"
DEFAULT_MUT_AUG = "^"
DEFAULT_DATA_ISSUE_AUG = "%d"

class TraceGenerator():
    "Template for trace generator from delimited trace"

    def __init__(self, sequence:List) -> None:
        self._sequence = deepcopy(sequence)
        self._augments = list()

    def add_augmentor(self, augment:'TraceAugment') -> None:
        self._augments.append(augment)
        # keep augments in order
        self._augments = sorted(self._augments, 
            key=lambda x: x.ordering().value
        ) 

    def __call__(self) -> Iterable[Trace]:
        gen = [ deepcopy(self._sequence) ]
        for augment in self._augments:
            gen = augment.augment(gen)
        return [ Trace(seq) for seq in gen]

class AugmentOrder(Enum):
    FIRST = 1
    SECOND = 2 
    LAST = 5

class TraceAugment(ABC):
    """
    Template for trace augementor, which modifies the 
    resulting traces generated from the generator.
    """

    def __init__(self, order:AugmentOrder) -> None:
        self._order = order

    @abstractmethod
    def augment(self, seqs:Iterable[List[str]]) -> Iterable[List[str]]:
        """
        Applies the augmentation to each sequence given and 
        returns a new list.
        """
        pass

    def ordering(self) -> AugmentOrder:
        return self._order

class TraceMutAugment(TraceAugment):
    """
    This trace augment, mutiplies the number of traces produced
    by the given multiplier.
    ### FORM
    "a b c d e || ^5" where "^5" is translated produce 5 of 
    this trace.
    """

    def __init__(self, mut:int) -> None:
        super().__init__(AugmentOrder.FIRST)
        self._mut = mut 

    def augment(self, seqs:Iterable[List[str]]) -> Iterable[List[str]]:
        out = list()
        for seq in seqs:
            out += [ deepcopy(seq) for _ in range(self._mut)]
        return out

class TraceDataIssue(TraceAugment):
    """
    This trace augment will simulate a data issue occuring on
    any generated trace, where each trace has a X% chance to
    have one of the following data issues:\n
    - two labels in the sequence are swapped
    - a label is removed from the sequence
    - a label is changed into another label in the sequence
    ### FORM
    "a b c d e || %d[X|0-100]" is translated to produce a trace
    with a X% chance to have a data issue.
    """

    def __init__(self, chance:int) -> None:
        super().__init__(AugmentOrder.SECOND)
        if (chance > 100 or chance < 0):
            raise ValueError("Unable to roll for data issues" + 
                "with the given chance. Chance needs to be a int "+
                f"between 0 and 100 :: {chance}"
            )
        self._chance = chance

    def augment(self, seqs: Iterable[List[str]]) -> Iterable[List[str]]:
        out = list()
        for seq in seqs:
            nseq = deepcopy(seq)
            # roll for issue
            chance = randint(0, 100)
            if (chance <= self._chance):
                # work out the type of issue
                issue = randint(1,3)
                if issue == 1:
                    nseq = self._swap_labels(nseq)
                elif issue == 2:
                    nseq = self._remove_label(nseq)
                else:
                    nseq = self._change_label(nseq)
            # add back seqs 
            out.append(nseq)
        return out

    def _swap_labels(self, seq:List[str]) -> List[str]:
        choices = list(range(len(seq)))
        c1 = choice(choices)
        c2 = choice(choices)
        temp = seq[c2]
        seq[c2] = seq[c1]
        seq[c1] = temp
        return seq  

    def _remove_label(self, seq:List[str]) -> List[str]:
        choices = list(range(len(seq)))
        removed = choice(choices)
        _ = seq.pop(removed)
        return seq 

    def _change_label(self, seq:List[str]) -> List[str]:
        label_choices = list(set(seq))
        index_choices = list(range(len(seq)))
        index = choice(index_choices)
        label = choice(label_choices)
        seq[index] = label
        return seq 
### Top level API calls

def gen_trace(trace: str, delimiter=DEFAULT_DELIM) -> List[Iterable[str]]:
    """
    This function generates a (simple) Trace from a delimited trace,
    e.g. "a b c" or "a b c || ^100".
    """
    if (len(trace) < 1):
        return Trace(list())
    # check for augments
    seq = trace.split(delimiter)
    if (DEFAULT_AUG_SPLIT in seq):
        pivot = seq.index(DEFAULT_AUG_SPLIT)
        tseq = seq[:pivot]
        aseq = seq[pivot:]
        # setup generator
        generator = TraceGenerator(tseq)
        for aug in aseq[1:]:
            if aug[0] == DEFAULT_MUT_AUG:
                try:
                    mut = int(aug[1:])
                    augment = TraceMutAugment(mut) 
                    generator.add_augmentor(augment)
                except Exception:
                    raise ValueError("Unable to convert "+
                        f"multiplier to int :: {aug}"
                    )
            elif aug[:2] == DEFAULT_DATA_ISSUE_AUG:
                try: 
                    chance = int(aug[2:])
                    augment = TraceDataIssue(chance)
                    generator.add_augmentor(augment)
                except ValueError as e:
                    raise e 
                # except Exception:
                #     raise ValueError("Unable to convert chance " +
                #         f"to a int :: '{aug[2:]}'"
                #     )
        return generator()
    else:
        return [Trace(seq)]

def gen_log(*traces: Iterable[str], delimiter=DEFAULT_DELIM) -> EventLog:
    """
    This function generates an (simple) event log from a collection
    of delimited traces, e.g. ["a b", "a c", "a b d"].\n
    Exemplar uses consist of:\n
    `convert("a b c", "a b", "a")`\n
    `convert(*[ t for t in traces])`\n

    More advanced usages:\n
    multiply a sequence, five times: `"a b c || ^5"`\n
    having 50% chance to cause a data issue: `"a b c d e || %d50"`\n
    """
    return EventLog( [ 
        t 
        for gens in map( gen_trace, traces )
        for t in gens
    ] )

