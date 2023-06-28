"""
This module includes the grammar tools used for the generate (top-level) 
module. The machinery in this module allows for the general prasing of the 
grammar. It also includes the fuzzing dictionary for generating abitiary
compliant members of the grammar.

GRAMMAR
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
<ascii> :: a | b | c | ... | x | y | z ** anything that matches [a-zA-Z0-9_]*

<domain> :: [Domains] <atttribute>
<attribute> :: <attribute> <attribute> | <attr>-<type> | <attr>-<type>-<dist>
<type> :: int | float | string | bool
<dist> :: <disttype> | <disttype>-<number>
<disttype> :: normal | uniform

"""
from re import sub
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Dict, Union, Iterable, Tuple
from dataclasses import dataclass

from pmkoalas.grammars.fuzzers import FuzzGrammar

# external library for handling grammars (parsing)
from parsimonious.grammar import Grammar, NodeVisitor

# Fuzzing tool
COMPLEX_LOG_FUZZING_GRAMMAR: FuzzGrammar = {
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
        ["<limit>", "<lshift>", "<rshift>", "<mshift>"],
    "<lshift>" : 
        ["<halfnumber>%-left"],
    "<rshift>" : 
        ["<halfnumber>%-right"],
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
        [ s for s in ascii_lowercase+ascii_uppercase+digits+"_" ],
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

COMPLEX_TRACE_FUZZING_GRAMMAR:FuzzGrammar = {
    "<trace>" : 
        ["[ <event> ]{<nonzero>} "],
    "<event>" :
        ["<event> <event>", "<word>" , "<word>{<data>}"],
    "<word>" :
        ["<ascii>"],
    "<data>" : 
        ["<attr>, ", "<attr>|<shift>, ", "<data><data>"],
    "<attr>" : 
        ["d_<alldigits>"],
    "<shift>" : 
        ["<limit>", "<lshift>", "<rshift>", "<mshift>"],
    "<lshift>" : 
        ["<halfnumber>%-left"],
    "<rshift>" : 
        ["<halfnumber>%-right"],
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
        [ s for s in ascii_lowercase+ascii_uppercase+digits+"_"],
}

COMPLEX_DOMAIN_FUZZING_GRAMMAR:FuzzGrammar = {
    "<domain>" : 
        ["Domains: <attribute> "],
    "<attribute>" : 
        ["<attribute> <attribute>", "<attr>-<type>", "<attr>-<type>-<dist>"],
    "<type>" : 
        ["int", "float", "string", "bool"],
    "<dist>" : 
        ["<disttype>" , "<disttype>-<number>"],
    "<disttype>" : 
        ["normal", "uniform"],
    "<attr>" : 
        ["d_<alldigits>"],
    "<number>" :
        ["<alldigits>", "<number><number>"],
    "<alldigits>" : 
        ["0","1", "2", "3", "4", "5", "6", "7", "8","9"],
}

# Parsing Grammar (a bit different from fuzzing setup)
COMPLEX_LOG_PARSING_GRAMMAR: Grammar = Grammar(
        """
        system = (domain " " log) / (log)
        log = "Patterns:{" samplesize "}" trace* " "
        trace = " " "[" event* " ]{" freq "}"
        event = (" " word "{" data* "}" ) / (" " word)
        word = ~"[a-zA-Z0-9_]{1,}" 
        data =  (attr "|" shift ", ") / (attr ", ")
        attr = "d_" ~"[0-9]{1}" 
        shift = mshift / limit / lshift / rshift 
        lshift = ~"[0-5]{1,2}" "%-left" 
        rshift = ~"[0-5]{1,2}" "%-right" 
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

# Parsing Grammer for traces (used for testing)
COMPLEX_TRACE_PARSING_GRAMMAR: Grammar = Grammar(
        """
        log = trace*
        trace = "[" event* " ]{" freq "} " 
        event = (" " word "{" data* "}" ) / (" " word)
        word = ~"[a-zA-Z0-9_]{1,}" 
        data =  (attr "|" shift ", ") / (attr ", ")
        attr = "d_" ~"[0-9]{1}" 
        shift = mshift / limit / lshift / rshift 
        lshift = ~"[0-5]{1,2}" "%-left" 
        rshift = ~"[0-5]{1,2}" "%-right" 
        mshift = ~"[0-5]{1,2}" "%" "-m-" ~"[0-5]{1,2}" "%" 
        limit = ("<<" ~"[0-9]*") / (">>" ~"[0-9]*") 
        freq = ~"[1-9]*" 
        samplesize = ~"[1-9]" ~"[0-9]*"
        nonzero = ~"[1-9]" ~"[0-9]*"
        """
)

# Parsing Grammar for domain (used for testing)
COMPLEX_DOMAIN_PARSING_GRAMMAR: Grammar = Grammar(
        """
        domain = "Domains:" (attribute*) " "
        attribute = (" " attr "-" type "-" dist) / (" " attr "-" type)
        type = "int" / "float" / "string" / "bool"
        dist = (disttype "-" ~"[0-9]*") / disttype  
        disttype = "normal" / "uniform"
        attr = "d_" ~"[0-9]{1}" 
        """
)

def strip_grammar(grammar:str) -> str:
    ret = " ".join(grammar.strip().splitlines())
    ret = sub("\s\s+", " ", ret.strip())
    return ret + " "

@dataclass
class ComplexLogParse():
    """
    Minimized structured output of the ComplexLogParser.
    """

    log:Dict[str,object]
    domain:Union[None,Dict[str,object]] = None

    def has_domain(self) -> bool:
        return self.domain != None 
    
    def samplesize(self) -> int:
        return self.log['samplesize']
    
    def patterns(self) -> Iterable[Dict]:
        return self.log['patterns']
    
    def attributes(self) -> Iterable[Tuple[str,Dict]]:
        if self.has_domain():
            return self.domain.items()
        else:
            return []

# Parsing tool
class ComplexLogParser(NodeVisitor):
    """
    
    """

    def prepare_parse(self, grammar:str):
        text = strip_grammar(grammar)
        tree = COMPLEX_LOG_PARSING_GRAMMAR.parse(text)
        return self.visit(tree)

    def visit_system(self, node, visited_children):
        vc = visited_children[0]
        if len(vc) == 3:
            return ComplexLogParse(log=vc[2],domain=vc[0])
        else:
            return ComplexLogParse(log=vc)

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
        samplesize = ""
        for c in visited_children[1]:
            samplesize += c.text
        return {
            "patterns" : patterns,
            "samplesize" : int(samplesize)
        } 
    
    def visit_attribute(self, node, visited_children):
        # find attr for attribute
        # getting children is a bit odd as the structure starts one depth down
        vc = visited_children[0]
        if (len(vc) == 4):
            _, attr, _, atype = vc
            dist = {
                "typer"  : "uniform",
                "amount" : 10
            }
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
        trace["weight"] = int(freq.text)
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
                "typer": stype.text[2:],
                "amount": int(shift.text)
            }
        else: 
            lshift, _, stype, rshift, _ = vc 
            return {
                "typer" : "mid",
                "lshift" : int(lshift.text),
                "rshift" : int(rshift.text)
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