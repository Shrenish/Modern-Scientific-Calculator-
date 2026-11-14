# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scientific Calculator & Math Assistant built with Python 3 + tkinter. Zero required third-party dependencies — uses only the standard library (`math`, `tkinter`, `re`, `json`, `urllib`, `threading`, `ast`).

## Running & Testing

```bash
# Launch the application
python calculator.py

# Run vigorous unit test suite
python -m unittest tests/test_calculator.py
```

No build step, no package manager, no virtualenv required.

## Key Modules & Architecture

- **`calculator.py`** — Main application window (`ScientificCalculator`) with a multi-tabbed interface (Catppuccin Mocha theme):
  - **Tab 1: 🧮 Calculator**: Scientific & programmer calculator, base conversions (DEC/HEX/OCT/BIN), expression recall, memory, and direct "Plot on Graph" / "Ask Assistant" actions.
  - **Tab 2: 📈 2D Grapher**: Interactive 2D function plotter with zoom/pan, multi-curve plotting $f(x)$ & $g(x)$, root markers, coordinate HUD, and presets. Automatically redraws on tab selection and canvas resize.
  - **Tab 3: 💡 Math Assistant**: Step-by-step problem solver for calculus, equations, geometry, finance, physics, and concepts with 1-click "Insert into Calc" / "Plot Function".
  - **Tab 4: 📐 Units & Constants**: Comprehensive unit converter (12 categories) + searchable CODATA physical constants table with double-click insertion.
  - **Tab 5: 📊 Matrix & Stats**: $2\times2$ and $3\times3$ matrix algebra (determinant, inverse, transpose) + descriptive statistics and linear regression.
  - **Tab 6: ⚙️ Settings**: Model provider configuration (Gemini, OpenRouter, OpenAI, Groq), API key manager, and live connection test.

- **`engine/calc_core.py`** — Core calculation engines:
  - `CalcEngine`: AST validation, safe namespace, angle modes (DEG/RAD/GRAD), memory registers, implicit multiplication, percentage logic.
  - `MatrixEngine`: $2\times2$ and $3\times3$ determinants, adjugate inverses, multiplication, transpose.
  - `StatsEngine`: Descriptive statistics (mean, median, mode, sample/population variance, standard deviation, IQR) and linear regression.
  - `compile_math_expr()`: Fast, safe compilation of expressions $f(x)$ for graphing and numerical calculus with prefix stripping, implicit multiplication, and comprehensive mathematical functions.

- **`engine/ai_engine.py`** — Mathematical problem solver:
  - `LocalMathSolver`: 100% offline symbolic, heuristic, and knowledge base engine for concepts (calculus, Pythagoras, Euler, Fibonacci, Ohm's law), linear and quadratic equations, polynomial derivatives, Simpson's definite integrals, geometry, finance, physics, and arithmetic.
  - `CloudMathAI`: Non-blocking async network client supporting Google Gemini, OpenRouter, OpenAI, and Groq with automatic fallback to `LocalMathSolver`.

- **`engine/grapher.py`** — `GraphCanvas`:
  - Pure Tkinter Canvas 2D grapher with vector curves, dynamic adaptive grid lines, coordinate HUD, bisection root detection, mouse-drag panning, and mouse-wheel zooming.

- **`engine/converters.py`** — `UnitConverter` & `PHYSICAL_CONSTANTS`:
  - 12 categories of unit conversions with exact reference scaling.
  - 24 CODATA physical & astronomical constants.

- **`tests/test_calculator.py`** — 23 automated unit tests for all engines and conversion modules.
