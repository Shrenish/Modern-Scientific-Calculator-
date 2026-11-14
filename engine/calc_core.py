"""
CalcCore — Advanced Mathematical & Scientific Calculation Engine
================================================================
Comprehensive mathematical evaluation engine supporting:
- Arithmetic, power, roots, logarithms
- Trigonometric, inverse, and hyperbolic functions (DEG, RAD, GRAD)
- Advanced number theory: GCD, LCM, primes, factors, permutations, combinations
- Complex numbers support
- Matrix operations (2x2 and 3x3 determinant, inverse, transpose, multiplication)
- Statistical analysis (mean, median, mode, variance, std dev, linear regression)
- Programmer base conversions & bitwise logic
- Safe AST / restricted namespace evaluation
"""

from __future__ import annotations

import ast
import math
import re
from typing import Any, Callable


class CalcEngine:
    """Safe evaluation engine with extensive scientific capabilities."""

    DEG = "DEG"
    RAD = "RAD"
    GRAD = "GRAD"

    def __init__(self) -> None:
        self.angle_mode: str = self.DEG
        self.memory: float = 0.0
        self.variables: dict[str, float] = {"ans": 0.0, "x": 0.0, "y": 0.0}
        self.history: list[str] = []
        self._last_result: float = 0.0

    # ------------------------------------------------------------------
    # Angle mode conversions
    # ------------------------------------------------------------------
    def _to_rad(self, x: float) -> float:
        if self.angle_mode == self.RAD:
            return x
        if self.angle_mode == self.GRAD:
            return x * math.pi / 200.0
        return math.radians(x)

    def _from_rad(self, x: float) -> float:
        if self.angle_mode == self.RAD:
            return x
        if self.angle_mode == self.GRAD:
            return x * 200.0 / math.pi
        return math.degrees(x)

    # ------------------------------------------------------------------
    # Mathematical helpers
    # ------------------------------------------------------------------
    @staticmethod
    def is_prime(n: int) -> bool:
        """Check if an integer n is prime."""
        n = int(n)
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        w = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += w
            w = 6 - w
        return True

    @staticmethod
    def factors(n: int) -> list[int]:
        """Return sorted list of all positive divisors of n."""
        n = abs(int(n))
        if n == 0:
            return [0]
        divs = set()
        for i in range(1, int(math.isqrt(n)) + 1):
            if n % i == 0:
                divs.add(i)
                divs.add(n // i)
        return sorted(divs)

    @staticmethod
    def fibonacci(n: int) -> int:
        """Return the nth Fibonacci number (0-indexed)."""
        n = int(n)
        if n < 0:
            raise ValueError("Fibonacci requires n >= 0")
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    # ------------------------------------------------------------------
    # Safe evaluation namespace
    # ------------------------------------------------------------------
    def _build_ns(self) -> dict[str, Any]:
        """Build dictionary of allowed math functions and constants."""
        trig = {
            "sin": lambda x: math.sin(self._to_rad(x)),
            "cos": lambda x: math.cos(self._to_rad(x)),
            "tan": lambda x: math.tan(self._to_rad(x)),
            "asin": lambda x: self._from_rad(math.asin(x)),
            "acos": lambda x: self._from_rad(math.acos(x)),
            "atan": lambda x: self._from_rad(math.atan(x)),
            "atan2": lambda y, x: self._from_rad(math.atan2(y, x)),
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "asinh": math.asinh,
            "acosh": math.acosh,
            "atanh": math.atanh,
            "sind": lambda x: math.sin(math.radians(x)),
            "cosd": lambda x: math.cos(math.radians(x)),
            "tand": lambda x: math.tan(math.radians(x)),
        }
        logfns = {
            "log": math.log10,
            "ln": math.log,
            "log2": math.log2,
            "logb": lambda x, b: math.log(x, b),
        }
        roots_powers = {
            "sqrt": math.sqrt,
            "cbrt": lambda x: math.copysign(abs(x) ** (1.0 / 3.0), x),
            "nthroot": lambda x, n: x ** (1.0 / n) if x >= 0 else (-((-x) ** (1.0 / n))),
            "exp": math.exp,
            "pow": pow,
            "abs": abs,
        }
        discrete = {
            "factorial": math.factorial,
            "perm": math.perm,
            "comb": math.comb,
            "gcd": math.gcd,
            "lcm": lambda a, b: math.lcm(int(a), int(b)),
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "isPrime": self.is_prime,
            "factors": self.factors,
            "fib": self.fibonacci,
        }
        consts = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": math.inf,
            "ans": self._last_result,
            "Ans": self._last_result,
        }
        # Include dynamic variables
        variables = {k: v for k, v in self.variables.items()}

        ns: dict[str, Any] = {}
        ns.update(trig)
        ns.update(logfns)
        ns.update(roots_powers)
        ns.update(discrete)
        ns.update(consts)
        ns.update(variables)
        return ns

    # ------------------------------------------------------------------
    # Expression preprocessing
    # ------------------------------------------------------------------
    @staticmethod
    def _preprocess(expr: str) -> str:
        """Translate UI symbols, implicit multiplication, and format into valid Python math."""
        s = expr.strip()
        if not s:
            return "0"

        # Replace UI glyphs
        s = s.replace("×", "*").replace("÷", "/").replace("−", "-").replace("–", "-")
        s = s.replace("^", "**")
        s = s.replace("√", "sqrt")

        # Handle percentage additions/subtractions like 50 + 10% or 100 - 20%
        # e.g., (A) + (B)% -> (A) * (1 + (B)/100)
        s = re.sub(r"(\d+(\.\d+)?)\s*\+\s*(\d+(\.\d+)?)%", r"(\1 * (1 + \3/100))", s)
        s = re.sub(r"(\d+(\.\d+)?)\s*-\s*(\d+(\.\d+)?)%", r"(\1 * (1 - \3/100))", s)
        # Standalone percentage: 25% -> (25/100)
        s = re.sub(r"(\d+(\.\d+)?)%", r"(\1/100)", s)

        # Handle implicit multiplication:
        # e.g. 2pi -> 2*pi, 2(3+4) -> 2*(3+4), (2+3)(4+5) -> (2+3)*(4+5), 3sin(x) -> 3*sin(x)
        # Note: Avoid breaking scientific notation like 1e5 or 2E3
        s = re.sub(r"(\d)\s*([a-df-zA-Z(])", r"\1*\2", s)  # skips 'e' directly after digit for 1e5
        s = re.sub(r"(\))\s*(\d|[a-zA-Z(])", r"\1*\2", s)

        # Standalone 'e' or 'pi' preceded by a number
        s = re.sub(r"(\d)\s*(pi|tau|ans)", r"\1*\2", s, flags=re.IGNORECASE)

        return s

    # ------------------------------------------------------------------
    # AST safety validation
    # ------------------------------------------------------------------
    ALLOWED_AST_NODES = {
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name,
        ast.Call, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.FloorDiv, ast.Mod, ast.Pow, ast.USub, ast.UAdd,
        ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift, ast.Invert,
        ast.Tuple, ast.List,
    }

    def _validate_ast(self, tree: ast.AST) -> None:
        """Ensure no unsafe constructs like import, exec, attributes, or loops exist."""
        for node in ast.walk(tree):
            if type(node) not in self.ALLOWED_AST_NODES:
                raise ValueError(f"Disallowed expression element: {type(node).__name__}")
            if isinstance(node, ast.Attribute):
                raise ValueError("Attribute access is prohibited")

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate(self, expression: str) -> float | complex | int:
        """Evaluate expression safely, updating answer state."""
        processed = self._preprocess(expression)
        try:
            tree = ast.parse(processed, mode="eval")
            self._validate_ast(tree)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in expression: {e.msg}") from e

        ns = self._build_ns()
        compiled = compile(tree, filename="<calc>", mode="eval")
        result = eval(compiled, {"__builtins__": {}}, ns)  # noqa: S307

        if isinstance(result, (int, float)):
            self._last_result = float(result)
            self.variables["ans"] = self._last_result
        return result

    def last(self) -> float:
        return self._last_result

    # ------------------------------------------------------------------
    # Memory register operations
    # ------------------------------------------------------------------
    def store_memory(self, val: float) -> None:
        self.memory = float(val)

    def mem_add(self, val: float) -> None:
        self.memory += float(val)

    def mem_sub(self, val: float) -> None:
        self.memory -= float(val)

    def mem_recall(self) -> float:
        return self.memory

    def mem_clear(self) -> None:
        self.memory = 0.0

    def set_variable(self, name: str, val: float) -> None:
        clean_name = re.sub(r"[^a-zA-Z]", "", name).lower()
        if clean_name:
            self.variables[clean_name] = float(val)

    def get_variable(self, name: str) -> float:
        return self.variables.get(name.lower(), 0.0)


def compile_math_expr(expr: str) -> Callable[[float], float] | None:
    """Safely compile a math expression f(x) into a fast callable with x as variable."""
    s = expr.strip()
    if not s:
        return None

    # Strip equation prefixes like "y =", "f(x) =", "g(x) =", "y(x) ="
    s = re.sub(r"^(?:y|f\(x\)|g\(x\)|y\(x\))\s*=\s*", "", s, flags=re.IGNORECASE).strip()
    if not s:
        return None

    # Standardize operators and glyphs
    s = s.replace("^", "**").replace("×", "*").replace("÷", "/").replace("−", "-").replace("–", "-")

    # Normalize variable X to lowercase x (avoiding hex numbers or function names)
    # Replace uppercase X with lowercase x when used as a variable
    s = re.sub(r"\bX\b", "x", s)

    # Implicit multiplication:
    # 2x -> 2*x, 3(x+1) -> 3*(x+1), )x -> )*x, )( -> )*(, x( -> x*(
    s = re.sub(r"(\d)\s*([a-df-zA-Z(])", r"\1*\2", s)
    s = re.sub(r"(\))\s*(\d|[a-zA-Z(])", r"\1*\2", s)
    s = re.sub(r"\bx\s*\(", "x*(", s)
    s = re.sub(r"\)\s*x\b", ")*x", s)

    # Safe math functions mapping
    safe_dict = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sec": lambda v: 1.0 / math.cos(v) if abs(math.cos(v)) > 1e-12 else float("nan"),
        "csc": lambda v: 1.0 / math.sin(v) if abs(math.sin(v)) > 1e-12 else float("nan"),
        "cot": lambda v: 1.0 / math.tan(v) if abs(math.tan(v)) > 1e-12 else float("nan"),
        "asin": lambda v: math.asin(v) if -1.0 <= v <= 1.0 else float("nan"),
        "acos": lambda v: math.acos(v) if -1.0 <= v <= 1.0 else float("nan"),
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "sqrt": lambda v: math.sqrt(v) if v >= 0 else float("nan"),
        "cbrt": lambda v: math.copysign(abs(v) ** (1.0 / 3.0), v),
        "exp": lambda v: math.exp(min(v, 700)),
        "ln": lambda v: math.log(v) if v > 0 else float("nan"),
        "log": lambda v: math.log10(v) if v > 0 else float("nan"),
        "log10": lambda v: math.log10(v) if v > 0 else float("nan"),
        "log2": lambda v: math.log2(v) if v > 0 else float("nan"),
        "abs": abs,
        "sinc": lambda v: math.sin(v) / v if v != 0 else 1.0,
        "floor": math.floor,
        "ceil": math.ceil,
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    try:
        code = compile(s, "<compiled_math>", "eval")
    except Exception:
        return None

    def fn(x: float) -> float:
        try:
            local_scope = {"x": float(x), "X": float(x)}
            val = eval(code, {"__builtins__": {}}, {**safe_dict, **local_scope})  # noqa: S307
            if isinstance(val, complex):
                return val.real if abs(val.imag) < 1e-12 else float("nan")
            return float(val)
        except Exception:
            return float("nan")

    return fn



# ----------------------------------------------------------------------
# Matrix & Linear Algebra Operations (Pure Python)
# ----------------------------------------------------------------------
class MatrixEngine:
    """Matrix computation engine for 2x2 and 3x3 matrices."""

    @staticmethod
    def det2(m: list[list[float]]) -> float:
        """Determinant of 2x2 matrix [[a, b], [c, d]]."""
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]

    @staticmethod
    def det3(m: list[list[float]]) -> float:
        """Determinant of 3x3 matrix."""
        a, b, c = m[0]
        d, e, f = m[1]
        g, h, i = m[2]
        return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

    @staticmethod
    def inverse2(m: list[list[float]]) -> list[list[float]]:
        """Inverse of 2x2 matrix."""
        d = MatrixEngine.det2(m)
        if abs(d) < 1e-12:
            raise ValueError("Matrix is singular (determinant = 0)")
        return [
            [m[1][1] / d, -m[0][1] / d],
            [-m[1][0] / d, m[0][0] / d]
        ]

    @staticmethod
    def inverse3(m: list[list[float]]) -> list[list[float]]:
        """Inverse of 3x3 matrix using adjugate method."""
        d = MatrixEngine.det3(m)
        if abs(d) < 1e-12:
            raise ValueError("Matrix is singular (determinant = 0)")

        # Minors & Cofactors
        c00 =  (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        c01 = -(m[1][0] * m[2][2] - m[1][2] * m[2][0])
        c02 =  (m[1][0] * m[2][1] - m[1][1] * m[2][0])

        c10 = -(m[0][1] * m[2][2] - m[0][2] * m[2][1])
        c11 =  (m[0][0] * m[2][2] - m[0][2] * m[2][0])
        c12 = -(m[0][0] * m[2][1] - m[0][1] * m[2][0])

        c20 =  (m[0][1] * m[1][2] - m[0][2] * m[1][1])
        c21 = -(m[0][0] * m[1][2] - m[0][2] * m[1][0])
        c22 =  (m[0][0] * m[1][1] - m[0][1] * m[1][0])

        # Transpose of cofactor matrix divided by determinant
        return [
            [c00 / d, c10 / d, c20 / d],
            [c01 / d, c11 / d, c21 / d],
            [c02 / d, c12 / d, c22 / d]
        ]

    @staticmethod
    def multiply(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
        """Multiply matrix A by matrix B."""
        rows_a = len(A)
        cols_a = len(A[0])
        rows_b = len(B)
        cols_b = len(B[0])

        if cols_a != rows_b:
            raise ValueError(f"Incompatible dimensions: ({rows_a}x{cols_a}) and ({rows_b}x{cols_b})")

        result = [[0.0 for _ in range(cols_b)] for _ in range(rows_a)]
        for i in range(rows_a):
            for j in range(cols_b):
                result[i][j] = sum(A[i][k] * B[k][j] for k in range(cols_a))
        return result

    @staticmethod
    def transpose(m: list[list[float]]) -> list[list[float]]:
        """Transpose of a matrix."""
        return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]


# ----------------------------------------------------------------------
# Statistics Engine (Pure Python)
# ----------------------------------------------------------------------
class StatsEngine:
    """Comprehensive descriptive statistics and linear regression."""

    @staticmethod
    def analyze(numbers: list[float]) -> dict[str, Any]:
        """Compute complete descriptive statistics for a list of numbers."""
        if not numbers:
            raise ValueError("No numbers provided for analysis")

        n = len(numbers)
        s = sum(numbers)
        mean = s / n
        sorted_vals = sorted(numbers)

        # Median
        if n % 2 == 1:
            median = sorted_vals[n // 2]
        else:
            median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        # Mode
        freq: dict[float, int] = {}
        for x in numbers:
            freq[x] = freq.get(x, 0) + 1
        max_freq = max(freq.values())
        modes = [k for k, v in freq.items() if v == max_freq]

        # Variance & Std Dev
        var_pop = sum((x - mean) ** 2 for x in numbers) / n
        std_pop = math.sqrt(var_pop)

        var_sample = sum((x - mean) ** 2 for x in numbers) / (n - 1) if n > 1 else 0.0
        std_sample = math.sqrt(var_sample)

        # Min, Max, Range, IQR
        min_val = sorted_vals[0]
        max_val = sorted_vals[-1]
        val_range = max_val - min_val

        q1 = sorted_vals[n // 4]
        q3 = sorted_vals[(3 * n) // 4]
        iqr = q3 - q1

        return {
            "count": n,
            "sum": s,
            "mean": mean,
            "median": median,
            "mode": modes[0] if len(modes) == 1 else modes,
            "min": min_val,
            "max": max_val,
            "range": val_range,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "variance_pop": var_pop,
            "std_dev_pop": std_pop,
            "variance_sample": var_sample,
            "std_dev_sample": std_sample,
        }

    @staticmethod
    def linear_regression(x_vals: list[float], y_vals: list[float]) -> dict[str, float]:
        """Compute linear regression y = mx + c with Pearson correlation r."""
        if len(x_vals) != len(y_vals) or len(x_vals) < 2:
            raise ValueError("Regression requires at least 2 paired points")

        n = len(x_vals)
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n

        ss_xx = sum((x - mean_x) ** 2 for x in x_vals)
        ss_yy = sum((y - mean_y) ** 2 for y in y_vals)
        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))

        if abs(ss_xx) < 1e-12:
            raise ValueError("All x values are identical, slope is undefined")

        slope = ss_xy / ss_xx
        intercept = mean_y - slope * mean_x
        r = ss_xy / math.sqrt(ss_xx * ss_yy) if (ss_xx * ss_yy) > 0 else 0.0
        r_squared = r ** 2

        return {
            "slope": slope,
            "intercept": intercept,
            "correlation_r": r,
            "r_squared": r_squared
        }
