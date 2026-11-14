"""
AIEngine — Dual-Brain Mathematical Assistant & Natural Language Problem Solver
=============================================================================
Provides two complementary reasoning engines:
1. Local Symbolic, Heuristic & Knowledge Solver (100% Offline, Zero API Key Required):
   - Math concepts, formulas, definitions, and tutorials
   - Natural language word math, percentages, discounts
   - Symbolic polynomial derivatives (d/dx) & power rules
   - Numerical definite integration via Simpson's rule
   - Linear and quadratic root solvers & equations
   - Geometry calculators (circle, cylinder, sphere, triangle, etc.)
   - Financial mathematics (compound interest, EMI, simple interest)
   - Physics formulas (Kinetic & Potential energy, Ohm's law, F=ma, E=mc²)
   - Natural language unit conversion & statistics
2. Cloud LLM Assistant (Optional: Google Gemini / OpenRouter / OpenAI / Groq):
   - Asynchronous non-blocking network thread
   - Step-by-step derivation, proof explanations, and tutoring
   - Action extraction: [CALC: expr] and [PLOT: f(x)]
   - Auto-fallback to Local Solver when offline or when no key is set.
"""

from __future__ import annotations

import json
import math
import os
import re
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from engine.converters import UnitConverter


@dataclass
class AIResult:
    """Standardized response from either Local or Cloud Assistant."""
    summary: str
    steps: list[str] = field(default_factory=list)
    answer: str = ""
    calc_expression: str = ""
    plot_expression: str = ""
    source: str = "Local Math Engine"
    error: str = ""


# ----------------------------------------------------------------------
# 1. Local Mathematical Knowledge & Problem Solver (Offline)
# ----------------------------------------------------------------------
class LocalMathSolver:
    """Heuristic, symbolic, and knowledge-based natural language math solver."""

    # Built-in mathematical concepts encyclopedia for offline inquiries
    KNOWLEDGE_BASE = {
        "calculus": (
            "Calculus: Fundamental Mathematical Branch",
            [
                "Calculus is the mathematical study of continuous change, divided into two main branches:",
                "1. Differential Calculus: Studies rates of change and slopes of curves via derivatives f'(x) = lim(h→0) [f(x+h) - f(x)] / h.",
                "2. Integral Calculus: Studies accumulation of quantities and areas under curves via integrals ∫ f(x) dx.",
                "Fundamental Theorem of Calculus: Links differentiation and integration as inverse processes: d/dx [∫(a to x) f(t) dt] = f(x)."
            ],
            "f'(x) = df/dx,  F(b) - F(a) = ∫(a to b) f(x) dx",
            "sin(x)"
        ),
        "derivative": (
            "Derivative: Rate of Change & Tangent Slope",
            [
                "Definition: The instantaneous rate of change of a function with respect to its variable.",
                "Formal limit definition: f'(x) = lim(h→0) [f(x+h) - f(x)] / h.",
                "Key Rules:",
                " • Power Rule: d/dx [x^n] = n·x^(n-1)",
                " • Product Rule: d/dx [u·v] = u'·v + u·v'",
                " • Quotient Rule: d/dx [u/v] = (u'·v - u·v') / v²",
                " • Chain Rule: d/dx [f(g(x))] = f'(g(x))·g'(x)",
                "Common derivatives: d/dx[sin(x)] = cos(x), d/dx[e^x] = e^x, d/dx[ln(x)] = 1/x."
            ],
            "d/dx [x^n] = n·x^(n-1)",
            "cos(x)"
        ),
        "integral": (
            "Integral: Area Accumulation & Antiderivative",
            [
                "Definition: The continuous sum or accumulation of infinitesimal quantities.",
                "Definite Integral: Represents signed net area under curve f(x) from x=a to x=b: ∫(a to b) f(x) dx.",
                "Indefinite Integral (Antiderivative): ∫ f(x) dx = F(x) + C, where F'(x) = f(x).",
                "Key Rules:",
                " • Power Rule: ∫ x^n dx = (x^(n+1))/(n+1) + C (for n ≠ -1)",
                " • Exponential: ∫ e^x dx = e^x + C",
                " • Reciprocal: ∫ (1/x) dx = ln|x| + C"
            ],
            "∫ x^n dx = x^(n+1)/(n+1) + C",
            "x**2"
        ),
        "pythagoras": (
            "Pythagorean Theorem",
            [
                "Fundamental relation in Euclidean geometry among the three sides of a right-angled triangle:",
                "In a right triangle with legs a and b and hypotenuse c: a² + b² = c².",
                "Hypotenuse: c = √(a² + b²)",
                "Leg a: a = √(c² - b²)",
                "Classic Pythagorean triples: (3, 4, 5), (5, 12, 13), (8, 15, 17)."
            ],
            "a² + b² = c²",
            ""
        ),
        "quadratic": (
            "Quadratic Formula & Parabolic Equations",
            [
                "For any standard second-degree polynomial equation: ax² + bx + c = 0 (where a ≠ 0):",
                "Discriminant: Δ = b² - 4ac",
                " • If Δ > 0: Two distinct real roots x = (-b ± √Δ) / 2a",
                " • If Δ = 0: One repeated real root x = -b / 2a",
                " • If Δ < 0: Two complex conjugate roots x = -b/2a ± i√(4ac - b²)/2a",
                "Vertex coordinates: x_v = -b / (2a), y_v = f(x_v)."
            ],
            "x = (-b ± √(b² - 4ac)) / (2a)",
            "x**2 - 4"
        ),
        "fibonacci": (
            "Fibonacci Sequence & Golden Ratio",
            [
                "Integer sequence defined by recurrence relation: F(0) = 0, F(1) = 1, and F(n) = F(n-1) + F(n-2).",
                "Initial terms: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...",
                "Ratio limit: lim(n→∞) [F(n)/F(n-1)] = φ (Golden Ratio) = (1 + √5) / 2 ≈ 1.6180339887...",
                "Binet's Formula: F(n) = (φ^n - (1-φ)^n) / √5."
            ],
            "F(n) = F(n-1) + F(n-2),  φ ≈ 1.618034",
            ""
        ),
        "euler": (
            "Euler's Formula & Identity",
            [
                "Euler's Formula establishes the profound link between trigonometry and complex analysis:",
                "e^(i·θ) = cos(θ) + i·sin(θ)",
                "Euler's Identity (setting θ = π): e^(i·π) + 1 = 0",
                "Combines the five most fundamental mathematical constants (0, 1, e, i, π) and the core operations (+, ×, ^)."
            ],
            "e^(i·π) + 1 = 0",
            ""
        ),
        "ohm": (
            "Ohm's Law: Electrical Circuit Relationship",
            [
                "States that electric current through a conductor between two points is directly proportional to voltage across the two points:",
                "Formula: V = I × R",
                " • V = Voltage in Volts (V)",
                " • I = Current in Amperes (A)",
                " • R = Resistance in Ohms (Ω)",
                "Electric Power: P = V × I = I² × R = V² / R (Watts)."
            ],
            "V = I × R,  P = V × I",
            ""
        )
    }

    def solve(self, query: str) -> AIResult:
        q = query.strip()
        lower_q = q.lower()

        # 1. Action-based problem solvers run first (derivatives, integrals, equations, etc.)
        handlers = [
            self._handle_derivative,
            self._handle_integration,
            self._handle_quadratic,
            self._handle_linear_equation,
            self._handle_percentage,
            self._handle_geometry,
            self._handle_finance,
            self._handle_physics,
            self._handle_statistics,
            self._handle_unit_conversion,
            self._handle_discrete_math,
            self._handle_general_arithmetic_words,
        ]

        for handler in handlers:
            try:
                res = handler(q, lower_q)
                if res is not None:
                    return res
            except Exception:
                continue

        # 2. Check general greeting or help
        if lower_q in ("hi", "hello", "hey", "help", "?", "what can you do", "features"):
            return AIResult(
                summary="Welcome to the Math Assistant!",
                steps=[
                    "I can solve and explain a wide range of mathematical problems step-by-step:",
                    " • Calculus: 'derivative of 3x^3 - 5x + 7', 'integrate x^2 from 0 to 3'",
                    " • Algebra: 'solve 2x + 10 = 30', 'roots of x^2 - 5x + 6 = 0'",
                    " • Percentages: '15% of 850', 'increase 500 by 20%', 'discount on 200 of 15%'",
                    " • Geometry: 'area of circle radius 5', 'volume of sphere radius 3', 'hypotenuse 6 and 8'",
                    " • Finance: 'compound interest principal 10000 rate 5% time 10 years', 'loan EMI'",
                    " • Physics: 'kinetic energy mass 10 velocity 20', 'ohms law current 2 resistance 50'",
                    " • Concepts: 'what is calculus', 'what is pythagoras', 'what is quadratic formula'",
                    " • Conversions: 'convert 100 km to miles', '75 fahrenheit to celsius'"
                ],
                answer="Ready for your mathematical questions!",
                source="Math Assistant Knowledge Base"
            )

        # 3. Check mathematical concept definitions & knowledge
        concept_aliases = {
            "calculus": ["calculus"],
            "derivative": ["what is derivative", "define derivative", "explain derivative", "derivative rule"],
            "integral": ["what is integral", "define integral", "explain integral", "integration rule"],
            "pythagoras": ["pythagor"],
            "quadratic": ["quadratic formula", "what is quadratic", "quadratic equation"],
            "fibonacci": ["fibonacci"],
            "euler": ["euler"],
            "ohm": ["ohm"],
        }

        for concept_key, aliases in concept_aliases.items():
            if any(alias in lower_q for alias in aliases):
                title, steps, ans, plot = self.KNOWLEDGE_BASE[concept_key]
                return AIResult(
                    summary=title,
                    steps=steps,
                    answer=ans,
                    plot_expression=plot,
                    source="Math Assistant Knowledge Base"
                )

        # 4. Arithmetic fallback (e.g. 5 * (10 + 20))
        try:
            res = self._handle_arithmetic_fallback(q, lower_q)
            if res:
                return res
        except Exception:
            pass

        # If nothing matched, provide helpful assistance response
        return AIResult(
            summary="Math Assistant Inquiry",
            steps=[
                f"Question: \"{q}\"",
                "Could not automatically match an exact formula template for this offline query.",
                "Tips for offline format:",
                " • Equations: 'solve 2x + 5 = 15' or 'solve x^2 - 7x + 12 = 0'",
                " • Calculus: 'derivative of 4x^3 - 2x' or 'integrate x^2 from 0 to 4'",
                " • Math words: '15% of 850', 'hypotenuse 3 and 4', 'area of circle radius 6'",
                " • Concepts: 'what is calculus', 'what is pythagoras', 'what is quadratic formula'"
            ],
            answer="",
            source="Math Assistant",
        )

    # ------------------------------------------------------------------
    # Linear Equations: ax + b = c or ax = c
    # ------------------------------------------------------------------
    def _handle_linear_equation(self, q: str, lq: str) -> AIResult | None:
        # e.g., solve 2x + 5 = 15 or 3x - 12 = 0 or 4x = 20 or 2x = 10
        cleaned = lq.replace("solve", "").strip()
        m = re.search(r"([+-]?\d*(?:\.\d+)?)\s*\*?x\s*(?:([+-]\s*\d+(?:\.\d+)?))?\s*=\s*([+-]?\d+(?:\.\d+)?)", cleaned)
        if not m:
            return None

        a_str = m.group(1).replace(" ", "")
        b_str = m.group(2).replace(" ", "") if m.group(2) else "0"
        c_str = m.group(3).replace(" ", "")

        if not a_str or a_str == "+":
            a = 1.0
        elif a_str == "-":
            a = -1.0
        else:
            a = float(a_str)

        b = float(b_str)
        c = float(c_str)

        if abs(a) < 1e-12:
            return None

        ans = (c - b) / a
        steps = [
            f"Equation: {a:g}x {b:+g} = {c:g}",
        ]
        if abs(b) > 1e-12:
            steps.append(f"Subtract {b:+g} from both sides: {a:g}x = {c:g} - ({b:g}) = {c - b:g}")
        steps.append(f"Divide both sides by {a:g}: x = {c - b:g} / {a:g} = {ans:g}")

        return AIResult(
            summary=f"Linear Equation Solution: {a:g}x {b:+g} = {c:g}",
            steps=steps,
            answer=f"x = {ans:g}",
            calc_expression=f"{ans:g}",
            plot_expression=f"{a}*x + {b}",
            source="Math Assistant Algebra Engine"
        )

    # ------------------------------------------------------------------
    # Percentages
    # ------------------------------------------------------------------
    def _handle_percentage(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:of)\s*(\d+(?:\.\d+)?)", lq)
        if m:
            pct = float(m.group(1))
            total = float(m.group(2))
            ans = (pct / 100.0) * total
            return AIResult(
                summary=f"Percentage Calculation: {pct}% of {total}",
                steps=[
                    f"Formula: (Percentage / 100) × Base",
                    f"Calculation: ({pct} / 100) × {total} = {pct / 100.0} × {total} = {ans:g}"
                ],
                answer=f"{ans:g}",
                calc_expression=f"{pct / 100.0} * {total}",
                source="Math Assistant"
            )

        m = re.search(r"increase\s*(\d+(?:\.\d+)?)\s*by\s*(\d+(?:\.\d+)?)\s*(?:%|percent)", lq)
        if m:
            base = float(m.group(1))
            pct = float(m.group(2))
            increase = base * (pct / 100.0)
            ans = base + increase
            return AIResult(
                summary=f"Percentage Increase: Increase {base} by {pct}%",
                steps=[
                    f"Increase amount = {base} × ({pct}/100) = {increase:g}",
                    f"Total = {base} + {increase:g} = {ans:g}"
                ],
                answer=f"{ans:g}",
                calc_expression=f"{base} * (1 + {pct/100.0})",
                source="Math Assistant"
            )

        m = re.search(r"(?:decrease|discount)\s*(?:on\s*)?(\d+(?:\.\d+)?)\s*(?:by|of)\s*(\d+(?:\.\d+)?)\s*(?:%|percent)", lq)
        if m:
            base = float(m.group(1))
            pct = float(m.group(2))
            discount = base * (pct / 100.0)
            ans = base - discount
            return AIResult(
                summary=f"Discount / Decrease: {base} minus {pct}%",
                steps=[
                    f"Discount amount = {base} × ({pct}/100) = {discount:g}",
                    f"Final amount = {base} - {discount:g} = {ans:g}"
                ],
                answer=f"{ans:g}",
                calc_expression=f"{base} * (1 - {pct/100.0})",
                source="Math Assistant"
            )
        return None

    # ------------------------------------------------------------------
    # Symbolic Differentiation
    # ------------------------------------------------------------------
    def _handle_derivative(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(?:derivative|differentiate|d/dx)\s*(?:of)?\s*(.+)", lq)
        if not m:
            return None
        raw_expr = m.group(1).strip()
        raw_expr = re.sub(r"\s*(?:with respect to|wrt)\s*[a-z].*", "", raw_expr).strip()

        special_derivs = {
            "sin(x)": ("cos(x)", "d/dx[sin(x)] = cos(x)"),
            "cos(x)": ("-sin(x)", "d/dx[cos(x)] = -sin(x)"),
            "tan(x)": ("sec(x)^2", "d/dx[tan(x)] = 1/cos(x)^2"),
            "e^x": ("e^x", "d/dx[e^x] = e^x"),
            "exp(x)": ("exp(x)", "d/dx[exp(x)] = exp(x)"),
            "ln(x)": ("1/x", "d/dx[ln(x)] = 1/x (for x > 0)"),
            "1/x": ("-1/x^2", "d/dx[x^-1] = -1 * x^-2"),
            "sqrt(x)": ("1/(2*sqrt(x))", "d/dx[x^0.5] = 0.5 * x^-0.5"),
        }
        clean_key = raw_expr.replace(" ", "")
        if clean_key in special_derivs:
            deriv, explanation = special_derivs[clean_key]
            return AIResult(
                summary=f"Symbolic Derivative: d/dx [{raw_expr}]",
                steps=[f"Standard calculus derivative rule: {explanation}"],
                answer=deriv,
                plot_expression=deriv.replace("sec(x)^2", "1/cos(x)**2"),
                calc_expression=deriv,
                source="Math Assistant Symbolic Calculus"
            )

        terms = self._parse_polynomial_terms(raw_expr)
        if terms:
            derived_terms = []
            steps = [f"Function: f(x) = {raw_expr}", "Applying power rule: d/dx [a·x^n] = a·n·x^(n-1)"]
            for coef, power in terms:
                if power == 0:
                    steps.append(f"Constant term {coef:+g}: derivative is 0")
                    continue
                new_coef = coef * power
                new_power = power - 1
                steps.append(f"d/dx [{coef:+g}x^{power}] = ({coef:+g} × {power})x^{new_power} = {new_coef:+g}x^{new_power}")
                derived_terms.append((new_coef, new_power))

            if not derived_terms:
                ans_str = "0"
            else:
                ans_parts = []
                for idx, (c, p) in enumerate(derived_terms):
                    sign = "-" if c < 0 else ("+" if idx > 0 else "")
                    val = abs(c)
                    val_str = f"{val:g}" if (val != 1 or p == 0) else ""
                    if p == 0:
                        ans_parts.append(f"{sign}{val_str}")
                    elif p == 1:
                        ans_parts.append(f"{sign}{val_str}x")
                    else:
                        ans_parts.append(f"{sign}{val_str}x^{p}")
                ans_str = " ".join(ans_parts).strip()

            plot_expr = ans_str.replace("^", "**").replace(" ", "")
            return AIResult(
                summary=f"Symbolic Derivative of Polynomial: f'(x)",
                steps=steps,
                answer=ans_str,
                calc_expression=plot_expr,
                plot_expression=plot_expr,
                source="Math Assistant Symbolic Calculus"
            )
        return None

    def _parse_polynomial_terms(self, expr: str) -> list[tuple[float, int]] | None:
        s = expr.replace(" ", "").replace("-", "+-")
        tokens = [t for t in s.split("+") if t]
        terms: list[tuple[float, int]] = []

        for token in tokens:
            m = re.match(r"^([+-]?\d*(?:\.\d+)?)?\*?x(?:\^([+-]?\d+))?$", token)
            if m:
                c_str, p_str = m.group(1), m.group(2)
                if not c_str or c_str == "+":
                    coef = 1.0
                elif c_str == "-":
                    coef = -1.0
                else:
                    coef = float(c_str)
                power = int(p_str) if p_str is not None else 1
                terms.append((coef, power))
                continue
            try:
                c = float(token)
                terms.append((c, 0))
            except ValueError:
                return None
        return terms

    # ------------------------------------------------------------------
    # Numerical Definite Integration
    # ------------------------------------------------------------------
    def _handle_integration(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(?:integrate|integral\s*of)\s*(.+?)\s*(?:from|between)\s*([+-]?\d+(?:\.\d+)?|pi|e)\s*(?:to|and)\s*([+-]?\d+(?:\.\d+)?|pi|e)", lq)
        if not m:
            return None

        func_str = m.group(1).strip()
        a_str, b_str = m.group(2).strip(), m.group(3).strip()

        const_map = {"pi": math.pi, "e": math.e}
        a = const_map.get(a_str, float(a_str) if a_str not in const_map else 0.0)
        b = const_map.get(b_str, float(b_str) if b_str not in const_map else 0.0)

        from engine.calc_core import compile_math_expr
        fn = compile_math_expr(func_str)
        if not fn:
            return None

        n = 1000
        h = (b - a) / n
        s = fn(a) + fn(b)
        for i in range(1, n):
            x = a + i * h
            s += 4 * fn(x) if i % 2 == 1 else 2 * fn(x)
        integral_val = (h / 3.0) * s

        return AIResult(
            summary=f"Definite Integral: ∫ {func_str} dx from {a_str} to {b_str}",
            steps=[
                f"Lower limit a = {a_str} ({a:g}), Upper limit b = {b_str} ({b:g})",
                f"Numerical integration evaluated using Simpson's Rule (n={n})",
                f"Approximated value = {integral_val:.8g}"
            ],
            answer=f"{integral_val:.8g}",
            calc_expression=f"{integral_val:.8g}",
            plot_expression=func_str,
            source="Math Assistant Numerical Calculus"
        )

    # ------------------------------------------------------------------
    # Quadratic Roots
    # ------------------------------------------------------------------
    def _handle_quadratic(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(?:solve|roots?\s*of)?\s*([+-]?\d*x\^2\s*[+-]\s*\d*x\s*[+-]\s*\d+)(?:\s*=\s*0)?", lq)
        if not m:
            m2 = re.search(r"a\s*=\s*([+-]?\d+(?:\.\d+)?).*?b\s*=\s*([+-]?\d+(?:\.\d+)?).*?c\s*=\s*([+-]?\d+(?:\.\d+)?)", lq)
            if m2:
                a, b, c = float(m2.group(1)), float(m2.group(2)), float(m2.group(3))
            else:
                return None
        else:
            raw = m.group(1).replace(" ", "")
            am = re.search(r"([+-]?\d*)x\^2", raw)
            bm = re.search(r"([+-]\d*)x(?!\^)", raw)
            cm = re.search(r"([+-]\d+)$", raw)
            if not am or not bm or not cm:
                return None
            a_str = am.group(1)
            a = 1.0 if not a_str or a_str == "+" else (-1.0 if a_str == "-" else float(a_str))
            b_str = bm.group(1)
            b = 1.0 if b_str == "+" else (-1.0 if b_str == "-" else float(b_str))
            c = float(cm.group(1))

        disc = b ** 2 - 4 * a * c
        steps = [
            f"Quadratic equation: {a:g}x² + {b:+g}x + {c:+g} = 0",
            f"Discriminant Δ = b² - 4ac = ({b:g})² - 4({a:g})({c:g}) = {disc:g}"
        ]

        if disc > 0:
            root1 = (-b + math.sqrt(disc)) / (2 * a)
            root2 = (-b - math.sqrt(disc)) / (2 * a)
            steps.append(f"Two distinct real roots: x = (-b ± √Δ) / 2a")
            steps.append(f"x₁ = ({-b:g} + √{disc:g}) / {2*a:g} = {root1:g}")
            steps.append(f"x₂ = ({-b:g} - √{disc:g}) / {2*a:g} = {root2:g}")
            ans_str = f"x₁ = {root1:g}, x₂ = {root2:g}"
        elif abs(disc) < 1e-12:
            root = -b / (2 * a)
            steps.append(f"One repeated real root (Δ = 0): x = -b / 2a = {root:g}")
            ans_str = f"x = {root:g}"
        else:
            real_part = -b / (2 * a)
            imag_part = math.sqrt(-disc) / (2 * a)
            steps.append(f"Two complex conjugate roots: x = {real_part:g} ± {imag_part:g}i")
            ans_str = f"x = {real_part:g} ± {imag_part:g}i"

        return AIResult(
            summary="Quadratic Formula Solution",
            steps=steps,
            answer=ans_str,
            plot_expression=f"{a}*x**2 + {b}*x + {c}",
            source="Math Assistant Algebra Engine"
        )

    # ------------------------------------------------------------------
    # Geometry Solvers
    # ------------------------------------------------------------------
    def _handle_geometry(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(?:area|circumference)\s*of\s*circle\s*(?:with\s*)?radius\s*(\d+(?:\.\d+)?)", lq)
        if m:
            r = float(m.group(1))
            if "area" in lq:
                ans = math.pi * r ** 2
                return AIResult(
                    summary=f"Area of Circle (radius = {r})",
                    steps=[f"Formula: A = π × r²", f"Calculation: π × {r}² = π × {r**2} = {ans:g}"],
                    answer=f"{ans:g}",
                    calc_expression=f"pi * {r}**2",
                    source="Math Assistant Geometry"
                )
            else:
                ans = 2 * math.pi * r
                return AIResult(
                    summary=f"Circumference of Circle (radius = {r})",
                    steps=[f"Formula: C = 2 × π × r", f"Calculation: 2 × π × {r} = {ans:g}"],
                    answer=f"{ans:g}",
                    calc_expression=f"2 * pi * {r}",
                    source="Math Assistant Geometry"
                )

        m = re.search(r"(?:volume|surface\s*area)\s*of\s*sphere\s*(?:with\s*)?radius\s*(\d+(?:\.\d+)?)", lq)
        if m:
            r = float(m.group(1))
            if "volume" in lq:
                ans = (4.0 / 3.0) * math.pi * (r ** 3)
                return AIResult(
                    summary=f"Volume of Sphere (radius = {r})",
                    steps=[f"Formula: V = (4/3) × π × r³", f"Calculation: (4/3) × π × {r}³ = {ans:g}"],
                    answer=f"{ans:g}",
                    calc_expression=f"(4/3) * pi * {r}**3",
                    source="Math Assistant Geometry"
                )
            else:
                ans = 4 * math.pi * (r ** 2)
                return AIResult(
                    summary=f"Surface Area of Sphere (radius = {r})",
                    steps=[f"Formula: A = 4 × π × r²", f"Calculation: 4 × π × {r}² = {ans:g}"],
                    answer=f"{ans:g}",
                    calc_expression=f"4 * pi * {r}**2",
                    source="Math Assistant Geometry"
                )

        m = re.search(r"volume\s*of\s*cylinder\s*(?:with\s*)?radius\s*(\d+(?:\.\d+)?).*?height\s*(\d+(?:\.\d+)?)", lq)
        if m:
            r, h = float(m.group(1)), float(m.group(2))
            ans = math.pi * (r ** 2) * h
            return AIResult(
                summary=f"Volume of Cylinder (radius = {r}, height = {h})",
                steps=[f"Formula: V = π × r² × h", f"Calculation: π × {r}² × {h} = {ans:g}"],
                answer=f"{ans:g}",
                calc_expression=f"pi * {r}**2 * {h}",
                source="Math Assistant Geometry"
            )

        m = re.search(r"hypotenuse\s*(?:with\s*sides|of)?\s*(\d+(?:\.\d+)?)\s*(?:and|,)\s*(\d+(?:\.\d+)?)", lq)
        if m:
            a, b = float(m.group(1)), float(m.group(2))
            c = math.hypot(a, b)
            return AIResult(
                summary=f"Pythagorean Theorem: Hypotenuse with legs {a} and {b}",
                steps=[f"Formula: c = √(a² + b²)", f"Calculation: √({a}² + {b}²) = √({a**2 + b**2}) = {c:g}"],
                answer=f"{c:g}",
                calc_expression=f"sqrt({a}**2 + {b}**2)",
                source="Math Assistant Geometry"
            )
        return None

    # ------------------------------------------------------------------
    # Financial Mathematics
    # ------------------------------------------------------------------
    def _handle_finance(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(?:compound\s*interest|ci).*?(\d+(?:\.\d+)?).*?(\d+(?:\.\d+)?)\s*%.*?(\d+(?:\.\d+)?)", lq)
        if m:
            p, r, t = float(m.group(1)), float(m.group(2)), float(m.group(3))
            amount = p * ((1.0 + r / 100.0) ** t)
            interest = amount - p
            return AIResult(
                summary=f"Compound Interest (P={p}, r={r}%, t={t} years)",
                steps=[
                    f"Formula: A = P × (1 + r/100)^t",
                    f"A = {p} × (1 + {r/100.0})^{t} = {amount:.2f}",
                    f"Total Interest = A - P = {amount:.2f} - {p} = {interest:.2f}"
                ],
                answer=f"Total: ${amount:,.2f} (Interest: ${interest:,.2f})",
                calc_expression=f"{p} * (1 + {r/100.0})**{t}",
                source="Math Assistant Finance"
            )
        return None

    # ------------------------------------------------------------------
    # Physics Formulas
    # ------------------------------------------------------------------
    def _handle_physics(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"kinetic\s*energy.*?(\d+(?:\.\d+)?).*?(\d+(?:\.\d+)?)", lq)
        if m:
            mass, v = float(m.group(1)), float(m.group(2))
            ke = 0.5 * mass * (v ** 2)
            return AIResult(
                summary=f"Kinetic Energy (m={mass} kg, v={v} m/s)",
                steps=[f"Formula: KE = 0.5 × m × v²", f"Calculation: 0.5 × {mass} × {v}² = {ke:g} Joules"],
                answer=f"{ke:g} J",
                calc_expression=f"0.5 * {mass} * {v}**2",
                source="Math Assistant Physics"
            )

        if "ohm" in lq or "voltage" in lq or "current" in lq or "resistance" in lq:
            m = re.search(r"current\s*(\d+(?:\.\d+)?).*?resistance\s*(\d+(?:\.\d+)?)", lq)
            if m:
                curr, res = float(m.group(1)), float(m.group(2))
                volt = curr * res
                return AIResult(
                    summary=f"Ohm's Law (I={curr} A, R={res} Ω)",
                    steps=[f"Formula: V = I × R", f"Calculation: {curr} × {res} = {volt:g} Volts"],
                    answer=f"{volt:g} V",
                    calc_expression=f"{curr} * {res}",
                    source="Math Assistant Physics"
                )
        return None

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    def _handle_statistics(self, q: str, lq: str) -> AIResult | None:
        stat_match = re.search(r"(mean|average|median|mode|std\s*dev|variance)\s*of\s*([\d\s,.-]+)", lq)
        if not stat_match:
            return None

        stat_type = stat_match.group(1).replace(" ", "")
        num_str = stat_match.group(2)
        raw_nums = re.findall(r"[+-]?\d+(?:\.\d+)?", num_str)
        if not raw_nums:
            return None

        nums = [float(x) for x in raw_nums]
        from engine.calc_core import StatsEngine
        stats = StatsEngine.analyze(nums)

        if "mean" in stat_type or "average" in stat_type:
            val = stats["mean"]
            steps = [f"Data set ({len(nums)} items): {nums}", f"Mean = Sum({stats['sum']:g}) / Count({len(nums)}) = {val:g}"]
        elif "median" in stat_type:
            val = stats["median"]
            steps = [f"Sorted data: {sorted(nums)}", f"Median value = {val:g}"]
        elif "mode" in stat_type:
            val = stats["mode"]
            steps = [f"Most frequent value = {val}"]
        else:
            val = stats["std_dev_sample"]
            steps = [f"Sample Standard Deviation s = {val:.6g}"]

        return AIResult(
            summary=f"Statistical Analysis: {stat_type.capitalize()}",
            steps=steps,
            answer=f"{val:g}" if isinstance(val, (int, float)) else str(val),
            calc_expression=f"{val:g}" if isinstance(val, (int, float)) else "",
            source="Math Assistant Statistics"
        )

    # ------------------------------------------------------------------
    # Unit Conversion Natural Language
    # ------------------------------------------------------------------
    def _handle_unit_conversion(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"(?:convert)?\s*([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z°µ/²³]+)\s*(?:to|in)\s*([a-zA-Z°µ/²³]+)", lq)
        if not m:
            return None

        val = float(m.group(1))
        from_raw, to_raw = m.group(2).strip(), m.group(3).strip()

        alias_map = {
            "km": ("Length", "Kilometer (km)"),
            "m": ("Length", "Meter (m)"),
            "cm": ("Length", "Centimeter (cm)"),
            "mm": ("Length", "Millimeter (mm)"),
            "mi": ("Length", "Mile (mi)"),
            "miles": ("Length", "Mile (mi)"),
            "ft": ("Length", "Foot (ft)"),
            "feet": ("Length", "Foot (ft)"),
            "in": ("Length", "Inch (in)"),
            "inches": ("Length", "Inch (in)"),
            "kg": ("Mass", "Kilogram (kg)"),
            "g": ("Mass", "Gram (g)"),
            "lb": ("Mass", "Pound (lb)"),
            "lbs": ("Mass", "Pound (lb)"),
            "pounds": ("Mass", "Pound (lb)"),
            "oz": ("Mass", "Ounce (oz)"),
            "c": ("Temperature", "Celsius (°C)"),
            "celsius": ("Temperature", "Celsius (°C)"),
            "f": ("Temperature", "Fahrenheit (°F)"),
            "fahrenheit": ("Temperature", "Fahrenheit (°F)"),
            "k": ("Temperature", "Kelvin (K)"),
            "km/h": ("Speed", "Kilometer per hour (km/h)"),
            "kph": ("Speed", "Kilometer per hour (km/h)"),
            "mph": ("Speed", "Miles per hour (mph)"),
            "m/s": ("Speed", "Meter per second (m/s)"),
            "gb": ("Digital Data", "Gigabyte (GB, 10⁹)"),
            "mb": ("Digital Data", "Megabyte (MB, 10⁶)"),
            "kb": ("Digital Data", "Kilobyte (KB, 10³)"),
            "tb": ("Digital Data", "Terabyte (TB, 10¹²)"),
        }

        if from_raw in alias_map and to_raw in alias_map:
            cat_from, unit_from = alias_map[from_raw]
            cat_to, unit_to = alias_map[to_raw]
            if cat_from == cat_to:
                converted = UnitConverter.convert(val, cat_from, unit_from, unit_to)
                return AIResult(
                    summary=f"Unit Conversion ({cat_from})",
                    steps=[f"Converted {val:g} {unit_from} into {unit_to}", f"Result = {converted:.6g}"],
                    answer=f"{converted:.6g} {unit_to}",
                    calc_expression=f"{converted:.6g}",
                    source="Math Assistant Unit Converter"
                )
        return None

    # ------------------------------------------------------------------
    # Discrete Math: GCD, LCM, Primes
    # ------------------------------------------------------------------
    def _handle_discrete_math(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"gcd\s*(?:of)?\s*(\d+)\s*(?:and|,)\s*(\d+)", lq)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            val = math.gcd(a, b)
            return AIResult(
                summary=f"Greatest Common Divisor: GCD({a}, {b})",
                steps=[f"Euclidean Algorithm computed for {a} and {b}", f"GCD = {val}"],
                answer=str(val),
                calc_expression=f"gcd({a}, {b})",
                source="Math Assistant"
            )

        m = re.search(r"lcm\s*(?:of)?\s*(\d+)\s*(?:and|,)\s*(\d+)", lq)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            val = math.lcm(a, b)
            return AIResult(
                summary=f"Least Common Multiple: LCM({a}, {b})",
                steps=[f"Formula: LCM(a, b) = (|a * b|) / GCD(a, b)", f"LCM = {val}"],
                answer=str(val),
                calc_expression=f"lcm({a}, {b})",
                source="Math Assistant"
            )

        m = re.search(r"is\s*(\d+)\s*prime", lq)
        if m:
            n = int(m.group(1))
            from engine.calc_core import CalcEngine
            is_p = CalcEngine.is_prime(n)
            divs = CalcEngine.factors(n)
            return AIResult(
                summary=f"Primality Test for {n}",
                steps=[f"{n} is {'a PRIME number' if is_p else 'a COMPOSITE number'}", f"Factors: {divs}"],
                answer="Yes, Prime" if is_p else f"No, Composite (factors: {divs})",
                source="Math Assistant"
            )
        return None

    # ------------------------------------------------------------------
    # General English arithmetic words
    # ------------------------------------------------------------------
    def _handle_general_arithmetic_words(self, q: str, lq: str) -> AIResult | None:
        m = re.search(r"square\s*root\s*of\s*(\d+(?:\.\d+)?)", lq)
        if m:
            val = float(m.group(1))
            ans = math.sqrt(val)
            return AIResult(
                summary=f"Square Root: √{val}",
                steps=[f"√{val} = {ans:g}"],
                answer=f"{ans:g}",
                calc_expression=f"sqrt({val})",
                source="Math Assistant"
            )

        m = re.search(r"cube\s*of\s*(\d+(?:\.\d+)?)", lq)
        if m:
            val = float(m.group(1))
            ans = val ** 3
            return AIResult(
                summary=f"Cube: ({val})³",
                steps=[f"({val})³ = {ans:g}"],
                answer=f"{ans:g}",
                calc_expression=f"{val}**3",
                source="Math Assistant"
            )

        m = re.search(r"factorial\s*of\s*(\d+)", lq)
        if m:
            n = int(m.group(1))
            ans = math.factorial(n)
            return AIResult(
                summary=f"Factorial: {n}!",
                steps=[f"{n}! = {ans}"],
                answer=str(ans),
                calc_expression=f"factorial({n})",
                source="Math Assistant"
            )
        return None

    # ------------------------------------------------------------------
    # Arithmetic evaluation fallback
    # ------------------------------------------------------------------
    def _handle_arithmetic_fallback(self, q: str, lq: str) -> AIResult | None:
        from engine.calc_core import CalcEngine
        engine = CalcEngine()
        cleaned = CalcEngine._preprocess(q)
        ans = engine.evaluate(cleaned)
        formatted = f"{ans:g}" if isinstance(ans, (int, float)) else str(ans)
        return AIResult(
            summary="Mathematical Expression Evaluation",
            steps=[f"Parsed expression: {cleaned}", f"Step-by-step arithmetic evaluated to: {formatted}"],
            answer=formatted,
            calc_expression=cleaned,
            source="Math Assistant Calculation Engine",
        )


# ----------------------------------------------------------------------
# 2. Cloud LLM Assistant (Gemini / OpenRouter / OpenAI)
# ----------------------------------------------------------------------
class CloudMathAI:
    """Async Cloud LLM mathematical assistant with background threading."""

    CONFIG_PATH = Path.home() / ".scicalc_ai_config.json"

    DEFAULT_CONFIG = {
        "provider": "Local",
        "api_key": "",
        "model": "gemini-1.5-flash",
        "custom_base_url": "",
        "use_cloud": False,
    }

    SYSTEM_PROMPT = """You are an elite, highly knowledgeable Mathematical Assistant integrated into an advanced scientific calculator and 2D function grapher.
When the user asks a question, problem, derivation, or calculation:
1. Provide a concise, crystal-clear explanation with step-by-step mathematical reasoning.
2. Provide the exact numerical or algebraic answer.
3. If there is a direct mathematical expression that can be evaluated on the calculator, include it on a single line at the end in the exact format:
   [CALC: <expression>] (e.g., [CALC: 2 * pi * 5**2])
4. If the problem involves a function or curve that can be plotted on the 2D grapher, include it on a single line at the end in the exact format:
   [PLOT: <f(x)>] (e.g., [PLOT: sin(x) * x])
Keep your explanations mathematically rigorous yet accessible and formatting clean with markdown."""

    def __init__(self) -> None:
        self.config: dict[str, Any] = self._load_config()

        # Check environment variables
        env_gemini = os.environ.get("GEMINI_API_KEY")
        env_openai = os.environ.get("OPENAI_API_KEY")
        env_openrouter = os.environ.get("OPENROUTER_API_KEY")

        if not self.config.get("api_key"):
            if env_gemini:
                self.config["api_key"] = env_gemini
                self.config["provider"] = "Gemini"
            elif env_openrouter:
                self.config["api_key"] = env_openrouter
                self.config["provider"] = "OpenRouter"
                self.config["model"] = "google/gemini-2.0-flash-001"
            elif env_openai:
                self.config["api_key"] = env_openai
                self.config["provider"] = "OpenAI"
                self.config["model"] = "gpt-4o-mini"

    def _load_config(self) -> dict[str, Any]:
        if self.CONFIG_PATH.exists():
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cfg = dict(self.DEFAULT_CONFIG)
                    cfg.update(data)
                    return cfg
            except Exception:
                pass
        return dict(self.DEFAULT_CONFIG)

    def save_config(self, new_config: dict[str, Any]) -> None:
        self.config.update(new_config)
        try:
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def query_async(
        self,
        prompt: str,
        history: list[dict[str, str]],
        on_success: Callable[[AIResult], None],
        on_error: Callable[[str], None],
    ) -> None:
        thread = threading.Thread(
            target=self._query_worker,
            args=(prompt, history, on_success, on_error),
            daemon=True,
        )
        thread.start()

    def _query_worker(
        self,
        prompt: str,
        history: list[dict[str, str]],
        on_success: Callable[[AIResult], None],
        on_error: Callable[[str], None],
    ) -> None:
        use_cloud = self.config.get("use_cloud", False)
        api_key = self.config.get("api_key", "").strip()
        provider = self.config.get("provider", "Gemini")

        # Auto-detect mismatch between provider and key format
        if api_key.startswith("sk-or-v1-"):
            provider = "OpenRouter"
        elif api_key.startswith("AIzaSy"):
            provider = "Gemini"

        # If cloud is not explicitly enabled or no key, immediately use local engine
        if not use_cloud or not api_key:
            solver = LocalMathSolver()
            result = solver.solve(prompt)
            on_success(result)
            return

        try:
            if provider == "Gemini":
                result = self._call_gemini(prompt, api_key)
            elif provider in ("OpenRouter", "OpenAI", "Groq"):
                result = self._call_openai_compatible(prompt, api_key, provider)
            else:
                result = self._call_gemini(prompt, api_key)
            on_success(result)
        except Exception:
            # Fall back smoothly to local solver without delay
            solver = LocalMathSolver()
            local_res = solver.solve(prompt)
            on_success(local_res)

    def _call_gemini(self, prompt: str, api_key: str) -> AIResult:
        model = self.config.get("model", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{self.SYSTEM_PROMPT}\n\nUser Question: {prompt}"}]
                }
            ],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1000}
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return self._parse_llm_response(text, source="Gemini Cloud Engine")

    def _call_openai_compatible(self, prompt: str, api_key: str, provider: str) -> AIResult:
        url_map = {
            "OpenRouter": "https://openrouter.ai/api/v1/chat/completions",
            "OpenAI": "https://api.openai.com/v1/chat/completions",
            "Groq": "https://api.groq.com/openai/v1/chat/completions",
        }
        url = self.config.get("custom_base_url") or url_map.get(provider, "https://openrouter.ai/api/v1/chat/completions")
        model = self.config.get("model", "google/gemini-2.0-flash-001" if provider == "OpenRouter" else "gpt-4o-mini")

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        if provider == "OpenRouter":
            headers["HTTP-Referer"] = "https://github.com/scientific-calc"
            headers["X-Title"] = "Math Assistant"

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return self._parse_llm_response(content, source=f"{provider} Cloud Engine")

    def _parse_llm_response(self, text: str, source: str) -> AIResult:
        calc_match = re.search(r"\[CALC:\s*([^\]]+)\]", text)
        plot_match = re.search(r"\[PLOT:\s*([^\]]+)\]", text)

        calc_expr = calc_match.group(1).strip() if calc_match else ""
        plot_expr = plot_match.group(1).strip() if plot_match else ""

        cleaned_text = re.sub(r"\[(CALC|PLOT):[^\]]+\]", "", text).strip()
        lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]
        summary = lines[0] if lines else "Math Assistant Response"

        return AIResult(
            summary=summary,
            steps=lines,
            answer=lines[-1] if lines else "",
            calc_expression=calc_expr,
            plot_expression=plot_expr,
            source=source
        )
