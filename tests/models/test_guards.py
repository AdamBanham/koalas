import unittest

from pmkoalas.models.petrinets.guards import Expression, GuardOutcomes

LT_EXP = "d1 < 5"
LT_EXP2 = "d1 &lt; 5"
LTE_EXP = "d1 <= 5"
LTE_EXP2 = "d1 &lt;= 5"
GT_EXP = "d1 > 5"
GT_EXP2 = "d1 &gt; 5"
GTE_EXP = "d1 >= 5"
GTE_EXP2 = "d1 &gt;= 5"
EQ_EXP = "d1 == 5"
EQ_EXP2 = "d1 == 9"
LOG_AND = " && "
LOG_AND2 = " &amp;&amp; "
LOG_OR = " || "

LARGE_AND = "((d1 > 5) && (d1 > 6)) && (d1 < 9)"
LARGE_OR = "((d1 == 8)||(d1 == 7)||d1 == 9)||(d1==5)"

LARGE_COMB = "((d1 > 5) && (d1 <= 9)) || (d1 == 9)"

TEST_STATE = {
    'd1' : 5
}
TEST_STATE2 = {
    'd1' : 9
}
UNDEF_STATE = {
    'd1' : 'a'
}
UNDEF_STATE2 = {
    'z' : 5
}
LARGE_TEST_STATE = {
    'd1' : 7
}

# Difficult experession that should parse
d_exps = [
    "((exogenous:t1:TAS:4h:transform:slope&gt;41.44)&amp;&amp;(exogenous:t1:TAS:4h:transform:slope&lt;=105.84))",
]

class GuardTests(unittest.TestCase):

    def test_less_than(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(LT_EXP)
            exp2 = Expression(LT_EXP2) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # testing to ensure that less than is handled correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )

    def test_less_than_equal(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(LTE_EXP)
            exp2 = Expression(LTE_EXP2) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # testing to ensure that less than or equal is handled correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )

    def test_greater_than(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(GT_EXP)
            exp2 = Expression(GT_EXP2) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # testing to ensure that greater than is handled correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )

    def test_greater_than_equal(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(GTE_EXP)
            exp2 = Expression(GTE_EXP2) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # testing to ensure that greater than or equal is handled correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )

    def test_equal_to(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(EQ_EXP)
            exp2 = Expression(EQ_EXP2) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # testing to ensure equal to is handled correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        ) 

    def test_logical_and(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(GT_EXP + LOG_AND + LTE_EXP2)
            exp2 = Expression(LTE_EXP2 + LOG_AND2 + EQ_EXP) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e)) 
        # check to see if logical and is working correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        ) 

    def test_logical_or(self):
        exp = None 
        exp2 = None
        try:
            exp = Expression(GT_EXP + LOG_OR + LT_EXP2)
            exp2 = Expression(EQ_EXP + LOG_OR + EQ_EXP2) 
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e)) 
        # check to see if logical or is working correctly
        # equation type one
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )
        # equation type two
        out = exp2.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(TEST_STATE2)
        self.assertEqual(
            out, GuardOutcomes.TRUE, 
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE, 
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        )
        out = exp2.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF, 
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        )  

    def test_large_and(self):
        exp = None 
        try:
            exp = Expression(LARGE_AND)
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # attempt evaluation
        out = exp.evaluate(LARGE_TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE,
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        ) 
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE,
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        ) 
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF,
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        ) 

    def test_large_or(self):
        exp = None 
        try:
            exp = Expression(LARGE_OR)
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # attempt evaluation
        out = exp.evaluate(LARGE_TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE,
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        ) 
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE,
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        ) 
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF,
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        ) 
    
    def test_large_comb(self):
        exp = None 
        try:
            exp = Expression(LARGE_COMB)
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))
        # attempt evaluation
        out = exp.evaluate(LARGE_TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.TRUE,
            f"evaluation did not match, expected {GuardOutcomes.TRUE},"
            +f" but returned {out}"
        ) 
        out = exp.evaluate(TEST_STATE)
        self.assertEqual(
            out, GuardOutcomes.FALSE,
            f"evaluation did not match, expected {GuardOutcomes.FALSE},"
            +f" but returned {out}"
        ) 
        out = exp.evaluate(UNDEF_STATE2)
        self.assertEqual(
            out, GuardOutcomes.UNDEF,
            f"evaluation did not match, expected {GuardOutcomes.UNDEF},"
            +f" but returned {out}"
        ) 

    def test_difficult_expressions(self):
        try:
            for exp in d_exps:
                pexp = Expression(exp)
        except Exception as e:
            self.fail(f"failed to parse less than statement :: "+str(e))