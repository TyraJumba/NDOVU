import os
import sys

# Allow importing from the src folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from lexer import Lexer
from parser import Parser, NdovuSyntaxError


def run_valid_test(title, code):
    print(f"--- VALID TEST: {title} ---")
    tokens = Lexer(code).make_tokens()
    ast = Parser(tokens).parse()
    print(ast.tree())
    print("RESULT: PASSED\n")


def run_invalid_test(title, code):
    print(f"--- INVALID TEST: {title} ---")
    try:
        tokens = Lexer(code).make_tokens()
        Parser(tokens).parse()
        print("RESULT: FAILED (Expected a syntax error, but none was raised)\n")
    except NdovuSyntaxError as e:
        print(f"CAUGHT ERROR: {e}")
        print("RESULT: PASSED\n")


if __name__ == "__main__":
    # 1. Valid Tests
    run_valid_test(
        "Assignment & BODMAS Precedence",
        """
        WEKA matokeo = 10 + 5 * 2
        ONYESHA matokeo
        """
    )

    run_valid_test(
        "Conditional (KAMA / VINGINEVYO)",
        """
        WEKA alama = 75
        KAMA alama >= 50 {
            ONYESHA "Umefaulu"
        } VINGINEVYO {
            ONYESHA "Jaribu tena"
        }
        """
    )

    run_valid_test(
        "While Loop (WAKATI)",
        """
        WEKA i = 1
        WAKATI i <= 3 {
            ONYESHA i
            WEKA i = i + 1
        }
        """
    )

    run_valid_test(
        "Repeat Loop (RUDIA)",
        """
        RUDIA 3 {
            ONYESHA "Karibu Ndovu"
        }
        """
    )

    # 2. Invalid Tests (Must raise NdovuSyntaxError)
    run_invalid_test(
        "Missing '=' in WEKA",
        "WEKA umri 20"
    )

    run_invalid_test(
        "Missing closing brace '}'",
        """
        KAMA 10 > 5 {
            ONYESHA "Kweli"
        """
    )

    run_invalid_test(
        "Missing comparison operator in WAKATI",
        """
        WAKATI alama 50 {
            ONYESHA alama
        }
        """
    )

    run_invalid_test(
        "Non-number after RUDIA",
        """
        RUDIA "tatu" {
            ONYESHA "Hujambo"
        }
        """
    )