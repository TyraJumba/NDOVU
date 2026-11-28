"""Semantic check tests. Run from the project root:  python -m unittest discover tests"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from parser import parse                          # noqa: E402
from semantic import Checker, SemanticError       # noqa: E402


def check(src):
    Checker().check(parse(src))


def error(src):
    try:
        check(src)
    except SemanticError as e:
        return e
    raise AssertionError("expected a SemanticError")


class ValidPrograms(unittest.TestCase):
    def test_declare_then_use(self):
        check("weka a = 1\nandika a")

    def test_assign_same_type(self):
        check('weka a = 1\nbadilisha a = a + 1\nweka s = "x"\nbadilisha s = s + "y"')

    def test_inner_block_can_use_outer_variable(self):
        check("weka n = 1\nkama n > 0 basi\n    badilisha n = n - 1\nmwisho")

    def test_loop_variable_inside_loop(self):
        check("kwa i kutoka 1 hadi 3 basi\n    andika i * 2\nmwisho")

    def test_loop_variable_can_be_reused_after_loop(self):
        check("kwa i kutoka 1 hadi 2 basi\nmwisho\nkwa i kutoka 1 hadi 2 basi\nmwisho")

    def test_same_name_in_separate_blocks(self):
        check("kama kweli basi weka x = 1 mwisho\nkama kweli basi weka x = 2 mwisho")

    def test_equality_of_same_types(self):
        check('andika "a" == "b", 1 != 2, kweli == uongo')

    def test_all_valid_examples(self):
        path = os.path.join(ROOT, "examples", "valid")
        for name in sorted(os.listdir(path)):
            with self.subTest(file=name):
                with open(os.path.join(path, name), encoding="utf-8") as f:
                    check(f.read())


class DeclarationErrors(unittest.TestCase):
    def test_use_before_declaration(self):
        e = error("andika mshahara")
        self.assertIn("hakijatangazwa", e.sw)
        self.assertEqual(e.line, 1)

    def test_assign_before_declaration(self):
        self.assertIn("hakijatangazwa", error("badilisha x = 5").sw)

    def test_declared_twice(self):
        e = error("weka a = 1\nweka a = 2")
        self.assertIn("kimeshatangazwa tayari", e.sw)
        self.assertEqual(e.line, 2)

    def test_variable_in_its_own_value(self):
        self.assertIn("hakijatangazwa", error("weka x = x + 1").sw)

    def test_variable_not_visible_outside_its_block(self):
        e = error("kama kweli basi\n    weka x = 1\nmwisho\nandika x")
        self.assertIn("'x' hakijatangazwa", e.sw)

    def test_loop_variable_not_visible_after_loop(self):
        self.assertIn("hakijatangazwa", error("kwa i kutoka 1 hadi 2 basi mwisho\nandika i").sw)

    def test_loop_variable_cannot_be_changed(self):
        self.assertIn("hakiwezi kubadilishwa", error("kwa i kutoka 1 hadi 3 basi badilisha i = 5 mwisho").sw)

    def test_loop_variable_cannot_reuse_existing_name(self):
        self.assertIn("kimeshatangazwa tayari", error("weka i = 0\nkwa i kutoka 1 hadi 2 basi mwisho").sw)

    def test_english_message(self):
        self.assertIn("is not declared", error("andika y").en)


class TypeErrors(unittest.TestCase):
    def test_add_string_and_number(self):
        e = error('weka a = "tano" + 5')
        self.assertEqual(e.kind, "aina")
        self.assertIn("huwezi kujumlisha neno na namba", e.sw)

    def test_arithmetic_on_string(self):
        self.assertIn("inahitaji namba", error('andika "a" * 2').sw)

    def test_compare_number_with_string(self):
        self.assertIn("inahitaji namba", error('andika 1 < "a"').sw)

    def test_equality_of_different_types(self):
        self.assertIn("aina moja tu", error('andika 1 == "1"').sw)

    def test_logic_on_numbers(self):
        self.assertIn("kweli/uongo pande zote mbili", error("andika 1 na 2").sw)

    def test_not_on_number(self):
        self.assertIn("'si' inahitaji", error("andika si 5").sw)

    def test_condition_must_be_boolean(self):
        self.assertIn("sharti la 'kama'", error("kama 5 basi mwisho").sw)
        self.assertIn("sharti la 'wakati'", error('wakati "a" basi mwisho').sw)

    def test_repeat_count_must_be_number(self):
        self.assertIn("idadi ya 'rudia'", error('rudia "a" mara mwisho').sw)

    def test_for_limits_must_be_numbers(self):
        self.assertIn("mipaka ya 'kwa'", error('kwa i kutoka 1 hadi "a" basi mwisho').sw)

    def test_assignment_cannot_change_type(self):
        e = error('weka a = 5\nbadilisha a = "tano"')
        self.assertIn("huwezi kukibadilisha kuwa neno", e.sw)
        self.assertEqual(e.line, 2)


class ExampleFiles(unittest.TestCase):
    def test_semantic_examples_are_rejected(self):
        path = os.path.join(ROOT, "examples", "invalid")
        for name in sorted(os.listdir(path)):
            if name.startswith("semantic_"):
                with self.subTest(file=name):
                    with open(os.path.join(path, name), encoding="utf-8") as f:
                        with self.assertRaises(SemanticError):
                            check(f.read())


if __name__ == "__main__":
    unittest.main()
