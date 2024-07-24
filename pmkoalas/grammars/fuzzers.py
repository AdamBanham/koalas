"""
This module includes Fuzzers that produce non-meaningful but compliant 
constructs of given fuzzing grammars. These are useful for testing techniques 
as well as testing. In some cases, they are useful for finding edge cases for 
techniques as well.
"""

from typing import List, Dict
import re
import random

FuzzGrammar = Dict[str, List]

RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

def nonterminals(expansion):
    if isinstance(expansion, tuple):
        expansion = expansion[0]
    return RE_NONTERMINAL.findall(expansion)

def is_nonterminal(s):
    return RE_NONTERMINAL.match(s)

class ExpansionError(Exception):
    pass

def simple_grammar_fuzzer(grammar: FuzzGrammar, 
                          start_symbol: str,
                          max_nonterminals: int = 10,
                          max_expansion_trials: int = 100,
                          log: bool = False) -> str:
    """
    Produce a string from `grammar`.\n
    Parameters
    ----------
    `start_symbol`: the start symbol \n
    `max_nonterminals`: the maximum number of nonterminals still left for 
    expansion \n
    `max_expansion_trials`: maximum # of attempts to produce a string \n
    `log`: print expansion progress if True \n
    """

    term = start_symbol
    expansion_trials = 0

    while len(nonterminals(term)) > 0:
        symbol_to_expand = random.choice(nonterminals(term))
        expansions = grammar[symbol_to_expand]
        expansion = random.choice(expansions)
        # In later chapters, we allow expansions to be tuples,
        # with the expansion being the first element
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        new_term = term.replace(symbol_to_expand, expansion, 1)

        if len(nonterminals(new_term)) < max_nonterminals:
            term = new_term
            if log:
                print("%-40s" % (symbol_to_expand + " -> " + expansion), term)
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= max_expansion_trials:
                raise ExpansionError("Cannot expand " + repr(term))

    return term