# 🧮 Scientific Calculator & Math Assistant

A powerful, all-in-one Scientific Calculator and Math Assistant built using **Python 3 and Tkinter**. It combines advanced mathematical calculations, interactive graph plotting, AI-powered problem solving, unit conversions, matrix operations, and statistical analysis in a modern desktop interface.

Designed with simplicity, performance, and accessibility in mind, this application requires **zero third-party dependencies** and uses only Python's standard library.

---

## ✨ Key Features

### 🧮 1. Scientific & Programmer Calculator
- Advanced scientific calculations and mathematical expressions.
- Supports DEG, RAD, and GRAD angle modes.
- Programmer calculator with DEC, HEX, OCT, and BIN conversions.
- Memory registers and expression history.
- Implicit multiplication and percentage calculations.
- Direct integration with the Math Assistant and 2D Grapher.

### 📈 2. Interactive 2D Grapher
- Plot mathematical functions such as `f(x)` and `g(x)`.
- Interactive zooming and mouse-drag panning.
- Dynamic adaptive grid and coordinate display.
- Automatic root detection and root markers.
- Multiple curve plotting.
- Built-in graph presets.
- Automatic graph redraw on tab selection and canvas resizing.

### 💡 3. AI Math Assistant
- Step-by-step mathematical problem solving.
- Supports calculus, algebra, geometry, finance, and physics.
- Offline mathematical solver with no internet requirement.
- Cloud AI integration with multiple providers:
  - Google Gemini
  - OpenRouter
  - OpenAI
  - Groq
- Automatic fallback to the local solver.
- One-click options to insert calculations into the calculator or plot functions.

### 📐 4. Units & Physical Constants
- Unit conversion across 12 categories.
- Comprehensive physical and astronomical constants.
- 24 CODATA physical and astronomical constants.
- Searchable constants table.
- Double-click insertion of constants into the calculator.

### 📊 5. Matrix & Statistics
- Supports 2×2 and 3×3 matrices.
- Matrix determinant calculations.
- Matrix inverse and transpose.
- Matrix multiplication.
- Descriptive statistical analysis:
  - Mean
  - Median
  - Mode
  - Variance
  - Standard deviation
  - Interquartile range (IQR)
- Linear regression analysis.

### ⚙️ 6. Settings & Configuration
- Multiple AI model provider configurations.
- API key management.
- Live AI connection testing.
- Customizable model provider selection.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core programming language |
| Tkinter | Graphical user interface |
| Math | Mathematical operations |
| AST | Safe mathematical expression validation |
| Regex | Expression processing |
| JSON | Data handling |
| urllib | Cloud AI communication |
| Threading | Non-blocking background operations |

**Dependencies:** No third-party packages required.

---

## 📁 Project Structure

```text
Scientific-Calculator/
│
├── calculator.py
│
├── engine/
│   ├── calc_core.py
│   ├── ai_engine.py
│   ├── grapher.py
│   └── converters.py
│
├── tests/
│   └── test_calculator.py
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3 installed on your computer.
- Tkinter support enabled in your Python installation.

No additional libraries, package managers, or virtual environments are required.

### 1. Clone the Repository

```bash
git clone https://github.com/Shrenish/Modern-Scientific-Calculator-.git
```

### 2. Navigate to the Project Directory

```bash
cd Modern-Scientific-Calculator-
```

### 3. Run the Application

```bash
python calculator.py
```

The Scientific Calculator application will launch in a desktop window.

---

## 🧪 Testing

The project includes an automated unit test suite containing **23 tests** covering the calculation engines and conversion modules.

Run the test suite using:

```bash
python -m unittest tests/test_calculator.py
```

No build process or additional testing framework is required.

---

## 🧠 Core Architecture

The application follows a modular architecture that separates the graphical interface, mathematical engines, AI functionality, graph plotting, and unit conversion.

### `calculator.py`
Main application window and six-tab graphical interface.

### `engine/calc_core.py`
Contains:
- `CalcEngine`
- `MatrixEngine`
- `StatsEngine`
- `compile_math_expr()`

Handles expression validation, mathematical calculations, matrix operations, statistical analysis, and mathematical expression compilation.

### `engine/ai_engine.py`
Contains:
- `LocalMathSolver`
- `CloudMathAI`

Provides offline mathematical problem solving and asynchronous cloud AI integration.

### `engine/grapher.py`
Contains:
- `GraphCanvas`

Implements interactive 2D mathematical graph plotting using the Tkinter Canvas.

### `engine/converters.py`
Contains:
- `UnitConverter`
- `PHYSICAL_CONSTANTS`

Handles unit conversions and physical constant references.

### `tests/test_calculator.py`
Contains 23 automated unit tests covering the application's core engines and conversion functionality.

---

## 🌟 Design & User Experience

- Modern Catppuccin Mocha-inspired dark interface.
- Six organized application tabs.
- Interactive mathematical tools.
- Integrated calculator, graphing, and AI workflows.
- Offline-first mathematical functionality.
- Lightweight desktop application.

---

## 🔐 Privacy & API Configuration

The local mathematical solver works offline without requiring an API key.

Cloud AI features require an API key from the selected provider. Configure the provider and API key through the application's Settings tab.

Never commit API keys, passwords, or other sensitive credentials to GitHub.

---

## 📌 Project Highlights

- 100% Python-based desktop application.
- Zero required third-party dependencies.
- Six integrated functional modules.
- 23 automated unit tests.
- Offline mathematical problem-solving capabilities.
- Multiple cloud AI provider integrations.
- Interactive mathematical graphing.
- Modular and maintainable architecture.

---

## 👨‍💻 Author

**Shrenish**

GitHub: [@Shrenish](https://github.com/Shrenish)

---

## 📄 License

No license has been specified yet. All rights and permissions are reserved by the project author unless a license is added.

---

**Scientific Calculator & Math Assistant**  
*Making advanced mathematics simpler, smarter, and more accessible.*
