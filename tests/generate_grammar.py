
from utils import Grammar, simple_grammar_fuzzer
from string import ascii_lowercase
import re

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
        ["<attr>, ", "<attr>|<shift>, ", "<data><data>"],
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

from parsimonious.grammar import Grammar, NodeVisitor
from pmkoalas.simple import Trace
from abc import ABC, abstractmethod

class PesudoGenerator(ABC):

    @abstractmethod
    def generate(self) -> object:
        """
        Generates the object from the grammar parsing.
        """

class PesudoEvent(PesudoGenerator):

    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> object:
        return []
    
class PesudoTrace(PesudoGenerator):

    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> object:
        return []
    
class PesudoLog(PesudoGenerator):

    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> object:
        return []
    
class PesudoAttribute(PesudoGenerator):

    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> object:
        return [] 
    
class PesudoDomain(PesudoGenerator):

    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> object:
        return []
    
class PesudoSystem(PesudoGenerator):

    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> object:
        return []

class ComplexLogVisitor(NodeVisitor):
    """
    
    """

    par_grammar_complex_log = Grammar(
        """
        system = (domain " " log) / (log)
        log = "Patterns:{" samplesize "}" trace*
        trace = " " "[" event* " ]{" freq "}"
        event = (" " word "{" data* "}" ) / (" " word)
        word = ~"[a-z]{1,}" 
        data =  (attr "|" shift ", ") / (attr ", ")
        attr = "d_" ~"[0-9]{1}" 
        shift = mshift / limit / lshift / rshift 
        lshift = ~"[0-5]{1,2}" "-left" 
        rshift = ~"[0-5]{1,2}" "-right" 
        mshift = ~"[0-5]{1,2}" "%" "-m-" ~"[0-5]{1,2}" "%" 
        limit = ("<<" ~"[0-9]*") / (">>" ~"[0-9]*") 
        freq = ~"[1-9]*" 
        samplesize = ~"[1-9]" ~"[0-9]*"
        nonzero = ~"[1-9]" ~"[0-9]*"

        domain = "Domains:" (attribute*)
        attribute = (" " attr "-" type "-" dist) / (" " attr "-" type)
        type = "int" / "float" / "string" / "bool"
        dist = (disttype "-" ~"[0-9]*") / disttype  
        disttype = "normal" / "uniform"
        """
    )

    def prepare_parse(self, text):
        text = " ".join(text.splitlines())
        text = re.sub("\s\s+", " ", text.strip())
        tree = par_grammar_complex_log.parse(text)
        return self.visit(tree)

    def visit_system(self, node, visited_children):
        vc = visited_children[0]
        if len(vc) == 3:
            return {
                "domain" : vc[0],
                "log" : vc[2]
            }
        else:
            return {
                "log" : vc
            }

    def visit_domain(self, node, visited_children):
        output = {}
        for c in visited_children[1]:
            output[c["name"]] = c
        return output 

    def visit_log(self, node, visited_children):
        patterns = []
        # collect patterns
        for c in visited_children[3]:
            patterns.append(c)
        # collect sample size
        samplesize = visited_children[1][0].text
        return {
            "patterns" : patterns,
            "samplesize" : samplesize
        } 
    
    def visit_attribute(self, node, visited_children):
        # find attr for attribute
        # getting children is a bit odd as the structure starts one depth down
        vc = visited_children[0]
        if (len(vc) == 4):
            _, attr, _, atype = vc
            dist = {}
        else:
            _, attr, _, atype, _, dist = vc
        atype = atype[0].text
        # print(f"{attr}-{atype}-{dist}")
        res = { 
            "match" :  node.text,
            "name"  :  attr,
            "atype" :  atype,
            "dist"  : dist
        }
        return res
    
    def visit_trace(self, node, visited_children):
        trace = {
            "events" : [],
            "weight" : 1,
            "match"  : node.text
        }
        vc = visited_children
        _, _, events, _, freq, _ = vc 
        for e in events:
            trace["events"].append(e)
        trace["weight"] = freq.text
        return trace
    
    def visit_event(self, node, visited_children):
        # find elements of events
        vc = visited_children[0]
        if (len(vc) == 5):
            _, act, _, data, _ = vc 
        else:
            _, act = vc 
            data = []
        # handle data
        vars = []
        if len(data) > 0:
            for d in data:
                # extract elements
                if len(d) == 4:
                    attr, _, shift, _ = d 
                else:
                    attr,_ = d 
                    shift = None
                # add to vars 
                vars.append(
                    {
                        "name" : attr,
                        "shift" : shift
                    }
                )
        res = { 
            "match" : node.text,
            "act"   : act.text,
            "vars"  : vars  
        }
        return res
    
    def visit_data(self, node, visited_children):
        return visited_children[0]
    
    def visit_shift(self, node, visited_children):
        vc = visited_children[0]
        if  len(vc) == 2:
            shift, stype = vc
            return {
                "typer": stype.text,
                "amount": shift.text
            }
        else: 
            lshift, _, stype, rshift, _ = vc 
            return {
                "typer" : stype.text,
                "lshift" : lshift.text,
                "rshift" : rshift.text
            }
    
    def visit_lshift(self, node, visited_children):
        return visited_children 
    
    def visit_rshift(self, node, visited_children):
        return visited_children

    def visit_limit(self, node, visited_children):
        vc = visited_children[0]
        return vc  
    
    def visit_mshift(self, node, visited_children):
        return visited_children
    
    def visit_attr(self, node, visited_children):
        prefix , suffix = visited_children
        return prefix.text + suffix.text
    
    def visit_dist(self, node, visited_children):
        vc = visited_children[0]
        if (len(vc) == 3):
            atype, _, mean = vc
            return {
                "typer" : atype[0].text,
                "mean"  : mean.text
            }
        else: 
            atype = vc
            return {
                "typer" : atype[0].text
            }

    def generic_visit(self, node, visited_children):
        return visited_children or node


par_grammar_complex_log = Grammar(
    """
    system = (domain " " log) / (log)
    log = "Patterns:{" samplesize "}" trace*
    trace = " " "[" event* " ]{" freq "}"
    event = (" " word "{" data* "}" ) / (" " word)
    word = ~"[a-z]{1,}" 
    data =  (attr "|" shift ", ") / (attr ", ")
    attr = "d_" ~"[0-9]{1}" 
    shift = mshift / limit / lshift / rshift 
    lshift = ~"[0-5]{1,2}" "-left" 
    rshift = ~"[0-5]{1,2}" "-right" 
    mshift = ~"[0-5]{1,2}" "%" "-m-" ~"[0-5]{1,2}" "%" 
    limit = ("<<" ~"[0-9]*") / (">>" ~"[0-9]*") 
    freq = ~"[1-9]*" 
    samplesize = ~"[1-9]" ~"[0-9]*"
    nonzero = ~"[1-9]" ~"[0-9]*"

    domain = "Domains:" (attribute*)
    attribute = (" " attr "-" type "-" dist) / (" " attr "-" type)
    type = "int" / "float" / "string" / "bool"
    dist = (disttype "-" ~"[0-9]*") / disttype  
    disttype = "normal" / "uniform"
    """
)

test_trace_01 = " [ u ]{8}"
test_trace_02 = " [ a b c ]{16}"
test_trace_03 = " [ a{d_1, } ]{224}"
test_trace_04 = " [ a{d_1, d_2, } b c ]{224}"
test_trace_05 = " [ dog{d_1, d_2, } cat dog ]{224}"
test_trace_grammar = Grammar(
    """
    trace = " " "[" event* " ]{" freq "}"
    event = (" " word "{" data* "}" ) / (" " word)
    word = ~"[a-z]{1,}" 
    data =  (attr "|" shift ", ") / (attr ", ")
    attr = "d_" ~"[0-9]{1}" 
    shift = mshift / limit / lshift / rshift 
    lshift = ~"[0-5]{1,2}" "-left" 
    rshift = ~"[0-5]{1,2}" "-right" 
    mshift = ~"[0-5]{1,2}" "%" "-m-" ~"[0-5]{1,2}" "%" 
    limit = ("<<" ~"[0-9]*") / (">>" ~"[0-9]*") 
    freq = ~"[1-9]*" 
    samplesize = ~"[1-9]" ~"[0-9]*"
    nonzero = ~"[1-9]" ~"[0-9]*"
    """
)
trace_tests = [ test_trace_01, test_trace_02, test_trace_03, test_trace_04,
                test_trace_05
]

test_attribute_01 = """
    Domains:
        d_1-float-uniform-3
"""
test_attribute_02 = """
    Domains:
        d_1-float-uniform-3
        d_1-int
        d_5-int-uniform-2
"""
test_domain_grammar = Grammar( """
    domain = "Domains:" (attribute*)
    attribute = (" " attr "-" type "-" dist) / (" " attr "-" type)
    type = "int" / "float" / "string" / "bool"
    dist = (disttype "-" ~"[0-9]*") / disttype  
    disttype = "normal" / "uniform"
    attr = "d_" ~"[0-9]{1}"
    """
)
attribute_tests = [test_attribute_01, test_attribute_02]


test_log_01 = """Patterns:{10} 
    [ a b c ]{3}
"""
test_log_02 = """
    Patterns:{8339} 
        [ z{d_2|>>671, d_2|4-left, } ]{9}
"""
test_log_03 = """
    Patterns:{7} 
        [ d{d_0|4-right, d_8, d_0|3-left, d_8|>>9, } ]{19} 
        [ h{d_2, } v ]{96}
"""

log_tests = [test_log_01, test_log_02, test_log_03]


test_system_01 = """
    Domains: 
        d_9-float-uniform 
    Patterns:{4} 
        [ k{d_0|4%-m-1%, } ]{2}

"""
test_system_02 = """
    Domains: 
        d_7-string-uniform-38 
        d_7-string 
    Patterns:{6} 
        [ m{d_4|>>1, } ]{9}
"""
test_system_03 = """
    Patterns:{85341655} 
        [ p n ]{1778}
        [ v{d_5, 
        d_8,
        d_2|54-left,
        d_8|2-right,
        d_4,
        d_5|15-right,
        d_6|5-right,
        d_9|0%-m-10%,
        d_7|4-right,
        d_0,
        d_3|02%-m-10%,
        d_2|>>62,
        d_8|2-right,
        } ]{15}
        [ z ]{6}
"""
test_system_04 = """
    Domains: 
        d_1-float-uniform-3 
        d_1-int 
        d_5-int-uniform-2 
    Patterns:{2} 
        [ b ]{72867}
"""
test_system_05 = """
    Domains: 
        d_0-int-uniform 
    Patterns:{28} 
        [ t{d_1, d_0|41%-m-21%, } ]{97} 
        [ y{d_7, } ]{3173273}
"""
test_system_06 = """
    Patterns:{3} 
        [ w{d_5, } ]{16981498579561286884813} 
        [ q{d_4|1%-m-4%, d_5, d_2, d_1|4-right, d_2|<<8262054, d_0, d_3, d_9, d_2|4-right, d_7, d_9|32-right, } s{d_3|1-right, d_8, d_1, d_8|33-left, } ]{3} 
        [ a ]{9}
"""
test_system_07 = """
    Domains: 
        d_8-string-normal 
    Patterns:{89} 
        [ l ]{936288} 
        [ a p q{d_4, } b i y{d_6, d_1, } r p ]{9}
"""
system_tests = [test_system_01, test_system_02, test_system_03, test_system_04,
                test_system_05, test_system_06]

if __name__ == "__main__":
    print("testing finding a trace")
    for test in trace_tests:
        print(f"test string :: {test}")
        try :
            out = test_trace_grammar.parse(test)
            print("passed")
        except Exception as e :
            print(f"!!!failed :: {e}")

    print("testing finding a attribute")
    for test in attribute_tests:
        formatted_test = " ".join(test.splitlines())
        formatted_test = re.sub("\s\s+", " ", formatted_test.strip())
        print(f"test string :: '{formatted_test}'")
        try :
            out = test_domain_grammar.parse(formatted_test)
            print("passed")
        except Exception as e :
            print(f"!!!failed :: {e}")

    print("testing on log patterns")
    for test in log_tests:
        formatted_test = " ".join(test.splitlines())
        formatted_test = re.sub("\s\s+", " ", formatted_test.strip())
        print(f"test string :: '{formatted_test}'")
        try :
            out = par_grammar_complex_log.parse(formatted_test)
            print("passed")
        except Exception as e :
            print(f"!!!failed :: {e}")

    print("testing on system patterns")
    for test in system_tests:
        formatted_test = " ".join(test.splitlines())
        formatted_test = re.sub("\s\s+", " ", formatted_test.strip())
        print(f"test string :: '{formatted_test}'")
        try :
            out = par_grammar_complex_log.parse(formatted_test)
            print("passed")
        except Exception as e :
            print(f"!!!failed :: {e}")
    
    fuzzed_out = simple_grammar_fuzzer(
        COMPLEX_LOG_GRAMMAR,
        "<system>",
        50,
        100,
        False
    )
    # fuzzed_out = test_system_07
    print(f"Fuzzed output :: '{fuzzed_out}'")
    iv = ComplexLogVisitor()
    out = iv.prepare_parse(fuzzed_out)
    print(out)
    print(f"parsed output:")
    if "domain" in out:
        print("Domain:")
        for key, val in out['domain'].items():
            print(f"\t{key} -- {val}")
    print(f"Log ({out['log']['samplesize']})")
    for i,pattern in enumerate(out["log"]["patterns"]):
        print(f"\tPattern {i+1} : (weight={pattern['weight']})")
        for e in pattern["events"]:
            print(f"\t\t {e['act']}")
            print(f"\t\t\t vars : {e['vars']}")


    