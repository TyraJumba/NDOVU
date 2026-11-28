"""
NDOVU interpreter (Week 4).

Walks the AST and runs it. Variables live in a stack of scopes (one scope per
block). The semantic checker runs first, so the types are already known to be
safe when execution starts.
"""
from parser import (Program, If, While, Repeat, For, Declare, Assign, Output,
                    BinOp, UnaryOp, Number, String, Boolean, Var)


class RuntimeErr(Exception):
    """Error found while the program is running."""
    def __init__(self, line, sw, en):
        super().__init__(sw)
        self.sw = f"Kosa la wakati wa kukimbia (mstari {line}): {sw}"
        self.en = f"Runtime error (line {line}): {en}"
        self.line = line


def show(value):
    """How a value is printed."""
    if isinstance(value, bool):
        return "kweli" if value else "uongo"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(round(value, 10))
    return str(value)


def is_whole(n):
    return isinstance(n, int) or (isinstance(n, float) and n.is_integer())


class Interpreter:
    def __init__(self, output=print, max_steps=1_000_000):
        self.out = output
        self.max_steps = max_steps
        self.steps = 0
        self.scopes = []

    def run(self, program):
        self.scopes = [{}]
        self.steps = 0
        self.block(program.statements, new_scope=False)

    # --- scopes ---
    def block(self, statements, new_scope=True, preset=None):
        if new_scope:
            self.scopes.append(dict(preset or {}))
        try:
            for stmt in statements:
                self.execute(stmt)
        finally:
            if new_scope:
                self.scopes.pop()

    def tick(self, line):
        self.steps += 1
        if self.steps > self.max_steps:
            raise RuntimeErr(line,
                             f"kitanzi kinaonekana kutokuisha (zaidi ya {self.max_steps} marudio).",
                             f"the loop seems endless (more than {self.max_steps} repeats).")

    # --- statements ---
    def execute(self, s):
        if isinstance(s, Declare):
            self.scopes[-1][s.name] = self.evaluate(s.value)
        elif isinstance(s, Assign):
            value = self.evaluate(s.value)
            for scope in reversed(self.scopes):
                if s.name in scope:
                    scope[s.name] = value
                    break
        elif isinstance(s, Output):
            self.out(" ".join(show(self.evaluate(v)) for v in s.values))
        elif isinstance(s, If):
            if self.evaluate(s.condition):
                self.block(s.then_body)
            elif s.else_body is not None:
                self.block(s.else_body)
        elif isinstance(s, While):
            while self.evaluate(s.condition):
                self.tick(s.line)
                self.block(s.body)
        elif isinstance(s, Repeat):
            n = self.evaluate(s.count)
            if not is_whole(n) or n < 0:
                raise RuntimeErr(s.line,
                                 f"idadi ya 'rudia' lazima iwe namba kamili isiyo hasi (nimepata {show(n)}).",
                                 f"the count of 'rudia' must be a whole number, not negative (found {show(n)}).")
            for _ in range(int(n)):
                self.tick(s.line)
                self.block(s.body)
        elif isinstance(s, For):
            a, b = self.evaluate(s.start), self.evaluate(s.end)
            for v in (a, b):
                if not is_whole(v):
                    raise RuntimeErr(s.line,
                                     f"mipaka ya 'kwa' lazima iwe namba kamili (nimepata {show(v)}).",
                                     f"the limits of 'kwa' must be whole numbers (found {show(v)}).")
            for i in range(int(a), int(b) + 1):
                self.tick(s.line)
                self.block(s.body, preset={s.var: i})
        else:
            raise TypeError(f"unknown statement {s!r}")

    # --- expressions ---
    def evaluate(self, e):
        if isinstance(e, (Number, String)):
            return e.value
        if isinstance(e, Boolean):
            return e.value == "kweli"
        if isinstance(e, Var):
            for scope in reversed(self.scopes):
                if e.name in scope:
                    return scope[e.name]
            raise RuntimeErr(e.line, f"kigeu '{e.name}' hakipatikani.", f"variable '{e.name}' not found.")
        if isinstance(e, UnaryOp):
            v = self.evaluate(e.operand)
            return -v if e.op == "-" else not v
        if isinstance(e, BinOp):
            return self.binop(e)
        raise TypeError(f"unknown expression {e!r}")

    def binop(self, e):
        op = e.op
        if op == "na":
            return self.evaluate(e.left) and self.evaluate(e.right)
        if op == "au":
            return self.evaluate(e.left) or self.evaluate(e.right)
        a, b = self.evaluate(e.left), self.evaluate(e.right)
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise RuntimeErr(e.line, "huwezi kugawanya kwa sifuri.", "you cannot divide by zero.")
            result = a / b
            return int(result) if result.is_integer() else result
        return {">": a > b, "<": a < b, ">=": a >= b, "<=": a <= b,
                "==": a == b, "!=": a != b}[op]
