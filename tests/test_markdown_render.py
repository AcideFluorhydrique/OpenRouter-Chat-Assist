# -*- coding: utf-8 -*-
import unittest

from markdown_render import latex_to_unicode, render_markdown


class LatexTest(unittest.TestCase):
    def test_conversions(self):
        cases = {
            r"x^2 + y^2 = r^2": "x² + y² = r²",
            r"\frac{a+b}{2}": "(a+b)/2",
            r"\sqrt{x^2+1}": "√(x²+1)",
            r"\sum_{i=1}^{n} i": "∑ᵢ₌₁ⁿ i",
            r"a \leq b \neq c": "a ≤ b ≠ c",
            r"x \in \mathbb{R}": "x ∈ ℝ",
            r"90^\circ": "90°",
            r"e^{i\pi}": "e^(iπ)",
        }
        for src, expected in cases.items():
            self.assertEqual(latex_to_unicode(src), expected, src)

    def test_matrix_is_laid_out_next_to_text(self):
        lines = latex_to_unicode(r"A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}").split("\n")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("A = ⎛"))


class MarkdownTest(unittest.TestCase):
    def tagged(self, text, tag):
        return [t for t, tags in render_markdown(text) if tag in tags]

    def test_inline_math_is_not_italic(self):
        self.assertEqual(self.tagged("见 $a_1 * b_2 * c$ 处", "math"), ["a₁ * b₂ * c"])
        self.assertEqual(self.tagged("见 $a_1 * b_2 * c$ 处", "italic"), [])

    def test_currency_is_not_math(self):
        self.assertEqual(self.tagged("花了 $5 和 $10", "math"), [])

    def test_snake_case_is_not_italic(self):
        self.assertEqual(self.tagged("snake_case_name", "italic"), [])

    def test_display_math(self):
        self.assertEqual(self.tagged("$$\n\\frac{1}{2}\n$$", "math_block"), ["1/2\n"])
        self.assertEqual(self.tagged("\\[ x^2 \\]", "math_block"), ["x²\n"])

    def test_code_is_untouched(self):
        self.assertEqual(self.tagged("```\na*b*c $x$\n```", "code_block"), ["a*b*c $x$\n"])

    def test_numbered_and_nested_lists(self):
        segments = render_markdown("1. one\n   - sub")
        self.assertEqual(segments[0], ("1. ", ("list0",)))
        self.assertIn(("◦ ", ("list1",)), segments)

    def test_bold_inside_list_and_heading(self):
        self.assertEqual(self.tagged("- **a**\n# **b**", "bold"), ["a", "b"])

    def test_table(self):
        rows = self.tagged("| a | b |\n|---|---|\n| 1 | $x^2$ |", "table")
        self.assertEqual(rows[0], "a\tb\n")
        self.assertEqual(rows[2], "1\tx²\n")


if __name__ == "__main__":
    unittest.main()
