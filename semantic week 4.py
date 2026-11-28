"""
NDOVU semantic checker .

Walks the AST before anything runs and checks that variables are declared
and that values are used with the right types. Types: number, string, boolean.
"""
from parser import (If, While, Repeat, For, Declare, Assign, Output,
                    BinOp, UnaryOp, Number, String, Boolean, Var)

TYPE_SW = {"number": "namba", "string": "neno", "boolean": "kweli/uongo"}


class SemanticError(Exception):
    """Semantic or type error with a Kiswahili message and an English meaning."""
    def __init__(self, kind, line, sw, en):
        label_sw, label_en = (("Kosa la maana", "Semantic error") if kind == "maana"
                              else ("Kosa la aina", "Type error"))
        super().__init__(sw)
        self.sw = f"{label_sw} (mstari {line}): {sw}"
        self.en = f"{label_en} (line {line}): {en}"
        self.kind, self.line = kind, line


class Checker:
    def __init__(self):
        self.scopes = []          # a stack of {name: (type, readonly, line)}

    def check(self, program):
        self.scopes = [{}]
        self.block(program.statements, new_scope=False)

    # --- symbol table ---
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def declare(self, name, tp, line, readonly=False):
        old = self.lookup(name)
        if old:
            raise SemanticError("maana", line,
                                f"kigeu '{name}' kimeshatangazwa tayari (mstari {old[2]}).",
                                f"variable '{name}' is already declared (line {old[2]}).")
        self.scopes[-1][name] = (tp, readonly, line)

    # --- statements ---
    def block(self, statements, new_scope=True, preset=None):
        if new_scope:
            self.scopes.append({})
        for name, entry in (preset or {}).items():
            self.scopes[-1][name] = entry
        for stmt in statements:
            self.statement(stmt)
        if new_scope:
            self.scopes.pop()

    def statement(self, s):
        if isinstance(s, Declare):
            tp = self.infer(s.value)                 # check the value first
            self.declare(s.name, tp, s.line)
        elif isinstance(s, Assign):
            entry = self.lookup(s.name)
            if entry is None:
                raise SemanticError("maana", s.line,
                                    f"kigeu '{s.name}' hakijatangazwa. Tumia 'weka' kwanza.",
                                    f"variable '{s.name}' is not declared. Use 'weka' first.")
            if entry[1]:
                raise SemanticError("maana", s.line,
                                    f"'{s.name}' ni kigeu cha kitanzi cha 'kwa' na hakiwezi kubadilishwa.",
                                    f"'{s.name}' is a 'kwa' loop variable and cannot be changed.")
            new = self.infer(s.value)
            if new != entry[0]:
                raise SemanticError("aina", s.line,
                                    f"kigeu '{s.name}' ni {TYPE_SW[entry[0]]}, huwezi kukibadilisha kuwa {TYPE_SW[new]}.",
                                    f"variable '{s.name}' is a {entry[0]}; you cannot change it to a {new}.")
        elif isinstance(s, Output):
            for v in s.values:
                self.infer(v)
        elif isinstance(s, If):
            self.need_condition(s.condition, "kama", s.line)
            self.block(s.then_body)
            if s.else_body is not None:
                self.block(s.else_body)
        elif isinstance(s, While):
            self.need_condition(s.condition, "wakati", s.line)
            self.block(s.body)
        elif isinstance(s, Repeat):
            tp = self.infer(s.count)
            if tp != "number":
                raise SemanticError("aina", s.line,
                                    f"idadi ya 'rudia' lazima iwe namba, lakini nimepata {TYPE_SW[tp]}.",
                                    f"the count of 'rudia' must be a number, but found {tp}.")
            self.block(s.body)
        elif isinstance(s, For):
            for bound in (s.start, s.end):
                tp = self.infer(bound)
                if tp != "number":
                    raise SemanticError("aina", s.line,
                                        f"mipaka ya 'kwa' lazima iwe namba, lakini nimepata {TYPE_SW[tp]}.",
                                        f"the limits of 'kwa' must be numbers, but found {tp}.")
            if self.lookup(s.var):
                old = self.lookup(s.var)
                raise SemanticError("maana", s.line,
                                    f"kigeu '{s.var}' kimeshatangazwa tayari (mstari {old[2]}).",
                                    f"variable '{s.var}' is already declared (line {old[2]}).")
            self.block(s.body, preset={s.var: ("number", True, s.line)})

    def need_condition(self, expr, kw, line):
        tp = self.infer(expr)
        if tp != "boolean":
            raise SemanticError("aina", line,
                                f"sharti la '{kw}' lazima liwe kweli au uongo, lakini nimepata {TYPE_SW[tp]}.",
                                f"the condition of '{kw}' must be true or false, but found {tp}.")

    # --- expressions: return the type ---
    def infer(self, e):
        if isinstance(e, Number):
            return "number"
        if isinstance(e, String):
            return "string"
        if isinstance(e, Boolean):
            return "boolean"
        if isinstance(e, Var):
            entry = self.lookup(e.name)
            if entry is None:
                raise SemanticError("maana", e.line,
                                    f"kigeu '{e.name}' hakijatangazwa. Tumia 'weka' kwanza.",
                                    f"variable '{e.name}' is not declared. Use 'weka' first.")
            return entry[0]
        if isinstance(e, UnaryOp):
            tp = self.infer(e.operand)
            want = "number" if e.op == "-" else "boolean"
            if tp != want:
                raise SemanticError("aina", e.line,
                                    f"'{e.op}' inahitaji {TYPE_SW[want]}, lakini nimepata {TYPE_SW[tp]}.",
                                    f"'{e.op}' needs a {want}, but found {tp}.")
            return want
        if isinstance(e, BinOp):
            return self.binop(e)
        raise TypeError(f"unknown expression {e!r}")

    def binop(self, e):
        a, b = self.infer(e.left), self.infer(e.right)
        op = e.op

        def bad(sw, en):
            raise SemanticError("aina", e.line, sw, en)

        if op == "+":
            if a == b and a in ("number", "string"):
                return a
            if a != b:
                bad(f"huwezi kujumlisha {TYPE_SW[a]} na {TYPE_SW[b]}.",
                    f"you cannot add a {a} and a {b}.")
            bad("'+' haiwezi kutumika kwa kweli/uongo.", "'+' cannot be used with booleans.")
        if op in ("-", "*", "/", ">", "<", ">=", "<="):
            if a != "number" or b != "number":
                bad(f"'{op}' inahitaji namba pande zote mbili, lakini nimepata {TYPE_SW[a]} na {TYPE_SW[b]}.",
                    f"'{op}' needs numbers on both sides, but found {a} and {b}.")
            return "number" if op in "-*/" else "boolean"
        if op in ("==", "!="):
            if a != b:
                bad(f"'{op}' inalinganisha thamani za aina moja tu, lakini nimepata {TYPE_SW[a]} na {TYPE_SW[b]}.",
                    f"'{op}' compares values of the same type, but found {a} and {b}.")
            return "boolean"
        if op in ("na", "au"):
            if a != "boolean" or b != "boolean":
                bad(f"'{op}' inahitaji kweli/uongo pande zote mbili, lakini nimepata {TYPE_SW[a]} na {TYPE_SW[b]}.",
                    f"'{op}' needs true/false on both sides, but found {a} and {b}.")
            return "boolean"
        raise TypeError(f"unknown operator {op}")
