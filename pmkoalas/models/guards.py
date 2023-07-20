"""
This module handles all machinery need to parse, check, and export
expressions on models, i.e. guards associated with transitions in a Petri net
with data.
"""
from pmkoalas.complex import ComplexTrace


from pyparsing import (
    Word,
    nums,
    alphas,
    Combine,
    oneOf,
    opAssoc,
    infixNotation,
    Literal,
)

from typing import Any,Set,Dict
from copy import deepcopy,copy
from enum import Enum

class EvalLiteral:
    "Class to evaluate a parsed literal"

    def __init__(self):
        self.value = None

    def eval(self):
        return eval( self.value.replace('&#34;',"'"))

    def __call__(self, tokens) -> Any:
        self.value = tokens[0]
        return copy(self)
    
class EvalVariable:
    "Class to evaluate a parsed variable"

    def __init__(self, state_space):
        self.value = None
        self._observed_variables = set()
        self._set_state_space(state_space)

    def _set_state_space(self, space):
        self._state_space = space 

    def eval(self, dryrun=False):
        if (dryrun):
            self._observed_variables.add(self.value)
            return
        if self.value in self._state_space:
            return self._state_space[self.value]
        raise ValueError(f"Undefined variable :: {self.value}")

    def seen_variables(self) -> Set:
        return self._observed_variables
    
    def __call__(self, tokens) -> Any:
        self.value = tokens[0]
        self.eval(dryrun=True)
        return copy(self)
    
class EvalConstant:
    "Class to evaluate a parsed numeric constant"

    def __init__(self):
        self.value = None

    def eval(self):
        if self.value == 'true':
            return True 
        elif self.value == 'false':
            return False
        return float(self.value)

    def __call__(self, tokens) -> Any:
        self.value = tokens[0]
        return copy(self)


class EvalComparisonOp:
    "Class to evaluate comparison expressions"
    opMap = {
        "&lt;" : lambda a, b: a < b,
        "&lt;=" : lambda a,b: a <= b,
        "&gt;" : lambda a, b: a > b,
        "&gt;=" : lambda a,b: a >= b,
        "==": lambda a, b: a == b,
        '&amp;&amp;': lambda a,b: a and b,
        "<" : lambda a, b: a < b,
        "<=" : lambda a,b: a <= b,
        ">" : lambda a, b: a > b,
        ">=" : lambda a,b: a >= b,
        '&&': lambda a,b: a and b,
    }

    def __init__(self):
        self.value = None

    def eval(self):
        val1 = self.value[0].eval()
        for op, val in self.operatorOperands(self.value[1:]):
            fn = EvalComparisonOp.opMap[op]
            val2 = val.eval()
            if not fn(val1, val2):
                break
            val1 = val2
        else:
            return True
        return False

    def operatorOperands(self,tokenlist):
        "generator to extract operators and operands in pairs"
        it = iter(tokenlist)
        while 1:
            try:
                yield (next(it), next(it))
            except StopIteration:
                break

    def __call__(self, tokens) -> Any:
        self.value = tokens[0]
        return copy(self)

class ExpressionParser():
    "A parser for guards associated with Petri net with Data"

    def __init__(self, state_space, exp:str) -> None:
        self._space = state_space
        self._org_exp = exp
        self._create_instances()
        self._create_operand()
        self._expr_form()
        self._parse()

    def _create_instances(self) -> None:
        self._constant = EvalConstant()
        self._literal = EvalLiteral()
        self._variable = EvalVariable(self._space)
        self._comparison = EvalComparisonOp()

    def _create_operand(self) -> None:
        # operand for parser
        booleans = Literal("true") | Literal('false')
        integer = Word(nums)
        real = Combine(Word(nums) + "." + Word(nums))
        values = booleans | real | integer 
        values.setParseAction(self._constant)

        literal = Combine('&#34;' + Word(alphas) + '&#34;')
        literal = literal | Combine('"' + Word(alphas) + '"')
        literal.setParseAction(self._literal)

        variable = Combine(Word(alphas,exact=1) + Word(alphas + nums))
        variable.setParseAction(self._variable)

        self._operand = values | literal | variable

    def _expr_form(self) -> None:
        comparisonop = oneOf("&lt;= <= &gt;= >= &lt; < &gt; > == &amp;&amp; &&")
        self._expr = infixNotation(
            self._operand,
            [
                (comparisonop, 2, opAssoc.LEFT, self._comparison),
            ],
        )

    def _parse(self):
        self._result = self._expr.parseString(self._org_exp)[0]

    def get_observed_vars(self):
        return self._variable.seen_variables()

    def change_state_space(self, state_space):
        self._space = state_space
        self._create_instances()
        self._create_operand()
        self._expr_form()
        self._parse()

    def result(self):
        return self._result.eval()
    
class GuardOutcomes(Enum):
    TRUE = True 
    FALSE = False
    UNDEF = "undefined"
    
class Expression():
    """
    A representation of reasoning extractable from a boolean logic expression.
    """

    def __init__(self, exp:str,) -> None:
        self._org_exp = exp 
        self._parser = ExpressionParser(dict(), exp)
        self._parsed_exp = None
        self._dom = self._find_dom(exp)

    def _find_dom(self, exp:str) -> Set[str]:
        parser = ExpressionParser(dict(), exp)
        return parser.get_observed_vars()
    
    def can_evaluate(self, data:Dict[str,object]) -> bool:
        """
        Checks if all variables are present for evaluation.
        """
        for req in self._dom:
            if req not in data:
                return False
        return True

    def evaluate(self, data:Dict[str,object]) -> GuardOutcomes:
        """
        Evalutes the expression using the given data.
        """
        if (not self.can_evaluate(data)):
            return GuardOutcomes.UNDEF
        try:
            ret = ExpressionParser(data, self._org_exp).result()
            if ret:
                return GuardOutcomes.TRUE
            else:
                return GuardOutcomes.FALSE
        except Exception as e:
            print(f"Failed to evaluate :: {e}")
            return GuardOutcomes.UNDEF

    def __str__(self) -> str:
        return self._org_exp
    
    def __eq__(self, other: object) -> bool:
        if (type(self) == type(other)):
            return hash(self) == hash(str)
        return False
    
    def __hash__(self) -> int:
        return hash(str(self))

class Guard():
    """
    An abstraction for a guard.
    """

    def __init__(self, exp:Expression) -> None:
        self._exp = exp

    def evaluate(self, trace:ComplexTrace, i:int) -> GuardOutcomes:
        """
        Evalutes the guard in the context of the given trace, before the i-th 
        event.
        """
        state = trace.get_state_as_of(i)
        outcome = self._exp.evaluate(state)
        return outcome
    
    def evaluate_data(self, data:Dict[str,object]) -> GuardOutcomes:
        """
        Evaluates the guard in the context of the given data state.
        """
        return self._exp.evaluate(data)

    def __str__(self) -> str:
        return str(self._exp)
    
    def __hash__(self) -> int:
        return self._exp.__hash__()
    
    def __eq__(self, other: object) -> bool:
        if(type(self) == type(other)):
            return hash(self) == hash(other)
        return False