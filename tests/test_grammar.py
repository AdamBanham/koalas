import re
import unittest
from logging import debug, getLogger, DEBUG
from os.path import join

from pmkoalas.grammars.fuzzers import simple_grammar_fuzzer
from pmkoalas.grammars.fuzzers import ExpansionError
from pmkoalas.grammars.complex_logs import COMPLEX_TRACE_FUZZING_GRAMMAR
from pmkoalas.grammars.complex_logs import COMPLEX_DOMAIN_FUZZING_GRAMMAR
from pmkoalas.grammars.complex_logs import COMPLEX_LOG_FUZZING_GRAMMAR
from pmkoalas.grammars.complex_logs import ComplexLogParser, strip_grammar
from pmkoalas.grammars.complex_logs import COMPLEX_LOG_PARSING_GRAMMAR
from pmkoalas.grammars.complex_logs import COMPLEX_TRACE_PARSING_GRAMMAR
from pmkoalas.grammars.complex_logs import COMPLEX_DOMAIN_PARSING_GRAMMAR
from pmkoalas.grammars.complex_logs import ComplexLogParse

test_trace_01 = "[ u ]{8}"
test_trace_02 = "[ a b c ]{16}"
test_trace_03 = "[ a{d_1, } ]{224}"
test_trace_04 = "[ a{d_1, d_2, } b c ]{224}"
test_trace_05 = "[ dog{d_1, d_2, } cat dog ]{224}"
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
domain_tests = [test_attribute_01, test_attribute_02]

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
        d_2|54%-left,
        d_8|2%-right,
        d_4,
        d_5|15%-right,
        d_6|5%-right,
        d_9|0%-m-10%,
        d_7|4%-right,
        d_0,
        d_3|02%-m-10%,
        d_2|>>62,
        d_8|2%-right,
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
        [ q{d_4|1%-m-4%, d_5, d_2, d_1|4%-right, 
          d_2|<<8262054, d_0, d_3, d_9, d_2|4%-right, d_7, d_9|32%-right, } 
          s{d_3|1%-right, d_8, d_1, d_8|33%-left, } 
        ]{3} 
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

case_system_file = join(".","tests","case_system.gen")

def pretty_out(parse:ComplexLogParse) -> str:
    out = "parsed output:\n"
    if parse.has_domain():
        out += "Domain:\n"
        for key, val in parse.attributes():
            out += f"\t{key} -- {val}\n"
    out += f"Log ({parse.samplesize()})\n"
    for i,pattern in enumerate(parse.patterns()):
        out += f"\tPattern {i+1} : (weight={pattern['weight']})\n"
        for e in pattern["events"]:
            out += f"\t\t {e['act']}\n"
            out += f"\t\t\t vars : {e['vars']}\n"
    return out

class DTLogTest(unittest.TestCase):

    MAX_TRAILS = 50

    def setUp(self) -> None:
        self.complex_parser = ComplexLogParser()
        self.show_logging = getLogger().isEnabledFor(DEBUG)

    def test_trace_grammar(self):
        for test in trace_tests:
            test = strip_grammar(test)
            debug(f"test string :: {test}")
            try :
                out = COMPLEX_TRACE_PARSING_GRAMMAR.parse(test)
            except Exception as e :
                self.fail(f"!!! failed to parse trace in grammar :: {e}")

    def test_fuzz_trace_grammar(self):
        for curr in range(self.MAX_TRAILS):
            try :
                exemplar = simple_grammar_fuzzer(
                    COMPLEX_TRACE_FUZZING_GRAMMAR,
                    "<trace><trace><trace>",
                    25,
                    100,
                    self.show_logging
                    )
            except ExpansionError:
                continue
            exemplar = strip_grammar(exemplar)
            try :
                out = COMPLEX_TRACE_PARSING_GRAMMAR.parse(exemplar)
            except Exception as e :
                self.fail(f"!!! ({curr+1}/{self.MAX_TRAILS}) failed to " \
                          + f" parse fuzzed trace : \n {exemplar}\n" \
                          + f" reason :: {e}") 

    def test_domain_grammar(self):
        for test in  domain_tests:
            test = strip_grammar(test)
            debug(f"test string :: {test}")
            try :
                out = COMPLEX_DOMAIN_PARSING_GRAMMAR.parse(test)
            except Exception as e :
                self.fail(f"!!! failed to parse domains in grammar :: {e}")

    def test_fuzz_domain_grammar(self):
        for curr in range(self.MAX_TRAILS):
            try :
                exemplar = simple_grammar_fuzzer(
                    COMPLEX_DOMAIN_FUZZING_GRAMMAR,
                    "Domains: <attribute> <attribute> <attribute> ",
                    25,
                    100,
                    self.show_logging
                    )
            except ExpansionError:
                continue
            exemplar = strip_grammar(exemplar)
            try :
                out = COMPLEX_DOMAIN_PARSING_GRAMMAR.parse(exemplar)
            except Exception as e :
                self.fail(f"!!! ({curr+1}/{self.MAX_TRAILS}) failed to " \
                          + f" parse fuzzed trace : \n {exemplar}\n" \
                          + f" reason :: {e}")  

    def test_system_grammar(self):
        for test in system_tests :
            test = strip_grammar(test)
            debug(f"test string :: {test}")
            try :
                out = COMPLEX_LOG_PARSING_GRAMMAR.parse(test)
            except Exception as e :
                self.fail(f"!!! failed to parse domains in grammar ('{test}') :: {e}") 

    def test_fuzz_system_grammar(self):
        for curr in range(self.MAX_TRAILS):
            try :
                exemplar = simple_grammar_fuzzer(
                    COMPLEX_LOG_FUZZING_GRAMMAR,
                    "Domains: <attribute> Patterns:{100} <trace> <trace> <trace>",
                    25,
                    100,
                    self.show_logging
                    )
            except ExpansionError:
                continue
            exemplar = strip_grammar(exemplar)
            try :
                out = COMPLEX_LOG_PARSING_GRAMMAR.parse(exemplar)
            except Exception as e :
                self.fail(f"!!! ({curr+1}/{self.MAX_TRAILS}) failed to " \
                          + f" parse fuzzed trace : \n '{exemplar}'\n" \
                          + f" reason :: {e}")   
                
    def test_case_system_parse(self):
        #load in case system grammar
        with open(case_system_file, "r") as f:
            csystem = f.read()
            out = self.complex_parser.prepare_parse(csystem)
            print(out)
            print(pretty_out(out))

# if __name__ == "__main__":
    
#     fuzzed_out = simple_grammar_fuzzer(
#         COMPLEX_LOG_GRAMMAR,
#         "<system>",
#         50,
#         100,
#         False
#     )
#     # fuzzed_out = test_system_07
#     print(f"Fuzzed output :: '{fuzzed_out}'")
#     iv = ComplexLogVisitor()
#     out = iv.prepare_parse(fuzzed_out)
#     pretty_out(out)
#     # test loading in case_system
#     csystem = ""
#     with open("./tests/case_system.gen", "r") as f:
#         csystem = f.read()
#     print()
#     iv = ComplexLogVisitor()
#     out = iv.prepare_parse(csystem)
#     pretty_out(out)


    