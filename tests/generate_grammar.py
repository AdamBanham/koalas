
from utils import Grammar, simple_grammar_fuzzer
from string import ascii_lowercase

COMPLEX_LOG_GRAMMAR: Grammar = {
    "<system>" : 
        ["<log>", "<domain> <log>"],
    "<log>" : 
        ["Patterns:{<nonzero>} <trace>"],
    "<trace>" : 
        ["[ <event> ]{<nonzero>}", "[ <event> ]{<nonzero>} <trace>" ],
    "<event>" :
        ["<event> <event>", "<word>" , "<word>{<data>}"],
    "<word>" :
        ["<ascii>"],
    "<data>" : 
        ["<attr>,", "<attr>|<shift>,", "<data><data>"],
    "<attr>" : 
        ["d_<alldigits>"],
    "<shift>" : 
        ["<limit>" , "<lshift>", "<rshift>", "<mshift>"],
    "<lshift>" : 
        ["<halfnumber>-left"],
    "<rshift>" : 
        ["<halfnumber>-right"],
    "<mshift>" : 
        ["<halfnumber>%-m-<halfnumber>%"],
    "<limit>" :
        ["<<<number>", ">><number>"],
    "<halfnumber>" :
        ["<halfdigits>" , "<halfdigits><halfdigits>"],
    "<number>" :
        ["<alldigits>", "<number><number>"],
    "<nonzero>" :
        ["<nonzerodigits>", "<nonzero><nonzero>"],
    "<alldigits>" : 
        ["0","1", "2", "3", "4", "5", "6", "7", "8","9"],
    "<nonzerodigits>" : 
        ["1", "2", "3", "4", "5", "6", "7", "8","9"],
    "<halfdigits>" : 
        ["5", "4", "3", "2", "1", "0"],
    "<ascii>" : 
        [ s for s in ascii_lowercase],
    "<domain>" : 
        ["Domains: <attribute>"],
    "<attribute>" : 
        ["<attribute> <attribute>", "<attr>-<type>", "<attr>-<type>-<dist>"],
    "<type>" : 
        ["int", "float", "string", "bool"],
    "<dist>" : 
        ["<disttype>" , "<disttype>-<number>"],
    "<disttype>" : 
        ["normal", "uniform"]
}

from parsimonious.grammar import Grammar

par_grammar_complex_log = Grammar(
    """
    system = (domain " " log) / (log)
    log = "Patterns:{" samplesize "}" trace*
    trace = (" " "[" event* " ]{" freq "}") 
    event = (" " word "{" data* "}" ) / (" " word)
    word = ~"[a-z]{1,}" 
    data = (attr ",") / (attr "|" shift ",") 
    attr = "d_" ~"[0-9]{1}" 
    shift = limit / lshift / rshift / mshift 
    lshift = ~"[0-5]{,2}""-left" 
    rshift = ~"[0-5]{,2}""-right" 
    mshift = ~"[0-5]{,2}" "-m-" ~"[0-5]{,2}" 
    limit = ("<<" ~"[0-9]*") / (">>" ~"[0-9]*") 
    freq = ~"[1-9]*" 
    samplesize = ~"[1-9]*" 
    nonzero = ~"[1-9]*" 

    domain = "Domains: " (attribute*)
    attribute = (attr "-" type "-" dist) / (attr "-" type)
    type = "int" / "float" / "string" / "bool"
    dist = disttype / (disttype "-" ~"[0-9]*")
    disttype = "normal" / "uniform"
    """
)

test_trace_01 = " [ u ]{8}"
test_trace_02 = " [ a b c ]{16}"
test_trace_03 = " [ a{d_1,} ]{224}"
test_trace_04 = " [ a{d_1,d_2,} b c ]{224}"
test_trace_05 = " [ dog{d_1,d_2,} cat dog ]{224}"
test_trace_grammar = Grammar(
    """
    trace = " " "[" event* " ]{" freq "}"
    event = (" " word "{" data* "}" ) / (" " word)
    word = ~"[a-z]{1,}" 
    data = (attr ",") / (attr "|" shift ",") 
    attr = "d_" ~"[0-9]{1}" 
    shift = limit / lshift / rshift / mshift 
    lshift = ~"[0-5]{,2}""-left" 
    rshift = ~"[0-5]{,2}""-right" 
    mshift = ~"[0-5]{,2}" "-m-" ~"[0-5]{,2}" 
    limit = ("<<" ~"[0-9]*") / (">>" ~"[0-9]*") 
    freq = ~"[1-9]*" 
    samplesize = ~"[1-9]*" 
    nonzero = ~"[1-9]*" 
    """
)
trace_tests = [ test_trace_01, test_trace_02, test_trace_03, test_trace_04,
                test_trace_05
]

if __name__ == "__main__":
    print("testing finding a trace")
    for test in trace_tests:
        print(f"test string :: {test}")
        print(test_trace_grammar.parse(test))
    
    fuzzed_out = simple_grammar_fuzzer(
        COMPLEX_LOG_GRAMMAR,
        "<system>",
        7,
        100,
        True
    )
    print(f"Fuzzed output :: '{fuzzed_out}'")
    print(par_grammar_complex_log.parse(fuzzed_out))

    