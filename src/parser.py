from lexer import Lexer


# AST (Abstract Syntax Tree) Nodes
class ASTNode:
    def tree(self, indent=0):
        return "  " * indent + self.__class__.__name__


class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def tree(self, indent=0):
        lines = ["  " * indent + "Program"]
        for stmt in self.statements:
            lines.append(stmt.tree(indent + 1))
        return "\n".join(lines)


class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def tree(self, indent=0):
        lines = ["  " * indent + f"Assign (WEKA {self.name})"]
        lines.append(self.value.tree(indent + 1))
        return "\n".join(lines)


class OutputNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def tree(self, indent=0):
        lines = ["  " * indent + "Output (ONYESHA)"]
        lines.append(self.expression.tree(indent + 1))
        return "\n".join(lines)


class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def tree(self, indent=0):
        lines = ["  " * indent + "Conditional (KAMA)"]
        lines.append("  " * (indent + 1) + "Condition:")
        lines.append(self.condition.tree(indent + 2))
        lines.append("  " * (indent + 1) + "Then:")
        for stmt in self.then_body:
            lines.append(stmt.tree(indent + 2))
        if self.else_body:
            lines.append("  " * (indent + 1) + "Else (VINGINEVYO):")
            for stmt in self.else_body:
                lines.append(stmt.tree(indent + 2))
        return "\n".join(lines)


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def tree(self, indent=0):
        lines = ["  " * indent + "WhileLoop (WAKATI)"]
        lines.append("  " * (indent + 1) + "Condition:")
        lines.append(self.condition.tree(indent + 2))
        lines.append("  " * (indent + 1) + "Body:")
        for stmt in self.body:
            lines.append(stmt.tree(indent + 2))
        return "\n".join(lines)


class RepeatNode(ASTNode):
    def __init__(self, count, body):
        self.count = count
        self.body = body

    def tree(self, indent=0):
        lines = ["  " * indent + f"RepeatLoop (RUDIA {self.count})"]
        for stmt in self.body:
            lines.append(stmt.tree(indent + 1))
        return "\n".join(lines)


class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def tree(self, indent=0):
        lines = ["  " * indent + f"BinOp ({self.op})"]
        lines.append(self.left.tree(indent + 1))
        lines.append(self.right.tree(indent + 1))
        return "\n".join(lines)


class LiteralNode(ASTNode):
    def __init__(self, value, literal_type):
        self.value = value
        self.literal_type = literal_type

    def tree(self, indent=0):
        return "  " * indent + f"{self.literal_type}({self.value!r})"


class VarNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def tree(self, indent=0):
        return "  " * indent + f"Var({self.name})"


# Parser (Recursive Descent)
class NdovuSyntaxError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def is_eof(self):
        tok = self.current()
        return tok is None or getattr(tok, "type", "") == "EOF"

    def advance(self):
        tok = self.current()
        self.pos += 1
        return tok

    def error(self, message, tok=None):
        tok = tok or self.current()
        if tok is not None:
            line = getattr(tok, "line", "?")
            col = getattr(tok, "column", "?")
            raise NdovuSyntaxError(f"Syntax Error at line {line}, column {col}: {message}")
        raise NdovuSyntaxError(f"Syntax Error at end of file: {message}")

    def expect_value(self, expected_val):
        tok = self.current()
        if tok is None or tok.value != expected_val:
            found = tok.value if tok else "EOF"
            self.error(f"Expected '{expected_val}', but found '{found}'")
        return self.advance()

    # <program> ::= <statement_list> EOF
    def parse(self):
        statements = []
        while not self.is_eof():
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    # <statement> ::= <assignment> | <output> | <conditional> | <while_loop> | <repeat_loop>
    def parse_statement(self):
        tok = self.current()
        if tok.value == "WEKA":
            return self.parse_assignment()
        elif tok.value == "ONYESHA":
            return self.parse_output()
        elif tok.value == "KAMA":
            return self.parse_conditional()
        elif tok.value == "WAKATI":
            return self.parse_while()
        elif tok.value == "RUDIA":
            return self.parse_repeat()
        else:
            self.error(f"Unexpected token '{tok.value}'. Expected a statement (WEKA, ONYESHA, KAMA, WAKATI, RUDIA).")

    # <assignment> ::= "WEKA" <identifier> "=" <expression>
    def parse_assignment(self):
        self.expect_value("WEKA")
        ident = self.current()
        if ident is None or ident.type not in ("IDENTIFIER", "ID"):
            found = ident.value if ident else "EOF"
            self.error(f"Expected variable name after 'WEKA', but found '{found}'")
        self.advance()
        self.expect_value("=")
        expr = self.parse_expression()
        return AssignNode(ident.value, expr)

    # <output> ::= "ONYESHA" <expression>
    def parse_output(self):
        self.expect_value("ONYESHA")
        expr = self.parse_expression()
        return OutputNode(expr)

    # <conditional> ::= "KAMA" <comparison> "{" <statement_list> "}" [ "VINGINEVYO" "{" <statement_list> "}" ]
    def parse_conditional(self):
        self.expect_value("KAMA")
        condition = self.parse_comparison()
        then_body = self.parse_block()
        else_body = None

        if not self.is_eof() and self.current().value == "VINGINEVYO":
            self.advance()
            else_body = self.parse_block()

        return IfNode(condition, then_body, else_body)

    # <while_loop> ::= "WAKATI" <comparison> "{" <statement_list> "}"
    def parse_while(self):
        self.expect_value("WAKATI")
        condition = self.parse_comparison()
        body = self.parse_block()
        return WhileNode(condition, body)

    # <repeat_loop> ::= "RUDIA" <number> "{" <statement_list> "}"
    def parse_repeat(self):
        self.expect_value("RUDIA")
        num_tok = self.current()
        if num_tok is None or num_tok.type not in ("NUMBER", "INT", "FLOAT"):
            found = num_tok.value if num_tok else "EOF"
            self.error(f"Expected a number after 'RUDIA', but found '{found}'")
        self.advance()
        body = self.parse_block()
        return RepeatNode(num_tok.value, body)

    def parse_block(self):
        self.expect_value("{")
        statements = []
        while not self.is_eof() and self.current().value != "}":
            statements.append(self.parse_statement())
        self.expect_value("}")
        return statements

    # <comparison> ::= <expression> <comp_op> <expression>
    def parse_comparison(self):
        left = self.parse_expression()
        tok = self.current()
        if tok is None or tok.value not in ("==", "!=", ">", "<", ">=", "<="):
            found = tok.value if tok else "EOF"
            self.error(f"Expected comparison operator (==, !=, >, <, >=, <=), but found '{found}'")
        op = self.advance().value
        right = self.parse_expression()
        return BinOpNode(left, op, right)

    # <expression> ::= <term> ( ("+" | "-") <term> )*
    def parse_expression(self):
        node = self.parse_term()
        while not self.is_eof() and self.current().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_term()
            node = BinOpNode(node, op, right)
        return node

    # <term> ::= <factor> ( ("*" | "/") <factor> )*
    def parse_term(self):
        node = self.parse_factor()
        while not self.is_eof() and self.current().value in ("*", "/"):
            op = self.advance().value
            right = self.parse_factor()
            node = BinOpNode(node, op, right)
        return node

    # <factor> ::= <number> | <string> | <boolean> | <identifier> | "(" <expression> ")"
    def parse_factor(self):
        tok = self.current()
        if tok is None:
            self.error("Unexpected end of file while reading expression")

        if tok.type in ("NUMBER", "INT", "FLOAT"):
            self.advance()
            return LiteralNode(tok.value, "Number")
        elif tok.type in ("STRING", "STR"):
            self.advance()
            return LiteralNode(tok.value, "String")
        elif tok.value in ("KWELI", "UONGO"):
            self.advance()
            return LiteralNode(tok.value, "Boolean")
        elif tok.type in ("IDENTIFIER", "ID"):
            self.advance()
            return VarNode(tok.value)
        elif tok.value == "(":
            self.advance()
            node = self.parse_expression()
            self.expect_value(")")
            return node
        else:
            self.error(f"Unexpected token '{tok.value}' in expression")


# Syntax Tests & AST Demo
if __name__ == "__main__":
    valid_code = """
    WEKA alama = 80
    KAMA alama >= 50 {
        ONYESHA "Umefaulu"
    } VINGINEVYO {
        ONYESHA "Jaribu tena"
    }
    """

    invalid_code = """
    WEKA umri 20
    """

    print("VALID PROGRAM AST:")
    tokens = Lexer(valid_code).make_tokens()
    ast = Parser(tokens).parse()
    print(ast.tree())

    print("\nINVALID PROGRAM TEST:")
    try:
        bad_tokens = Lexer(invalid_code).make_tokens()
        Parser(bad_tokens).parse()
    except NdovuSyntaxError as e:
        print(f"CAUGHT EXPECTED ERROR: {e}")