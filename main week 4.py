"""
NDOVU main program (Week 4): lexer -> parser -> semantic checks -> interpreter.

Usage:  python src/main.py program.ndovu [--tokens] [--ast]
"""
import sys

from lexer import tokenize, format_tokens, LexError
from parser import Parser, format_ast, ParseError
from semantic import Checker, SemanticError
from interpreter import Interpreter, RuntimeErr

ERRORS = (LexError, ParseError, SemanticError, RuntimeErr)


def run_source(source, output=print, show_tokens=False, show_ast=False):
    tokens = tokenize(source)                       # 1. characters -> tokens
    if show_tokens:
        output(format_tokens(tokens))
    tree = Parser(tokens).parse_program()           # 2. tokens -> AST
    if show_ast:
        output("\n".join(format_ast(tree)))
    Checker().check(tree)                           # 3. semantic checks
    Interpreter(output).run(tree)                   # 4. execution


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != 1:
        print("Usage: python src/main.py <file.ndovu> [--tokens] [--ast]")
        sys.exit(2)
    with open(args[0], encoding="utf-8") as f:
        source = f.read()
    try:
        run_source(source, show_tokens="--tokens" in flags, show_ast="--ast" in flags)
    except ERRORS as e:
        print(e.sw)
        print(e.en)
        sys.exit(1)
