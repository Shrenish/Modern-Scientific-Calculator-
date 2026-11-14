"""
Comprehensive Test Suite for Scientific Calculator & Math Assistant
===================================================================
"""

import math
import unittest
from engine.calc_core import CalcEngine, MatrixEngine, StatsEngine, compile_math_expr
from engine.converters import UnitConverter, PHYSICAL_CONSTANTS
from engine.ai_engine import LocalMathSolver, CloudMathAI, AIResult


class TestCalcEngine(unittest.TestCase):
    def setUp(self):
        self.calc = CalcEngine()

    def test_basic_arithmetic(self):
        self.assertEqual(self.calc.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.calc.evaluate("(10 - 2) / 4"), 2)
        self.assertEqual(self.calc.evaluate("2^3"), 8)

    def test_angle_modes(self):
        self.calc.angle_mode = CalcEngine.DEG
        self.assertAlmostEqual(self.calc.evaluate("sin(90)"), 1.0)
        self.assertAlmostEqual(self.calc.evaluate("cos(0)"), 1.0)
        self.calc.angle_mode = CalcEngine.RAD
        self.assertAlmostEqual(self.calc.evaluate("sin(pi/2)"), 1.0)
        self.assertAlmostEqual(self.calc.evaluate("cos(pi)"), -1.0)

    def test_scientific_functions(self):
        self.assertEqual(self.calc.evaluate("sqrt(16)"), 4)
        self.assertEqual(self.calc.evaluate("cbrt(27)"), 3)
        self.assertEqual(self.calc.evaluate("log(100)"), 2)
        self.assertAlmostEqual(self.calc.evaluate("ln(e)"), 1.0)
        self.assertEqual(self.calc.evaluate("factorial(5)"), 120)

    def test_implicit_multiplication(self):
        self.assertAlmostEqual(self.calc.evaluate("2pi"), 2 * math.pi)
        self.assertEqual(self.calc.evaluate("3(2+4)"), 18)
        self.assertEqual(self.calc.evaluate("(2+3)(4+1)"), 25)

    def test_percentages(self):
        self.assertAlmostEqual(self.calc.evaluate("50 + 10%"), 55.0)
        self.assertAlmostEqual(self.calc.evaluate("100 - 20%"), 80.0)
        self.assertAlmostEqual(self.calc.evaluate("25%"), 0.25)

    def test_number_theory(self):
        self.assertTrue(self.calc.is_prime(97))
        self.assertFalse(self.calc.is_prime(100))
        self.assertEqual(self.calc.factors(12), [1, 2, 3, 4, 6, 12])
        self.assertEqual(self.calc.fibonacci(10), 55)
        self.assertEqual(self.calc.evaluate("gcd(48, 64)"), 16)
        self.assertEqual(self.calc.evaluate("lcm(12, 18)"), 36)

    def test_memory(self):
        self.calc.store_memory(50)
        self.assertEqual(self.calc.mem_recall(), 50)
        self.calc.mem_add(25)
        self.assertEqual(self.calc.mem_recall(), 75)
        self.calc.mem_sub(15)
        self.assertEqual(self.calc.mem_recall(), 60)
        self.calc.mem_clear()
        self.assertEqual(self.calc.mem_recall(), 0)


class TestMatrixEngine(unittest.TestCase):
    def test_det2_and_inv2(self):
        m = [[4, 7], [2, 6]]
        det = MatrixEngine.det2(m)
        self.assertAlmostEqual(det, 10.0)
        inv = MatrixEngine.inverse2(m)
        prod = MatrixEngine.multiply(m, inv)
        for i in range(2):
            for j in range(2):
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(prod[i][j], expected)

    def test_det3_and_inv3(self):
        m = [[1, 2, 3], [0, 1, 4], [5, 6, 0]]
        det = MatrixEngine.det3(m)
        self.assertAlmostEqual(det, 1.0)
        inv = MatrixEngine.inverse3(m)
        prod = MatrixEngine.multiply(m, inv)
        for i in range(3):
            for j in range(3):
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(prod[i][j], expected)


class TestStatsEngine(unittest.TestCase):
    def test_descriptive_stats(self):
        data = [2, 4, 4, 4, 5, 5, 7, 9]
        res = StatsEngine.analyze(data)
        self.assertEqual(res["count"], 8)
        self.assertEqual(res["mean"], 5.0)
        self.assertEqual(res["median"], 4.5)
        self.assertEqual(res["mode"], 4)
        self.assertEqual(res["min"], 2)
        self.assertEqual(res["max"], 9)
        self.assertEqual(res["range"], 7)

    def test_linear_regression(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        reg = StatsEngine.linear_regression(x, y)
        self.assertAlmostEqual(reg["slope"], 2.0)
        self.assertAlmostEqual(reg["intercept"], 0.0)
        self.assertAlmostEqual(reg["correlation_r"], 1.0)


class TestUnitConverter(unittest.TestCase):
    def test_conversions(self):
        self.assertAlmostEqual(UnitConverter.convert(1, "Length", "Kilometer (km)", "Meter (m)"), 1000.0)
        self.assertAlmostEqual(UnitConverter.convert(0, "Temperature", "Celsius (°C)", "Fahrenheit (°F)"), 32.0)
        self.assertAlmostEqual(UnitConverter.convert(100, "Temperature", "Celsius (°C)", "Fahrenheit (°F)"), 212.0)
        self.assertAlmostEqual(UnitConverter.convert(1, "Digital Data", "Gigabyte (GB, 10⁹)", "Megabyte (MB, 10⁶)"), 1000.0)

    def test_physical_constants(self):
        symbols = [c.symbol for c in PHYSICAL_CONSTANTS]
        self.assertIn("c", symbols)
        self.assertIn("h", symbols)
        self.assertIn("G", symbols)
        self.assertIn("N_A", symbols)
        self.assertIn("k_B", symbols)


class TestLocalMathSolver(unittest.TestCase):
    def setUp(self):
        self.solver = LocalMathSolver()

    def test_linear_equation(self):
        res = self.solver.solve("solve 2x + 5 = 15")
        self.assertEqual(res.answer, "x = 5")

    def test_concept_calculus(self):
        res = self.solver.solve("what is calculus")
        self.assertIn("Fundamental", res.summary)

    def test_derivative_nlp(self):
        res = self.solver.solve("derivative of 3x^2 + 5x")
        self.assertEqual(res.answer, "6x +5")

    def test_integral_nlp(self):
        res = self.solver.solve("integrate x^2 from 0 to 3")
        self.assertEqual(res.answer, "9")

    def test_percentage_nlp(self):
        res = self.solver.solve("what is 20% of 600")
        self.assertEqual(res.answer, "120")

    def test_quadratic_nlp(self):
        res = self.solver.solve("solve x^2 - 7x + 12 = 0")
        self.assertIn("4", res.answer)
        self.assertIn("3", res.answer)

    def test_circle_nlp(self):
        res = self.solver.solve("area of circle radius 4")
        self.assertAlmostEqual(float(res.answer), math.pi * 16, places=2)

    def test_finance_nlp(self):
        res = self.solver.solve("compound interest principal 1000 rate 10% time 2 years")
        self.assertIn("Total", res.answer)


class TestCompilationAndGraph(unittest.TestCase):
    def test_math_compilation(self):
        fn = compile_math_expr("sin(x) + 2x")
        self.assertIsNotNone(fn)
        self.assertAlmostEqual(fn(0), 0.0)
        self.assertAlmostEqual(fn(math.pi / 2), 1.0 + math.pi)

    def test_equation_prefix_and_casing(self):
        fn1 = compile_math_expr("y = sin(x)")
        self.assertIsNotNone(fn1)
        self.assertAlmostEqual(fn1(0), 0.0)

        fn2 = compile_math_expr("f(x) = x^2 - 4")
        self.assertIsNotNone(fn2)
        self.assertAlmostEqual(fn2(2), 0.0)

        fn3 = compile_math_expr("X^3 - 3X")
        self.assertIsNotNone(fn3)
        self.assertAlmostEqual(fn3(2), 2.0)

        fn4 = compile_math_expr("2(x+1)(x-2)")
        self.assertIsNotNone(fn4)
        self.assertAlmostEqual(fn4(3), 8.0)


if __name__ == "__main__":
    unittest.main()
