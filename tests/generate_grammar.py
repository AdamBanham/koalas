from utils import Grammar, simple_grammar_fuzzer
from string import ascii_lowercase

COMPLEX_LOG_GRAMMAR: Grammar = {
    "<system>" : 
        ["<log>", "<domain> <log>"],
    "<log>" : 
        ["[Patterns]{<number>} <trace>"],
    "<trace>" : 
        ["[ <event> ]{<nonzero>}", "[<event>]{<nonzero>} <trace>" ],
    "<event>" :
        ["<event> <event>", "<word>" , "<word>{<data>}"],
    "<word>" :
        ["<ascii>"],
    "<data>" : 
        ["<attr>", "<attr>|<shift>", "<data>,<data>"],
    "<attr>" : 
        ["d_<alldigits>"],
    "<shift>" : 
        ["<limit>" , "<lshift>", "<rshift>", "<mshift>"],
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
        ascii_lowercase,
    "<domain>" : 
        ["[Domains] "]
}

if __name__ == "__main__":
    simple_grammar_fuzzer(
        COMPLEX_LOG_GRAMMAR,
        "[Patterns]{200} [ <event> ]{<nonzero>} [ <event> ]{<nonzero>}" \
        +" [ <event> ]{<nonzero>}",
        50,
        100,
        True
    )