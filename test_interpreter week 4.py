"""Interpreter tests. Run from the project root:  python -m unittest discover tests"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from main import run_source                                   # noqa: E402
from parser import parse                                      # noqa: E402
from semantic import Checker                                  # noqa: E402
from interpreter import Interpreter, RuntimeErr               # noqa: E402
from lexer import LexError                                    # noqa: E402
from parser import ParseError                                 # noqa: E402
from semantic import SemanticError                            # noqa: E402


def run(src):
    lines = []
    run_source(src, output=lines.append)
    return lines


class Expressions(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(run("andika 1 + 2 * 3"), ["7"])

    def test_brackets(self):
        self.assertEqual(run("andika (1 + 2) * 3"), ["9"])

    def test_division_gives_decimals(self):
        self.assertEqual(run("andika 7 / 2"), ["3.5"])

    def test_whole_division_prints_without_decimals(self):
        self.assertEqual(run("andika 10 / 5"), ["2"])

    def test_decimal_rounding(self):
        self.assertEqual(run("andika 0.1 + 0.2"), ["0.3"])

    def test_unary_minus(self):
        self.assertEqual(run("andika -5 + 2"), ["-3"])

    def test_string_join(self):
        self.assertEqual(run('andika "Habari, " + "Amina"'), ["Habari, Amina"])

    def test_number_words(self):
        self.assertEqual(run("andika kumi na tano + ishirini"), ["35"])

    def test_booleans_print_in_swahili(self):
        self.assertEqual(run("andika 3 > 2, 3 < 2"), ["kweli uongo"])

    def test_logic_operators(self):
        self.assertEqual(run("andika kweli na uongo, kweli au uongo, si uongo"),
                         ["uongo kweli kweli"])

    def test_output_items_are_separated_by_a_space(self):
        self.assertEqual(run('andika "a", 1, "b"'), ["a 1 b"])


class Statements(unittest.TestCase):
    def test_variables(self):
        self.assertEqual(run("weka a = 4\nbadilisha a = a * 2\nandika a"), ["8"])

    def test_if_true_branch(self):
        self.assertEqual(run('kama 5 > 3 basi andika "A" vinginevyo andika "B" mwisho'), ["A"])

    def test_if_false_branch(self):
        self.assertEqual(run('kama 1 > 3 basi andika "A" vinginevyo andika "B" mwisho'), ["B"])

    def test_if_without_else_does_nothing(self):
        self.assertEqual(run('kama 1 > 3 basi andika "A" mwisho'), [])

    def test_while(self):
        self.assertEqual(run("weka n = 3\nwakati n > 0 basi\n andika n\n badilisha n = n - 1\nmwisho"),
                         ["3", "2", "1"])

    def test_repeat(self):
        self.assertEqual(run('rudia 2 mara andika "x" mwisho'), ["x", "x"])

    def test_repeat_zero_times(self):
        self.assertEqual(run('rudia 0 mara andika "x" mwisho'), [])

    def test_for_includes_both_ends(self):
        self.assertEqual(run("kwa i kutoka 2 hadi 4 basi andika i mwisho"), ["2", "3", "4"])

    def test_for_with_start_after_end_does_nothing(self):
        self.assertEqual(run("kwa i kutoka 5 hadi 1 basi andika i mwisho"), [])

    def test_variable_declared_inside_loop_is_new_each_time(self):
        self.assertEqual(run("rudia 2 mara\n weka t = 1\n andika t\nmwisho"), ["1", "1"])

    def test_nested_loops(self):
        src = "kwa i kutoka 1 hadi 2 basi\n kwa j kutoka 1 hadi 2 basi\n  andika i * j\n mwisho\nmwisho"
        self.assertEqual(run(src), ["1", "2", "2", "4"])


class RuntimeErrors(unittest.TestCase):
    def test_divide_by_zero(self):
        with self.assertRaises(RuntimeErr) as cm:
            run("andika 5 / 0")
        self.assertIn("kugawanya kwa sifuri", cm.exception.sw)

    def test_negative_repeat_count(self):
        with self.assertRaises(RuntimeErr) as cm:
            run("rudia 0 - 1 mara mwisho")
        self.assertIn("namba kamili isiyo hasi", cm.exception.sw)

    def test_fractional_repeat_count(self):
        with self.assertRaises(RuntimeErr):
            run("rudia 1.5 mara mwisho")

    def test_fractional_for_limit(self):
        with self.assertRaises(RuntimeErr):
            run("kwa i kutoka 1 hadi 2.5 basi mwisho")

    def test_endless_loop_is_stopped(self):
        tree = parse("wakati kweli basi\nmwisho")
        Checker().check(tree)
        with self.assertRaises(RuntimeErr) as cm:
            Interpreter(output=lambda s: None, max_steps=1000).run(tree)
        self.assertIn("kutokuisha", cm.exception.sw)

    def test_output_before_the_error_is_kept(self):
        lines = []
        with self.assertRaises(RuntimeErr):
            run_source('andika "kwanza"\nandika 1 / 0', output=lines.append)
        self.assertEqual(lines, ["kwanza"])

    def test_error_line_number(self):
        with self.assertRaises(RuntimeErr) as cm:
            run("weka a = 1\nweka b = 0\nandika a / b")
        self.assertEqual(cm.exception.line, 3)


EXPECTED = {
    "01_habari": ["Habari Dunia!"],
    "02_hesabu": ["Jumla ni 1000"],
    "03_umri": ["Mtu mzima"],
    "04_daraja": ["Daraja B"],
    "05_salamu": ["Karibu!", "Karibu!", "Karibu!"],
    "06_hesabu_nyuma": ["5", "4", "3", "2", "1", "Imekwisha!"],
    "07_maneno_ya_namba": ["Umri: 15", "Jumla: 36"],
    "08_mantiki": ["Unaruhusiwa kupiga kura", "Bei kamili"],
    "09_jedwali": ["1 x 3 = 3", "2 x 3 = 6", "3 x 3 = 9", "4 x 3 = 12", "5 x 3 = 15"],
    "10_jumla": ["Habari, Amina!", "Jumla ya 1 hadi 10 ni 55"],
}


class ExampleFiles(unittest.TestCase):
    def _read(self, folder, name):
        with open(os.path.join(ROOT, "examples", folder, name), encoding="utf-8") as f:
            return f.read()

    def test_valid_programs_give_the_expected_output(self):
        for name, expected in EXPECTED.items():
            with self.subTest(program=name):
                self.assertEqual(run(self._read("valid", name + ".ndovu")), expected)

    def test_invalid_programs_fail_at_the_right_stage(self):
        stage = {"lexical_": LexError, "syntax_": ParseError,
                 "semantic_": SemanticError, "runtime_": RuntimeErr}
        path = os.path.join(ROOT, "examples", "invalid")
        for name in sorted(os.listdir(path)):
            for prefix, error_type in stage.items():
                if name.startswith(prefix):
                    with self.subTest(program=name):
                        with self.assertRaises(error_type):
                            run(self._read("invalid", name))

    def test_semantic_error_stops_everything_before_output(self):
        lines = []
        with self.assertRaises(SemanticError):
            run_source('andika "hii haitaonekana"\nandika mshahara', output=lines.append)
        self.assertEqual(lines, [])


if __name__ == "__main__":
    unittest.main()
