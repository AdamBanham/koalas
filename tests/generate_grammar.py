from utils import Grammar, simple_grammar_fuzzer
from string import ascii_lowercase

COMPLEX_LOG_GRAMMAR: Grammar = {
    "<system>" : 
        ["<log>", "<domain> <log>"],
    "<log>" : 
        ["[Patterns]{<number>} <trace>"],
    "<trace>" : 
        ["[ <event> ]", "[<event>] <trace>" ],
    "<event>" :
        ["<event> <event>", "<word>" , "<word>{<data>}"],
    "<word>" :
        ["<ascii>"],
    "<ascii>" : 
        ascii_lowercase,
    "<data>" : 
        ["<attr>", "<attr>|<shift>", "<data> <data>"],
    "<attr>" : 
        ["d_<alldigits>"],
    "<shift>" : 
        ["<limit>" , "<lshift>", "<rshift>", "<mshift>"],
    "<lshift>" : 
        ["<number>%-left"],
    "<rshift>" : 
        ["<number>%-right"],
    "<mshift>" : 
        ["<number>%-m-<number>%"],
    "<limit>" :
        ["<< <number>", ">> <number>"],
    "<number>" :
        ["<digit>", "<digit><digit>"],
    "<digit>" : 
        ["5", "4", "3", "2", "1", "0"],
    "<alldigits>" : 
        ["1", "2", "3", "4", "5", "6", "7", "8","9"],
    "<domain>" : 
        ["[Domains] "]
}

if __name__ == "__main__":
    simple_grammar_fuzzer(
        COMPLEX_LOG_GRAMMAR,
        "[Patterns] <trace> <trace> <trace>",
        50,
        100,
        True
    )