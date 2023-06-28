"""
This module includes functions to quickly generate event logs, traces, and 
events in both simple and complex forms. The simple form functions allow for 
mutation of strings based on some simple augmentations, and are very similar
to the dtlog options.

The complex form functions are design tools for generating an event log from a 
grammar and allow for many more augmentations. These are mainly aimed at users 
that wish to include some decision making based on data within the log, but 
do not wish to explicitly code this relationship. 

Simple Form Objects
-------------------
generate_log\n
generate_trace\n

Complex Form Objects
--------------------
generate_from_grammar\n
"""
from typing import Iterable,List, Union
from enum import Enum
from abc import ABC,abstractmethod
from copy import deepcopy
from random import randint, choice, random, normalvariate, uniform
from statistics import NormalDist
from string import ascii_lowercase

from pmkoalas.simple import EventLog, Trace
from pmkoalas.complex import ComplexEventLog, ComplexTrace, ComplexEvent
from pmkoalas.grammars.complex_logs import ComplexLogParser, ComplexLogParse
from pmkoalas import __version__
from pmkoalas._logging import enable_logging, debug

### Simple form functions
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
    This trace augment, mutiplies the number of traces produced by the given 
    multiplier.
    ### FORM
    "a b c d e || ^5" where "^5" is translated to produce 5 of this trace.
    """

    def __init__(self, mut:int) -> None:
        super().__init__(AugmentOrder.FIRST)
        self._mut = mut 

    def augment(self, seqs:Iterable[List[str]]) -> Iterable[List[str]]:
        out = list()
        for seq in seqs:
            out += [ deepcopy(seq) for _ in range(self._mut)]
        return out

class DataIssueImpossible(Exception):
    """
    An exception that is raised when we are unable to generate a data issue,
    using the given pattern. Usually occurs when the trace length is one, or that
    the number of unique process attributes is one.
    """
    pass

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
            if (len(nseq) < 2 or len(set(nseq)) < 2):
                    raise DataIssueImpossible()
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
        while c2 == c1:
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
        while seq[index] == label:
            label = choice(label_choices)
        seq[index] = label
        return seq 
### Top level API calls

def generate_trace(trace: str, delimiter=DEFAULT_DELIM) -> List[Iterable[str]]:
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

def generate_log(*traces: Iterable[str], delimiter=DEFAULT_DELIM) -> EventLog:
    """
    This function generates an (simple) event log from a collection
    of delimited traces, e.g. ["a b", "a c", "a b d"]. However, in contrast to, 
    `pmkoalas.dtlog.convert`, this function allows for some simple augments to 
    variants.\n
    Exemplar use cases:\n
    - multiplying a sequence by a factor, e.g. five times: `"a b c || ^5"`\n
    - having 50% chance to cause a data issue: `"a b c d e || %d50"`\n
    - generating five traces, each with 25% chance of an issue: 
    `"a b c d e ||^5 %d25"`
    """
    return EventLog( [ 
        t 
        for gens in map( generate_trace, traces )
        for t in gens
    ] )

class GenerationIssue(Exception):
    pass

### Complex form functions
class PesudoGenerator(ABC):

    @abstractmethod
    def generate(self) -> object:
        """
        Generates the object from the grammar parsing.
        """

class PesudoEvent(PesudoGenerator):

    
    class SupportedShifters(Enum):
        left = 1
        right = 2
        mid = 3

        @classmethod
        def find_type(self, parsed) -> 'SupportedShifters':
            for shifter in self:
                if shifter.name == parsed:
                    return shifter 
            raise GenerationIssue(f"Unknown shifter presented :: '{parsed}'")
        
    class Shifter():

        def __init__(self, shift, amount) -> None:
            self._shift = shift 
            if (self.is_mid()):
                self.left = amount[0]
                self.right = amount[1]
            else:
                self.amount = amount

        def is_left(self):
            return self._shift == PesudoEvent.SupportedShifters.left
        
        def is_right(self):
            return self._shift == PesudoEvent.SupportedShifters.right
        
        def is_mid(self):
            return self._shift == PesudoEvent.SupportedShifters.mid

    def __init__(self, domain:'PesudoDomain', template) -> None:
        self._domain = domain 
        self._template = template 

    def generate(self) -> ComplexEvent:
        mapping = {}
        for var in self._template['vars']:
            vname = var['name']
            if (var['shift'] != None):
                shift = self.SupportedShifters.find_type(var['shift']['typer'])
                if "amount" in var['shift']:
                    shift = self.Shifter(shift, var['shift']['amount'])
                else:
                    shift = self.Shifter(shift, 
                            [var['shift']['lshift'], var['shift']['rshift']]
                    )
            else:
                shift = None
            mapping[vname] = self._domain.generate_attribute(vname, shift)
        ev = ComplexEvent(self._template['act'], mapping)
        return ev
    
class PesudoTrace(PesudoGenerator):

    def __init__(self, domain:'PesudoDomain', pattern) -> None:
        self._weight = pattern['weight']
        self._events = [ 
            PesudoEvent(domain, ev)
            for ev
            in pattern['events']
        ]
        self._match = pattern['match']

    def generate(self) -> Iterable[ComplexEvent]:
        for pe in self._events:
            yield pe.generate()
    
    @property
    def weight(self) -> int: 
        return self._weight
    
    def __str__(self) -> str:
        return self._match
    
class PesudoLog(PesudoGenerator):

    def __init__(self, domain:'PesudoDomain', patterns , samplesize:int) -> None:
        self._patterns = [ 
            PesudoTrace(domain, pattern)
            for pattern 
            in patterns
        ]
        self._weights = [ 
            pt.weight
            for pt 
            in self._patterns
        ]
        self._weights = [ 
            sum(self._weights[:i])
            for i 
            in range(1,len(self._weights)+1)
        ]
        self._samplesize = samplesize

    def generate(self) -> Iterable[ComplexTrace]:
        traces = []
        debug(f"making a log of size {self._samplesize}")
        for sample in range(self._samplesize):
            coin = uniform(0, self._weights[-1])
            for w,p in zip(self._weights, self._patterns):
                if coin <= w:
                    debug(f"coin :: {coin}, pattern :: {w}-{p}")
                    traces.append(ComplexTrace(p.generate(), 
                    { "concept:name" : f"Generated Trace {sample+1}",
                     "created:from" : f"pmkoalas_{__version__}"
                    })
                    )
                    break
        debug(len(traces))
        return traces
    
class PesudoAttribute(PesudoGenerator):

    # default parameters
    DEFAULT_RANGE_FOR_UNIFORM = 10
    DEFAULT_MEAN_FOR_NORMAL = 5.0
    DEFAULT_SIGMA_FOR_NORMAL = 1.0
    # support type classes
    class SupportedDistrubutions(Enum):
        uniform = "uniform"
        normal  = "normal"

        def __init__(self, parse) -> None:
            self.parse = parse

        @classmethod
        def find_type(self, parsed:str) -> 'SupportedDistrubutions':
            for dist in self:
                if dist.parse == parsed:
                    return dist
            raise GenerationIssue(f"Unsupported Distribution found :: '{parsed}'")

    class SupportedTypes(Enum):
        float = float
        int = int 
        string = str
        bool = bool

        def __init__(self, clazz) -> None:
            self.clazz = clazz

        @classmethod
        def find_type(self, parsed:str) -> 'SupportedTypes':
            for typer in self:
                if str(typer.name) == parsed:
                    return typer 
            raise GenerationIssue("Unsupported process attribute type found" /
                                  +f" :: '{parsed}") 

    def __init__(self, parsed) -> None:
        self._name = parsed['name']
        self._dist = self.SupportedDistrubutions.find_type(
            parsed['dist']['typer']
        )
        if ("mean" in parsed['dist']):
            self._dist_mean = float(parsed['dist']['mean'])
        else: 
            self._dist_mean = None
        self._type = self.SupportedTypes.find_type(parsed['atype'])
        self._setup()

    def _setup(self) -> None:
        if self._type == self.SupportedTypes.int:
            self._setup_int()
            return
        elif self._type == self.SupportedTypes.float:
            self._setup_float()
            return
        elif self._type == self.SupportedTypes.string:
            self._setup_string()
            return
        elif self._type == self.SupportedTypes.bool:
            return
        raise GenerationIssue(f"Setup not completed for attribute type" /
                              +f" '{self._type}'")
    
    def _setup_int(self):
        if (self._dist_mean == None):
            self._dist_mean = 25
        if self._dist == self.SupportedDistrubutions.normal: 
            mean = self._dist_mean
            std = self._dist_mean/8.0
            self._normal = NormalDist(mean, std)
            self._selector = \
                lambda : int(self._normal.samples(1)[0])
        else:
            max = self._dist_mean
            self._selector = \
                lambda : int(uniform(1, max+1))

    def _setup_float(self):
        if (self._dist_mean == None):
            self._dist_mean = 25
        if self._dist == self.SupportedDistrubutions.normal: 
            mean = self._dist_mean
            std = self._dist_mean/8.0
            self._normal = NormalDist(mean, std)
            self._selector = \
                lambda : self._normal.samples(1)[0]
        else:
            max = self._dist_mean
            self._selector = \
                lambda : uniform(1, max+1)

    def _setup_string(self):
        pass 

    def generate(self, shift) -> object:
        debug(f"generating {self._name} ({self._type},{self._dist})")
        if self._type == self.SupportedTypes.int:
            return self._generate_int(shift)
        elif self._type == self.SupportedTypes.float:
            return self._generate_float(shift)
        elif self._type == self.SupportedTypes.string:
            return self._generate_string(shift)
        elif self._type == self.SupportedTypes.bool:
            return choice([True,False])
        return 1 
    
    def _generate_int(self, shift:PesudoEvent.Shifter) -> int:
        if shift == None:
            return self._selector() 
        elif shift.is_left():
            sel = self._selector()
            if self._dist == self.SupportedDistrubutions.uniform:
                ranger = [i for i in range(1, int(self._dist_mean+1))]
                mid = int((len(ranger) / 2.0)+1)
                mid = max(int(mid - (mid * ((shift.amount*2)/100.0))), 1)
                ranger = ranger[:mid]
                accept = lambda x: x in ranger
            else:
                p = (50.0 - shift.amount)/100.0
                cutoff = self._normal.inv_cdf(p)
                accept = lambda x: x <= cutoff
            while not accept(sel):
                sel = self._selector()
            return sel 
        elif shift.is_right():
            sel = self._selector()
            if self._dist == self.SupportedDistrubutions.uniform:
                ranger = [i for i in range(1, int(self._dist_mean+1))]
                mid = int((len(ranger) / 2.0)-1)
                mid = min(int(mid + (mid * ((shift.amount*2)/100.0))),
                           len(ranger)-1)
                ranger = ranger[mid:]
                accept = lambda x: x in ranger
            else:
                p = (50.0 + shift.amount)/100.0
                cutoff = self._normal.inv_cdf(p)
                accept = lambda x: x >= cutoff
            while not accept(sel):
                sel = self._selector()
            return sel  
        elif shift.is_mid():
            sel = self._selector()
            if self._dist == self.SupportedDistrubutions.uniform:
                ranger = [i for i in range(1, int(self._dist_mean+1))]
                left = int((len(ranger) / 2.0)+1)
                left = max(int(left - (left * ((shift.left*2)/100.0))), 1)
                right = int((len(ranger) / 2.0)-1)
                right = min(int(right + (right * ((shift.right*2)/100.0))),
                             len(ranger)-1)
                ranger = ranger[left:right]
                accept = lambda x: x in ranger
            else:
                lp = (50.0 - shift.left)/100.0
                lcutoff = self._normal.inv_cdf(lp)
                rp = (50.0 + shift.right)/100.0
                rcutoff = self._normal.inv_cdf(rp)
                accept = lambda x: lcutoff <= x <= rcutoff
            while not accept(sel):
                sel = self._selector()
            return sel  
        raise GenerationIssue(f"Approciate shifter not used for int :: {shift}")

    def _generate_float(self, shift) -> float: 
        if shift == None:
            return self._selector() 
        elif shift.is_left():
            sel = self._selector()
            if self._dist == self.SupportedDistrubutions.uniform:
                ranger = self._dist_mean - 1
                mid = ranger - (ranger / 2.0)
                cutoff = mid - (ranger * (0.5 - (shift.amount/100))) 
                accept = lambda x: x <= cutoff
            else:
                p = (50.0 - shift.amount)/100.0
                cutoff = self._normal.inv_cdf(p)
                accept = lambda x: x <= cutoff
            while not accept(sel):
                sel = self._selector()
            return sel 
        elif shift.is_right():
            sel = self._selector()
            if self._dist == self.SupportedDistrubutions.uniform:
                ranger = self._dist_mean - 1
                mid = ranger - (ranger / 2.0)
                cutoff = mid + (ranger * (shift.amount/100)) 
                accept = lambda x: x >= cutoff
            else:
                p = (50.0 + shift.amount)/100.0
                cutoff = self._normal.inv_cdf(p)
                accept = lambda x: x >= cutoff
            while not accept(sel):
                sel = self._selector()
            return sel  
        elif shift.is_mid():
            sel = self._selector()
            if self._dist == self.SupportedDistrubutions.uniform:
                ranger = self._dist_mean - 1
                mid = ranger - (ranger / 2.0)
                lcutoff = mid - (ranger * (0.5 - (shift.amount/100)))
                rcutoff = mid + (ranger * (shift.amount/100)) 
                accept = lambda x: lcutoff <= x <= rcutoff
            else:
                lp = (50.0 - shift.left)/100.0
                lcutoff = self._normal.inv_cdf(lp)
                rp = (50.0 + shift.right)/100.0
                rcutoff = self._normal.inv_cdf(rp)
                accept = lambda x: lcutoff <= x <= rcutoff
            while not accept(sel):
                sel = self._selector()
            return sel  
        raise GenerationIssue(f"Approciate shifter not used for int :: {shift}") 
    
    def _generate_string(self, shift) -> str:
        return choice(ascii_lowercase)
    
class PesudoDomain(PesudoGenerator):

    def __init__(self, domain) -> None:
        self._attrs =  dict(
            (key, PesudoAttribute(val))
            for key,val 
            in domain.items()
        )
        debug(self._attrs)

    def generate(self,) -> None:
        return None
    
    def generate_attribute(self, name, shift=None) -> object:
        if (name in self._attrs):
            return self._attrs[name].generate(shift) 
        else: 
            raise GenerationIssue("unable to find process attribute named " \
                                  +f"'{name}' in grammar.")
    
class PesudoSystem(PesudoGenerator):

    def __init__(self, parsed_state:ComplexLogParse) -> None:
        self._domain = PesudoDomain(parsed_state.domain)
        self._log = PesudoLog(self._domain, parsed_state.patterns(), 
                              parsed_state.samplesize())   
        super().__init__()

    def generate(self) -> ComplexEventLog:
        traces = [ t for t in self._log.generate() ]
        return ComplexEventLog(traces, {}, "Dummy log generated from grammar")

def create_generator_from_grammar(grammar:str) -> PesudoSystem:
    parsed = ComplexLogParser().prepare_parse(grammar)
    return PesudoSystem(parsed)

@enable_logging
def generate_from_grammar(grammar:str) -> ComplexEventLog:
    system = create_generator_from_grammar(grammar)
    log = system.generate()
    return log
