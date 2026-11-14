"""
Scientific Calculator & AI Copilot — World-Class Mathematical Workbench
========================================================================
Features:
- Advanced Scientific & Programmer Calculator
- Interactive 2D Function Graphing Canvas (Pan, Zoom, Roots, Extrema)
- AI Math Copilot: Dual-Brain (Offline Local NLP Solver + Cloud LLM)
- Unit Converter & Physical Constants Library (CODATA standards)
- Matrix & Statistics Laboratory (Linear Algebra, Regression, Descriptive Stats)
- Full Keyboard Navigation & Expression History
"""

from __future__ import annotations

import math
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from engine.ai_engine import AIResult, CloudMathAI, LocalMathSolver
from engine.calc_core import CalcEngine, MatrixEngine, StatsEngine, compile_math_expr
from engine.converters import PHYSICAL_CONSTANTS, ConstantItem, UnitConverter
from engine.grapher import GraphCanvas

# ---------------------------------------------------------------------------
# Theme Constants (Catppuccin Mocha Inspired)
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#1e1e2e",
    "surface": "#181825",
    "mantle": "#11111b",
    "border": "#313244",
    "display_bg": "#181825",
    "display_fg": "#cdd6f4",
    "history_fg": "#6c7086",
    "btn_number": "#313244",
    "btn_number_fg": "#cdd6f4",
    "btn_op": "#45475a",
    "btn_op_fg": "#89b4fa",
    "btn_func": "#363a4f",
    "btn_func_fg": "#b4befe",
    "btn_equal": "#89b4fa",
    "btn_equal_fg": "#11111b",
    "btn_clear": "#f38ba8",
    "btn_clear_fg": "#11111b",
    "btn_special": "#a6e3a1",
    "btn_special_fg": "#11111b",
    "btn_mem": "#f9e2af",
    "btn_mem_fg": "#11111b",
    "btn_ai": "#cba6f7",
    "btn_ai_fg": "#11111b",
    "label_fg": "#a6adc8",
    "accent_blue": "#89b4fa",
    "accent_green": "#a6e3a1",
    "accent_peach": "#fab387",
    "accent_purple": "#cba6f7",
    "error_fg": "#f38ba8",
    "base_fg": "#89b4fa",
    "tab_active_bg": "#313244",
    "tab_inactive_bg": "#181825",
}

PAD_X = 3
PAD_Y = 3


# ---------------------------------------------------------------------------
# Main Application GUI
# ---------------------------------------------------------------------------
class ScientificCalculator(tk.Tk):
    """Next-generation Scientific Calculator with 2D Grapher & Math Assistant."""

    TITLE = "Scientific Calculator & Math Assistant"
    INITIAL_WIDTH = 780
    INITIAL_HEIGHT = 820

    def __init__(self) -> None:
        super().__init__()
        self.engine = CalcEngine()
        self.ai_cloud = CloudMathAI()
        self.ai_local = LocalMathSolver()

        self.expression: str = ""
        self.history_index: int = -1

        self._configure_window()
        self._setup_styles()
        self._build_ui()
        self._bind_keyboard()

    # ------------------------------------------------------------------
    # Window Configuration
    # ------------------------------------------------------------------
    def _configure_window(self) -> None:
        self.title(self.TITLE)
        self.configure(bg=COLORS["bg"])
        self.geometry(f"{self.INITIAL_WIDTH}x{self.INITIAL_HEIGHT}")
        self.minsize(680, 720)
        try:
            self.iconbitmap(default="")
        except tk.TclError:
            pass

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        # Custom Notebook tabs
        style.configure(
            "TNotebook",
            background=COLORS["bg"],
            borderwidth=0,
            tabmargins=[6, 4, 6, 0],
        )
        style.configure(
            "TNotebook.Tab",
            background=COLORS["surface"],
            foreground=COLORS["label_fg"],
            padding=[14, 8],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["btn_number"]), ("active", COLORS["btn_op"])],
            foreground=[("selected", COLORS["accent_blue"]), ("active", COLORS["display_fg"])],
        )

        # Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["btn_number"],
            troughcolor=COLORS["surface"],
            borderwidth=0,
            arrowsize=12,
        )

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        # Top Header Bar
        self._build_header_bar()

        # Tabbed Notebook container
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))

        # Tab 1: Calculator
        self.tab_calc = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_calc, text="  🧮 Calculator  ")
        self._build_calc_tab()

        # Tab 2: 2D Grapher
        self.tab_graph = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_graph, text="  📈 2D Grapher  ")
        self._build_graph_tab()

        # Tab 3: Math Assistant
        self.tab_ai = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_ai, text="  💡 Math Assistant  ")
        self._build_ai_tab()

        # Tab 4: Unit & Constants
        self.tab_units = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_units, text="  📐 Units & Constants  ")
        self._build_units_tab()

        # Tab 5: Matrix & Stats Lab
        self.tab_matrix = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_matrix, text="  📊 Matrix & Stats  ")
        self._build_matrix_tab()

        # Tab 6: Settings
        self.tab_settings = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_settings, text="  ⚙️ Settings  ")
        self._build_settings_tab()

        # Re-render active tab when switched
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event: Any = None) -> None:
        try:
            selected = self.notebook.select()
            if selected == str(self.tab_graph):
                self.after(50, self._on_graph_plot)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Top Header & Status Bar
    # ------------------------------------------------------------------
    def _build_header_bar(self) -> None:
        header = tk.Frame(self, bg=COLORS["bg"], height=34)
        header.pack(fill=tk.X, padx=10, pady=(6, 4))

        # Title & Branding
        title_box = tk.Frame(header, bg=COLORS["bg"])
        title_box.pack(side=tk.LEFT)
        tk.Label(
            title_box,
            text="⚡ SCIENTIFIC CALCULATOR",
            bg=COLORS["bg"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.LEFT)
        tk.Label(
            title_box,
            text=" + MATH ASSISTANT",
            bg=COLORS["bg"],
            fg=COLORS["accent_purple"],
            font=("Segoe UI", 11, "bold"),
        ).pack(side=tk.LEFT)

        # Right side controls: Angle mode & Memory
        right_box = tk.Frame(header, bg=COLORS["bg"])
        right_box.pack(side=tk.RIGHT)

        # Memory indicator
        self.mem_label = tk.Label(
            right_box,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["btn_mem"],
            font=("Consolas", 9, "bold"),
        )
        self.mem_label.pack(side=tk.RIGHT, padx=8)

        # Angle selector radio buttons
        self.angle_var = tk.StringVar(value=self.engine.angle_mode)
        for mode in (CalcEngine.DEG, CalcEngine.RAD, CalcEngine.GRAD):
            rb = tk.Radiobutton(
                right_box,
                text=mode,
                variable=self.angle_var,
                value=mode,
                command=self._on_angle_change,
                bg=COLORS["surface"],
                fg=COLORS["label_fg"],
                selectcolor=COLORS["tab_active_bg"],
                activebackground=COLORS["tab_active_bg"],
                activeforeground=COLORS["accent_purple"],
                font=("Consolas", 8, "bold"),
                indicatoron=False,
                padx=8,
                pady=2,
                relief=tk.FLAT,
                bd=0,
            )
            rb.pack(side=tk.LEFT, padx=2)

    # ==================================================================
    # TAB 1: SCIENTIFIC CALCULATOR
    # ==================================================================
    def _build_calc_tab(self) -> None:
        calc_frame = tk.Frame(self.tab_calc, bg=COLORS["bg"])
        calc_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Display Frame
        disp_frame = tk.Frame(calc_frame, bg=COLORS["display_bg"], bd=1, relief=tk.FLAT)
        disp_frame.pack(fill=tk.X, padx=4, pady=(2, 6))

        # History expression line
        self.history_label = tk.Label(
            disp_frame,
            text="",
            anchor="e",
            bg=COLORS["display_bg"],
            fg=COLORS["history_fg"],
            font=("Consolas", 11),
        )
        self.history_label.pack(fill=tk.X, padx=12, pady=(8, 0))

        # Current expression line
        self.expr_label = tk.Label(
            disp_frame,
            text="",
            anchor="e",
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            font=("Consolas", 18),
        )
        self.expr_label.pack(fill=tk.X, padx=12, pady=(2, 0))

        # Result line
        self.result_label = tk.Label(
            disp_frame,
            text="0",
            anchor="e",
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            font=("Consolas", 32, "bold"),
        )
        self.result_label.pack(fill=tk.X, padx=12, pady=(2, 8))

        # Programmer base conversions row
        base_frame = tk.Frame(calc_frame, bg=COLORS["surface"])
        base_frame.pack(fill=tk.X, padx=4, pady=(0, 6))
        self.base_labels: dict[str, tk.Label] = {}
        for base_name in ("DEC", "HEX", "OCT", "BIN"):
            lbl = tk.Label(
                base_frame,
                text=f"{base_name}: 0",
                bg=COLORS["surface"],
                fg=COLORS["base_fg"],
                font=("Consolas", 8, "bold"),
                padx=8,
                pady=3,
            )
            lbl.pack(side=tk.LEFT)
            self.base_labels[base_name] = lbl

        # Action Quick Bar: [Graph This] [Ask AI About This] [Clear]
        quick_bar = tk.Frame(calc_frame, bg=COLORS["bg"])
        quick_bar.pack(fill=tk.X, padx=4, pady=(0, 4))

        tk.Button(
            quick_bar,
            text="📈 Plot on Graph",
            bg=COLORS["btn_func"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._quick_plot_current,
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            quick_bar,
            text="💡 Ask Assistant to Explain",
            bg=COLORS["btn_func"],
            fg=COLORS["accent_purple"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._quick_ai_explain_current,
        ).pack(side=tk.LEFT, padx=2)

        # Calculator Button Grid
        grid_container = tk.Frame(calc_frame, bg=COLORS["bg"])
        grid_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 6 columns x 10 rows
        layout = [
            # Row 0: Memory + Clear
            [("MC", "mem"), ("MR", "mem"), ("M+", "mem"), ("M−", "mem"), ("AC", "clear"), ("⌫", "clear")],
            # Row 1: Trig & Log
            [("sin", "func"), ("cos", "func"), ("tan", "func"), ("log", "func"), ("ln", "func"), ("π", "special")],
            # Row 2: Inverse Trig & Roots
            [("sin⁻¹", "func"), ("cos⁻¹", "func"), ("tan⁻¹", "func"), ("√", "func"), ("x²", "func"), ("e", "special")],
            # Row 3: Hyperbolic & Powers
            [("sinh", "func"), ("cosh", "func"), ("tanh", "func"), ("∛", "func"), ("xʸ", "op"), ("eˣ", "func")],
            # Row 4: Discrete & Misc
            [("n!", "func"), ("|x|", "func"), ("log₂", "func"), ("(", "op"), (")", "op"), ("%", "op")],
            # Row 5: Combinatorics & Number Theory
            [("nPr", "func"), ("nCr", "func"), ("GCD", "func"), ("LCM", "func"), ("Prime?", "func"), ("Ans", "special")],
            # Row 6: Digits 7,8,9 + Clear & Division
            [("7", "num"), ("8", "num"), ("9", "num"), ("C", "clear"), ("±", "op"), ("÷", "op")],
            # Row 7: Digits 4,5,6 + Multiplication
            [("4", "num"), ("5", "num"), ("6", "num"), ("×", "op"), ("x", "func"), ("^", "op")],
            # Row 8: Digits 1,2,3 + Subtraction
            [("1", "num"), ("2", "num"), ("3", "num"), ("−", "op"), ("⌊x⌋", "func"), ("⌈x⌉", "func")],
            # Row 9: 0, ., +, =
            [("0", "num"), (".", "num"), ("10ˣ", "func"), ("+", "op"), ("Ans", "special"), ("=", "eq")],
        ]

        cmd_map = self._build_cmd_map()
        for r, row in enumerate(layout):
            for c, (label, style) in enumerate(row):
                cmd = cmd_map.get(label, lambda: None)
                self._make_button(grid_container, label, style, cmd, row=r, col=c)

        for c in range(6):
            grid_container.columnconfigure(c, weight=1)
        for r in range(10):
            grid_container.rowconfigure(r, weight=1)

    def _build_cmd_map(self) -> dict[str, Any]:
        return {
            "AC": self._clear,
            "C": self._clear,
            "⌫": self._backspace,
            "7": self._digit("7"),
            "8": self._digit("8"),
            "9": self._digit("9"),
            "4": self._digit("4"),
            "5": self._digit("5"),
            "6": self._digit("6"),
            "1": self._digit("1"),
            "2": self._digit("2"),
            "3": self._digit("3"),
            "0": self._digit("0"),
            ".": self._insert("."),
            "+": self._insert("+"),
            "−": self._insert("-"),
            "-": self._insert("-"),
            "×": self._insert("*"),
            "*": self._insert("*"),
            "÷": self._insert("/"),
            "/": self._insert("/"),
            "%": self._insert("%"),
            "(": self._insert("("),
            ")": self._insert(")"),
            "^": self._insert("^"),
            "=": self._evaluate,
            "±": self._negate,
            "sin": self._fn("sin"),
            "cos": self._fn("cos"),
            "tan": self._fn("tan"),
            "sin⁻¹": self._fn("asin"),
            "cos⁻¹": self._fn("acos"),
            "tan⁻¹": self._fn("atan"),
            "sinh": self._fn("sinh"),
            "cosh": self._fn("cosh"),
            "tanh": self._fn("tanh"),
            "log": self._fn("log"),
            "ln": self._fn("ln"),
            "log₂": self._fn("log2"),
            "√": self._fn("sqrt"),
            "∛": self._fn("cbrt"),
            "x²": self._pow2,
            "xʸ": self._insert("^"),
            "eˣ": self._fn("exp"),
            "10ˣ": lambda: self._append("10^"),
            "n!": self._factorial,
            "|x|": self._fn("abs"),
            "nPr": self._perm,
            "nCr": self._comb,
            "GCD": self._fn("gcd"),
            "LCM": self._fn("lcm"),
            "Prime?": self._fn("isPrime"),
            "⌊x⌋": self._fn("floor"),
            "⌈x⌉": self._fn("ceil"),
            "π": self._insert_const("pi"),
            "e": self._insert_const("e"),
            "x": self._insert("x"),
            "Ans": self._insert_ans,
            "MC": self._mem_clear,
            "MR": self._mem_recall_btn,
            "M+": self._mem_add_btn,
            "M−": self._mem_sub_btn,
        }

    def _make_button(
        self,
        parent: tk.Frame,
        text: str,
        style: str,
        command: Any,
        row: int,
        col: int,
    ) -> tk.Button:
        style_map = {
            "num": (COLORS["btn_number"], COLORS["btn_number_fg"]),
            "op": (COLORS["btn_op"], COLORS["btn_op_fg"]),
            "func": (COLORS["btn_func"], COLORS["btn_func_fg"]),
            "eq": (COLORS["btn_equal"], COLORS["btn_equal_fg"]),
            "clear": (COLORS["btn_clear"], COLORS["btn_clear_fg"]),
            "special": (COLORS["btn_special"], COLORS["btn_special_fg"]),
            "mem": (COLORS["btn_mem"], COLORS["btn_mem_fg"]),
            "ai": (COLORS["btn_ai"], COLORS["btn_ai_fg"]),
        }
        bg, fg = style_map.get(style, (COLORS["btn_number"], COLORS["btn_number_fg"]))
        btn_font = ("Consolas", 11)
        if style == "eq":
            btn_font = ("Consolas", 13, "bold")
        elif style == "func":
            btn_font = ("Consolas", 9, "bold")

        btn = tk.Button(
            parent,
            text=text,
            font=btn_font,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief=tk.FLAT,
            borderwidth=0,
            command=command,
            cursor="hand2",
        )
        btn.grid(row=row, column=col, padx=PAD_X, pady=PAD_Y, sticky="nsew")

        lighter = self._lighten(bg, 25)
        btn.bind("<Enter>", lambda e, b=btn, c=lighter: b.configure(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.configure(bg=c))
        return btn

    @staticmethod
    def _lighten(hex_color: str, amount: int) -> str:
        hex_color = hex_color.lstrip("#")
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ==================================================================
    # TAB 2: 2D FUNCTION GRAPHER
    # ==================================================================
    def _build_graph_tab(self) -> None:
        graph_box = tk.Frame(self.tab_graph, bg=COLORS["bg"])
        graph_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Control Panel: Inputs for f(x) and g(x)
        ctrl_panel = tk.Frame(graph_box, bg=COLORS["surface"], padx=8, pady=6)
        ctrl_panel.pack(fill=tk.X, pady=(0, 6))

        # f(x) Input Row
        f_row = tk.Frame(ctrl_panel, bg=COLORS["surface"])
        f_row.pack(fill=tk.X, pady=2)
        tk.Label(
            f_row,
            text="f(x) =",
            bg=COLORS["surface"],
            fg=COLORS["accent_blue"],
            font=("Consolas", 11, "bold"),
            width=6,
            anchor="e",
        ).pack(side=tk.LEFT)
        self.graph_f_entry = tk.Entry(
            f_row,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Consolas", 11),
            bd=1,
            relief=tk.FLAT,
        )
        self.graph_f_entry.insert(0, "sin(x)")
        self.graph_f_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.graph_f_entry.bind("<Return>", lambda e: self._on_graph_plot())

        # g(x) Input Row
        g_row = tk.Frame(ctrl_panel, bg=COLORS["surface"])
        g_row.pack(fill=tk.X, pady=2)
        tk.Label(
            g_row,
            text="g(x) =",
            bg=COLORS["surface"],
            fg=COLORS["accent_peach"],
            font=("Consolas", 11, "bold"),
            width=6,
            anchor="e",
        ).pack(side=tk.LEFT)
        self.graph_g_entry = tk.Entry(
            g_row,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Consolas", 11),
            bd=1,
            relief=tk.FLAT,
        )
        self.graph_g_entry.insert(0, "cos(x)")
        self.graph_g_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.graph_g_entry.bind("<Return>", lambda e: self._on_graph_plot())

        # Buttons toolbar: [Plot] [Zoom In] [Zoom Out] [Reset View]
        btn_row = tk.Frame(ctrl_panel, bg=COLORS["surface"])
        btn_row.pack(fill=tk.X, pady=(4, 0))

        tk.Button(
            btn_row,
            text="⚡ Plot Curves",
            bg=COLORS["btn_equal"],
            fg=COLORS["btn_equal_fg"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self._on_graph_plot,
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            btn_row,
            text="🔍+ Zoom In",
            bg=COLORS["btn_number"],
            fg=COLORS["display_fg"],
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.graph_canvas.zoom(1.2),
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            btn_row,
            text="🔍- Zoom Out",
            bg=COLORS["btn_number"],
            fg=COLORS["display_fg"],
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.graph_canvas.zoom(1 / 1.2),
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            btn_row,
            text="↺ Reset View",
            bg=COLORS["btn_number"],
            fg=COLORS["display_fg"],
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.graph_canvas.reset_view(),
        ).pack(side=tk.LEFT, padx=3)

        # Preset curve chips
        presets = [("sin(x)", "sin(x)"), ("x² - 4", "x**2 - 4"), ("x³ - 3x", "x**3 - 3*x"), ("eˣ", "exp(x)"), ("Gaussian", "exp(-x**2)"), ("sinc(x)", "sin(x)/x")]
        preset_frame = tk.Frame(ctrl_panel, bg=COLORS["surface"])
        preset_frame.pack(side=tk.RIGHT)
        for label, expr in presets:
            tk.Button(
                preset_frame,
                text=label,
                bg=COLORS["btn_op"],
                fg=COLORS["display_fg"],
                font=("Segoe UI", 7),
                relief=tk.FLAT,
                padx=5,
                pady=2,
                cursor="hand2",
                command=lambda e=expr: self._apply_graph_preset(e),
            ).pack(side=tk.LEFT, padx=2)

        # Embedded Graph Canvas
        self.graph_canvas = GraphCanvas(graph_box)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        self.after(100, self._on_graph_plot)

    def _on_graph_plot(self) -> None:
        f_expr = self.graph_f_entry.get().strip()
        g_expr = self.graph_g_entry.get().strip()
        self.graph_canvas.set_functions(f_expr, g_expr)

    def _apply_graph_preset(self, expr: str) -> None:
        self.graph_f_entry.delete(0, tk.END)
        self.graph_f_entry.insert(0, expr)
        self._on_graph_plot()

    def plot_external_function(self, expr: str) -> None:
        """Plot a function triggered from AI or calculator."""
        self.notebook.select(self.tab_graph)
        self.graph_f_entry.delete(0, tk.END)
        self.graph_f_entry.insert(0, expr)
        self._on_graph_plot()

    # ==================================================================
    # TAB 3: MATHEMATICAL ASSISTANT & PROBLEM SOLVER
    # ==================================================================
    def _build_ai_tab(self) -> None:
        ai_box = tk.Frame(self.tab_ai, bg=COLORS["bg"])
        ai_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Header status banner
        status_bar = tk.Frame(ai_box, bg=COLORS["surface"], padx=8, pady=4)
        status_bar.pack(fill=tk.X, pady=(0, 6))

        provider_name = self.ai_cloud.config.get("provider", "Gemini")
        has_key = bool(self.ai_cloud.config.get("api_key", "").strip())
        mode_text = f"Mode: {provider_name} Cloud Engine" if has_key else "Mode: Offline Mathematical Engine (Zero Setup)"
        mode_fg = COLORS["accent_green"] if has_key else COLORS["accent_peach"]

        self.ai_mode_badge = tk.Label(
            status_bar,
            text=f"● {mode_text}",
            bg=COLORS["surface"],
            fg=mode_fg,
            font=("Segoe UI", 9, "bold"),
        )
        self.ai_mode_badge.pack(side=tk.LEFT)

        tk.Label(
            status_bar,
            text="Ask word problems, calculus, algebra, physics, or finance",
            bg=COLORS["surface"],
            fg=COLORS["history_fg"],
            font=("Segoe UI", 8),
        ).pack(side=tk.RIGHT)

        # Quick Example Chips
        chips_frame = tk.Frame(ai_box, bg=COLORS["bg"])
        chips_frame.pack(fill=tk.X, pady=(0, 6))
        chips = [
            "Derivative of 3x^3 - 5x^2 + 7",
            "Integrate sin(x) from 0 to pi",
            "Solve 2x + 5 = 15",
            "Solve x^2 - 5x + 6 = 0",
            "What is calculus",
            "Compound interest $10,000 at 5% for 10 yrs",
            "Convert 100 km to miles",
        ]
        for chip in chips:
            tk.Button(
                chips_frame,
                text=chip,
                bg=COLORS["btn_number"],
                fg=COLORS["label_fg"],
                font=("Segoe UI", 8),
                relief=tk.FLAT,
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda c=chip: self._set_ai_query(c),
            ).pack(side=tk.LEFT, padx=3, pady=2)

        # Chat Stream (Scrollable text)
        chat_frame = tk.Frame(ai_box, bg=COLORS["surface"])
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        self.ai_chat_text = tk.Text(
            chat_frame,
            bg=COLORS["surface"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            bd=0,
            padx=12,
            pady=10,
        )
        scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.ai_chat_text.yview)
        self.ai_chat_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ai_chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tags styling
        self.ai_chat_text.tag_config("user_msg", foreground=COLORS["accent_blue"], font=("Segoe UI", 10, "bold"))
        self.ai_chat_text.tag_config("ai_title", foreground=COLORS["accent_purple"], font=("Segoe UI", 11, "bold"))
        self.ai_chat_text.tag_config("ai_step", foreground=COLORS["display_fg"], font=("Consolas", 10))
        self.ai_chat_text.tag_config("ai_ans", foreground=COLORS["accent_green"], font=("Consolas", 11, "bold"))
        self.ai_chat_text.tag_config("ai_source", foreground=COLORS["history_fg"], font=("Segoe UI", 8, "italic"))

        # Welcome message
        self._append_ai_welcome()

        # Action Buttons Row (for latest response)
        self.ai_action_frame = tk.Frame(ai_box, bg=COLORS["bg"])
        self.ai_action_frame.pack(fill=tk.X, pady=(0, 6))

        self.btn_insert_calc = tk.Button(
            self.ai_action_frame,
            text="📥 Insert Answer into Calculator",
            bg=COLORS["btn_func"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._insert_ai_calc_expr,
        )
        self.btn_insert_calc.pack(side=tk.LEFT, padx=3)

        self.btn_plot_ai = tk.Button(
            self.ai_action_frame,
            text="📈 Plot Function on Grapher",
            bg=COLORS["btn_func"],
            fg=COLORS["accent_peach"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._plot_ai_func,
        )
        self.btn_plot_ai.pack(side=tk.LEFT, padx=3)

        self._last_ai_calc_expr = ""
        self._last_ai_plot_expr = ""

        # Bottom Input Bar
        input_bar = tk.Frame(ai_box, bg=COLORS["surface"], padx=6, pady=6)
        input_bar.pack(fill=tk.X)

        self.ai_entry = tk.Entry(
            input_bar,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Segoe UI", 11),
            bd=1,
            relief=tk.FLAT,
        )
        self.ai_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 6))
        self.ai_entry.bind("<Return>", lambda e: self._on_ai_submit())

        self.btn_ai_send = tk.Button(
            input_bar,
            text="💡 Ask Assistant",
            bg=COLORS["btn_ai"],
            fg=COLORS["btn_ai_fg"],
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self._on_ai_submit,
        )
        self.btn_ai_send.pack(side=tk.RIGHT)

    def _append_ai_welcome(self) -> None:
        self.ai_chat_text.insert(tk.END, "💡 Math Assistant is ready!\n", "ai_title")
        self.ai_chat_text.insert(
            tk.END,
            "Ask any question in natural language (e.g. word math problems, calculus derivations, algebra, geometry, physics, or financial calculations).\n"
            "Both an Offline Symbolic Solver and Cloud LLMs are fully supported!\n\n",
            "ai_step",
        )

    def _set_ai_query(self, query: str) -> None:
        self.ai_entry.delete(0, tk.END)
        self.ai_entry.insert(0, query)
        self._on_ai_submit()

    def _on_ai_submit(self) -> None:
        query = self.ai_entry.get().strip()
        if not query:
            return

        self.ai_entry.delete(0, tk.END)
        self.ai_chat_text.insert(tk.END, f"\nUser: {query}\n", "user_msg")
        self.ai_chat_text.insert(tk.END, "Thinking & computing step-by-step solution...\n", "ai_source")
        self.ai_chat_text.see(tk.END)

        self.btn_ai_send.configure(state=tk.DISABLED, text="Computing...")

        # Asynchronous call through dual-brain CloudMathAI
        def on_success(res: AIResult) -> None:
            self.after(0, lambda: self._render_ai_result(res))

        def on_error(err: str) -> None:
            self.after(0, lambda: self._render_ai_error(err))

        self.ai_cloud.query_async(query, [], on_success, on_error)

    def _render_ai_result(self, res: AIResult) -> None:
        self.btn_ai_send.configure(state=tk.NORMAL, text="💡 Ask Assistant")

        self.ai_chat_text.insert(tk.END, f"\n{res.summary}\n", "ai_title")
        for step in res.steps:
            self.ai_chat_text.insert(tk.END, f"  • {step}\n", "ai_step")
        if res.answer:
            self.ai_chat_text.insert(tk.END, f"Answer: {res.answer}\n", "ai_ans")
        self.ai_chat_text.insert(tk.END, f"Source: {res.source}\n\n", "ai_source")
        self.ai_chat_text.see(tk.END)

        # Update action buttons
        self._last_ai_calc_expr = res.calc_expression or res.answer
        self._last_ai_plot_expr = res.plot_expression

        if self._last_ai_calc_expr:
            self.btn_insert_calc.configure(state=tk.NORMAL)
        else:
            self.btn_insert_calc.configure(state=tk.DISABLED)

        if self._last_ai_plot_expr:
            self.btn_plot_ai.configure(state=tk.NORMAL)
        else:
            self.btn_plot_ai.configure(state=tk.DISABLED)

    def _render_ai_error(self, err: str) -> None:
        self.btn_ai_send.configure(state=tk.NORMAL, text="💡 Ask Assistant")
        self.ai_chat_text.insert(tk.END, f"Notice: {err}\n\n", "ai_source")
        self.ai_chat_text.see(tk.END)

    def _insert_ai_calc_expr(self) -> None:
        if self._last_ai_calc_expr:
            self.notebook.select(self.tab_calc)
            self.expression = str(self._last_ai_calc_expr)
            self._update_display()

    def _plot_ai_func(self) -> None:
        if self._last_ai_plot_expr:
            self.plot_external_function(self._last_ai_plot_expr)

    # ==================================================================
    # TAB 4: UNITS & CONSTANTS STUDIO
    # ==================================================================
    def _build_units_tab(self) -> None:
        main_units_frame = tk.Frame(self.tab_units, bg=COLORS["bg"])
        main_units_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Upper Section: Unit Converter
        conv_label = tk.Label(
            main_units_frame,
            text="🔄 MULTI-UNIT CONVERTER",
            bg=COLORS["bg"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 11, "bold"),
        )
        conv_label.pack(anchor="w", pady=(0, 4))

        conv_card = tk.Frame(main_units_frame, bg=COLORS["surface"], padx=10, pady=8)
        conv_card.pack(fill=tk.X, pady=(0, 10))

        # Category Selector
        cat_row = tk.Frame(conv_card, bg=COLORS["surface"])
        cat_row.pack(fill=tk.X, pady=4)
        tk.Label(cat_row, text="Category:", bg=COLORS["surface"], fg=COLORS["label_fg"], font=("Segoe UI", 9, "bold"), width=10, anchor="w").pack(side=tk.LEFT)
        self.unit_cat_var = tk.StringVar(value="Length")
        self.unit_cat_cb = ttk.Combobox(cat_row, textvariable=self.unit_cat_var, values=UnitConverter.get_categories(), state="readonly", width=22)
        self.unit_cat_cb.pack(side=tk.LEFT)
        self.unit_cat_cb.bind("<<ComboboxSelected>>", self._on_unit_cat_changed)

        # From Value & Unit
        from_row = tk.Frame(conv_card, bg=COLORS["surface"])
        from_row.pack(fill=tk.X, pady=4)
        tk.Label(from_row, text="From:", bg=COLORS["surface"], fg=COLORS["label_fg"], font=("Segoe UI", 9, "bold"), width=10, anchor="w").pack(side=tk.LEFT)
        self.unit_from_val = tk.Entry(from_row, bg=COLORS["display_bg"], fg=COLORS["display_fg"], insertbackground=COLORS["display_fg"], font=("Consolas", 11), width=14, bd=1, relief=tk.FLAT)
        self.unit_from_val.insert(0, "1.0")
        self.unit_from_val.pack(side=tk.LEFT, padx=(0, 6))
        self.unit_from_val.bind("<KeyRelease>", lambda e: self._on_unit_convert())

        self.unit_from_var = tk.StringVar()
        self.unit_from_cb = ttk.Combobox(from_row, textvariable=self.unit_from_var, state="readonly", width=24)
        self.unit_from_cb.pack(side=tk.LEFT)
        self.unit_from_cb.bind("<<ComboboxSelected>>", lambda e: self._on_unit_convert())

        # To Value & Unit
        to_row = tk.Frame(conv_card, bg=COLORS["surface"])
        to_row.pack(fill=tk.X, pady=4)
        tk.Label(to_row, text="To:", bg=COLORS["surface"], fg=COLORS["label_fg"], font=("Segoe UI", 9, "bold"), width=10, anchor="w").pack(side=tk.LEFT)
        self.unit_to_val = tk.Label(to_row, text="0.0", bg=COLORS["display_bg"], fg=COLORS["accent_green"], font=("Consolas", 12, "bold"), width=14, anchor="w", padx=4)
        self.unit_to_val.pack(side=tk.LEFT, padx=(0, 6))

        self.unit_to_var = tk.StringVar()
        self.unit_to_cb = ttk.Combobox(to_row, textvariable=self.unit_to_var, state="readonly", width=24)
        self.unit_to_cb.pack(side=tk.LEFT)
        self.unit_to_cb.bind("<<ComboboxSelected>>", lambda e: self._on_unit_convert())

        tk.Button(
            to_row,
            text="📥 Send to Calculator",
            bg=COLORS["btn_func"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self._send_unit_result_to_calc,
        ).pack(side=tk.LEFT, padx=8)

        # Initialize combo values
        self._on_unit_cat_changed()

        # Lower Section: Physical Constants Table
        const_label = tk.Label(
            main_units_frame,
            text="⚛️ PHYSICAL & ASTRONOMICAL CONSTANTS (CODATA)",
            bg=COLORS["bg"],
            fg=COLORS["accent_purple"],
            font=("Segoe UI", 11, "bold"),
        )
        const_label.pack(anchor="w", pady=(6, 4))

        # Search Bar for Constants
        search_row = tk.Frame(main_units_frame, bg=COLORS["bg"])
        search_row.pack(fill=tk.X, pady=(0, 4))
        tk.Label(search_row, text="Search Constant:", bg=COLORS["bg"], fg=COLORS["label_fg"], font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.const_search_entry = tk.Entry(
            search_row,
            bg=COLORS["surface"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Segoe UI", 9),
            bd=1,
            relief=tk.FLAT,
            width=24,
        )
        self.const_search_entry.pack(side=tk.LEFT, padx=6)
        self.const_search_entry.bind("<KeyRelease>", self._on_const_search)

        # Constants Treeview
        tree_frame = tk.Frame(main_units_frame, bg=COLORS["surface"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("symbol", "name", "value", "unit", "category")
        self.const_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.const_tree.heading("symbol", text="Symbol")
        self.const_tree.heading("name", text="Name")
        self.const_tree.heading("value", text="Value")
        self.const_tree.heading("unit", text="Unit")
        self.const_tree.heading("category", text="Category")

        self.const_tree.column("symbol", width=80, anchor="center")
        self.const_tree.column("name", width=200, anchor="w")
        self.const_tree.column("value", width=140, anchor="e")
        self.const_tree.column("unit", width=120, anchor="w")
        self.const_tree.column("category", width=100, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.const_tree.yview)
        self.const_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.const_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Populate constants
        self._populate_constants(PHYSICAL_CONSTANTS)

        # Double click to insert constant into calculator
        self.const_tree.bind("<Double-1>", self._on_const_double_click)

        tk.Label(
            main_units_frame,
            text="Tip: Double-click any constant to insert its numerical value directly into the calculator expression!",
            bg=COLORS["bg"],
            fg=COLORS["history_fg"],
            font=("Segoe UI", 8, "italic"),
        ).pack(anchor="w", pady=(4, 0))

    def _on_unit_cat_changed(self, event: Any = None) -> None:
        cat = self.unit_cat_var.get()
        units = UnitConverter.get_units(cat)
        self.unit_from_cb["values"] = units
        self.unit_to_cb["values"] = units
        if units:
            self.unit_from_var.set(units[0])
            self.unit_to_var.set(units[1] if len(units) > 1 else units[0])
        self._on_unit_convert()

    def _on_unit_convert(self) -> None:
        try:
            val = float(self.unit_from_val.get())
            cat = self.unit_cat_var.get()
            u_from = self.unit_from_var.get()
            u_to = self.unit_to_var.get()
            if u_from and u_to:
                res = UnitConverter.convert(val, cat, u_from, u_to)
                self.unit_to_val.configure(text=f"{res:.8g}")
        except Exception:
            self.unit_to_val.configure(text="---")

    def _send_unit_result_to_calc(self) -> None:
        res_str = self.unit_to_val.cget("text")
        if res_str and res_str != "---":
            self.notebook.select(self.tab_calc)
            self._append(res_str)

    def _populate_constants(self, items: list[ConstantItem]) -> None:
        self.const_tree.delete(*self.const_tree.get_children())
        for c in items:
            self.const_tree.insert("", tk.END, values=(c.symbol, c.name, f"{c.value:.8e}", c.unit, c.category))

    def _on_const_search(self, event: Any = None) -> None:
        query = self.const_search_entry.get().lower().strip()
        filtered = [
            c for c in PHYSICAL_CONSTANTS
            if query in c.name.lower() or query in c.symbol.lower() or query in c.category.lower()
        ]
        self._populate_constants(filtered)

    def _on_const_double_click(self, event: Any = None) -> None:
        selected = self.const_tree.selection()
        if not selected:
            return
        item_vals = self.const_tree.item(selected[0], "values")
        if item_vals:
            val_str = item_vals[2]
            self.notebook.select(self.tab_calc)
            self._append(val_str)

    # ==================================================================
    # TAB 5: MATRIX & STATISTICS LAB
    # ==================================================================
    def _build_matrix_tab(self) -> None:
        lab_frame = tk.Frame(self.tab_matrix, bg=COLORS["bg"])
        lab_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Upper: Matrix Section
        tk.Label(
            lab_frame,
            text="🔢 MATRIX & LINEAR ALGEBRA",
            bg=COLORS["bg"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        matrix_card = tk.Frame(lab_frame, bg=COLORS["surface"], padx=10, pady=8)
        matrix_card.pack(fill=tk.X, pady=(0, 10))

        # Size toggle: 2x2 or 3x3
        m_ctrl_row = tk.Frame(matrix_card, bg=COLORS["surface"])
        m_ctrl_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(m_ctrl_row, text="Matrix Size:", bg=COLORS["surface"], fg=COLORS["label_fg"], font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.matrix_size_var = tk.StringVar(value="2x2")
        for sz in ("2x2", "3x3"):
            tk.Radiobutton(
                m_ctrl_row,
                text=sz,
                variable=self.matrix_size_var,
                value=sz,
                command=self._on_matrix_size_change,
                bg=COLORS["surface"],
                fg=COLORS["accent_blue"],
                selectcolor=COLORS["surface"],
                activebackground=COLORS["surface"],
                font=("Segoe UI", 9),
            ).pack(side=tk.LEFT, padx=4)

        # Matrix Grid Inputs
        self.m_entries_frame = tk.Frame(matrix_card, bg=COLORS["surface"])
        self.m_entries_frame.pack(side=tk.LEFT, padx=(0, 16))
        self.m_entries: list[list[tk.Entry]] = []
        self._build_matrix_entries(2)

        # Operations buttons
        m_btn_box = tk.Frame(matrix_card, bg=COLORS["surface"])
        m_btn_box.pack(side=tk.LEFT, padx=8)

        tk.Button(m_btn_box, text="Determinant (det)", bg=COLORS["btn_func"], fg=COLORS["display_fg"], font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2", command=self._calc_matrix_det).pack(fill=tk.X, pady=2)
        tk.Button(m_btn_box, text="Inverse (A⁻¹)", bg=COLORS["btn_func"], fg=COLORS["display_fg"], font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2", command=self._calc_matrix_inverse).pack(fill=tk.X, pady=2)
        tk.Button(m_btn_box, text="Transpose (Aᵀ)", bg=COLORS["btn_func"], fg=COLORS["display_fg"], font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=8, pady=3, cursor="hand2", command=self._calc_matrix_transpose).pack(fill=tk.X, pady=2)

        # Matrix result display
        self.matrix_res_label = tk.Label(
            matrix_card,
            text="Result:\nReady",
            bg=COLORS["display_bg"],
            fg=COLORS["accent_green"],
            font=("Consolas", 10),
            justify=tk.LEFT,
            padx=10,
            pady=6,
            relief=tk.FLAT,
        )
        self.matrix_res_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6)

        # Lower: Statistics Analyzer Section
        tk.Label(
            lab_frame,
            text="📊 DESCRIPTIVE STATISTICS & REGRESSION",
            bg=COLORS["bg"],
            fg=COLORS["accent_peach"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(8, 4))

        stats_card = tk.Frame(lab_frame, bg=COLORS["surface"], padx=10, pady=8)
        stats_card.pack(fill=tk.BOTH, expand=True)

        stats_in_row = tk.Frame(stats_card, bg=COLORS["surface"])
        stats_in_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(stats_in_row, text="Dataset (comma or space separated):", bg=COLORS["surface"], fg=COLORS["label_fg"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.stats_entry = tk.Entry(
            stats_in_row,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Consolas", 10),
            bd=1,
            relief=tk.FLAT,
        )
        self.stats_entry.insert(0, "4, 8, 15, 16, 23, 42, 55, 68, 72")
        self.stats_entry.pack(fill=tk.X, pady=(2, 4))

        tk.Button(
            stats_in_row,
            text="📈 Analyze Dataset",
            bg=COLORS["btn_equal"],
            fg=COLORS["btn_equal_fg"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self._on_analyze_stats,
        ).pack(side=tk.LEFT)

        # Statistics Results Text
        self.stats_res_text = tk.Text(
            stats_card,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            font=("Consolas", 9),
            height=8,
            bd=0,
            padx=8,
            pady=6,
        )
        self.stats_res_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

    def _build_matrix_entries(self, n: int) -> None:
        for widget in self.m_entries_frame.winfo_children():
            widget.destroy()
        self.m_entries = []
        for r in range(n):
            row_entries = []
            for c in range(n):
                e = tk.Entry(
                    self.m_entries_frame,
                    bg=COLORS["display_bg"],
                    fg=COLORS["display_fg"],
                    insertbackground=COLORS["display_fg"],
                    font=("Consolas", 10, "bold"),
                    width=5,
                    justify="center",
                    bd=1,
                    relief=tk.FLAT,
                )
                e.insert(0, "1" if r == c else "0")
                e.grid(row=r, column=c, padx=3, pady=3)
                row_entries.append(e)
            self.m_entries.append(row_entries)

    def _on_matrix_size_change(self) -> None:
        sz = self.matrix_size_var.get()
        n = 2 if sz == "2x2" else 3
        self._build_matrix_entries(n)

    def _read_matrix(self) -> list[list[float]]:
        mat = []
        for row in self.m_entries:
            row_vals = []
            for e in row:
                row_vals.append(float(e.get().strip() or 0.0))
            mat.append(row_vals)
        return mat

    def _calc_matrix_det(self) -> None:
        try:
            m = self._read_matrix()
            det = MatrixEngine.det2(m) if len(m) == 2 else MatrixEngine.det3(m)
            self.matrix_res_label.configure(text=f"Determinant:\n|A| = {det:g}")
        except Exception as ex:
            self.matrix_res_label.configure(text=f"Error:\n{ex}")

    def _calc_matrix_inverse(self) -> None:
        try:
            m = self._read_matrix()
            inv = MatrixEngine.inverse2(m) if len(m) == 2 else MatrixEngine.inverse3(m)
            lines = ["Inverse A⁻¹:"]
            for row in inv:
                lines.append("  [" + ", ".join(f"{x:8.4g}" for x in row) + "]")
            self.matrix_res_label.configure(text="\n".join(lines))
        except Exception as ex:
            self.matrix_res_label.configure(text=f"Error:\n{ex}")

    def _calc_matrix_transpose(self) -> None:
        try:
            m = self._read_matrix()
            trans = MatrixEngine.transpose(m)
            lines = ["Transpose Aᵀ:"]
            for row in trans:
                lines.append("  [" + ", ".join(f"{x:8.4g}" for x in row) + "]")
            self.matrix_res_label.configure(text="\n".join(lines))
        except Exception as ex:
            self.matrix_res_label.configure(text=f"Error:\n{ex}")

    def _on_analyze_stats(self) -> None:
        raw_text = self.stats_entry.get().strip()
        import re
        nums = [float(x) for x in re.findall(r"[+-]?\d+(?:\.\d+)?", raw_text)]
        if not nums:
            self.stats_res_text.delete("1.0", tk.END)
            self.stats_res_text.insert(tk.END, "Error: No valid numbers found in dataset.\n")
            return

        try:
            res = StatsEngine.analyze(nums)
            self.stats_res_text.delete("1.0", tk.END)
            out = f"""DESCRIPTIVE STATISTICS SUMMARY:
------------------------------------------------------------
Count (N)        : {res['count']}
Sum (Σx)         : {res['sum']:g}
Mean (μ)         : {res['mean']:g}
Median           : {res['median']:g}
Mode             : {res['mode']}
Min              : {res['min']:g}
Max              : {res['max']:g}
Range            : {res['range']:g}
Q1 / Q3 / IQR    : {res['q1']:g} / {res['q3']:g} / {res['iqr']:g}
Sample Variance  : {res['variance_sample']:.6g}
Sample Std Dev (s): {res['std_dev_sample']:.6g}
Pop. Std Dev (σ) : {res['std_dev_pop']:.6g}
"""
            self.stats_res_text.insert(tk.END, out)
        except Exception as ex:
            self.stats_res_text.delete("1.0", tk.END)
            self.stats_res_text.insert(tk.END, f"Error: {ex}\n")

    # ==================================================================
    # TAB 6: AI CONFIGURATION & SETTINGS
    # ==================================================================
    def _build_settings_tab(self) -> None:
        settings_box = tk.Frame(self.tab_settings, bg=COLORS["bg"])
        settings_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        tk.Label(
            settings_box,
            text="⚙️ MATHEMATICAL ASSISTANT CONFIGURATION",
            bg=COLORS["bg"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            settings_box,
            text="The Math Assistant includes a complete Offline Knowledge & Symbolic Engine by default.\n"
                 "To optionally enable Cloud LLM reasoning (Gemini, OpenRouter, OpenAI, Groq), configure below.",
            bg=COLORS["bg"],
            fg=COLORS["label_fg"],
            font=("Segoe UI", 9),
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 10))

        card = tk.Frame(settings_box, bg=COLORS["surface"], padx=14, pady=12)
        card.pack(fill=tk.X, pady=(0, 10))

        # Provider
        p_row = tk.Frame(card, bg=COLORS["surface"])
        p_row.pack(fill=tk.X, pady=6)
        tk.Label(p_row, text="Model Provider:", bg=COLORS["surface"], fg=COLORS["display_fg"], font=("Segoe UI", 9, "bold"), width=16, anchor="w").pack(side=tk.LEFT)
        self.cfg_provider_var = tk.StringVar(value=self.ai_cloud.config.get("provider", "Gemini"))
        self.cfg_provider_cb = ttk.Combobox(
            p_row,
            textvariable=self.cfg_provider_var,
            values=["Gemini", "OpenRouter", "OpenAI", "Groq"],
            state="readonly",
            width=20,
        )
        self.cfg_provider_cb.pack(side=tk.LEFT)

        # API Key
        k_row = tk.Frame(card, bg=COLORS["surface"])
        k_row.pack(fill=tk.X, pady=6)
        tk.Label(k_row, text="API Key:", bg=COLORS["surface"], fg=COLORS["display_fg"], font=("Segoe UI", 9, "bold"), width=16, anchor="w").pack(side=tk.LEFT)
        self.cfg_key_entry = tk.Entry(
            k_row,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Consolas", 10),
            show="*",
            width=36,
            bd=1,
            relief=tk.FLAT,
        )
        self.cfg_key_entry.insert(0, self.ai_cloud.config.get("api_key", ""))
        self.cfg_key_entry.pack(side=tk.LEFT, padx=(0, 6))

        self.cfg_show_key = tk.BooleanVar(value=False)
        tk.Checkbutton(
            k_row,
            text="Show",
            variable=self.cfg_show_key,
            command=self._toggle_show_key,
            bg=COLORS["surface"],
            fg=COLORS["label_fg"],
            selectcolor=COLORS["surface"],
            activebackground=COLORS["surface"],
            font=("Segoe UI", 8),
        ).pack(side=tk.LEFT)

        # Model Name
        m_row = tk.Frame(card, bg=COLORS["surface"])
        m_row.pack(fill=tk.X, pady=6)
        tk.Label(m_row, text="Model Identifier:", bg=COLORS["surface"], fg=COLORS["display_fg"], font=("Segoe UI", 9, "bold"), width=16, anchor="w").pack(side=tk.LEFT)
        self.cfg_model_entry = tk.Entry(
            m_row,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Consolas", 10),
            width=36,
            bd=1,
            relief=tk.FLAT,
        )
        self.cfg_model_entry.insert(0, self.ai_cloud.config.get("model", "gemini-1.5-flash"))
        self.cfg_model_entry.pack(side=tk.LEFT)

        # Base URL override (optional)
        u_row = tk.Frame(card, bg=COLORS["surface"])
        u_row.pack(fill=tk.X, pady=6)
        tk.Label(u_row, text="Custom Base URL:", bg=COLORS["surface"], fg=COLORS["display_fg"], font=("Segoe UI", 9, "bold"), width=16, anchor="w").pack(side=tk.LEFT)
        self.cfg_url_entry = tk.Entry(
            u_row,
            bg=COLORS["display_bg"],
            fg=COLORS["display_fg"],
            insertbackground=COLORS["display_fg"],
            font=("Consolas", 10),
            width=36,
            bd=1,
            relief=tk.FLAT,
        )
        self.cfg_url_entry.insert(0, self.ai_cloud.config.get("custom_base_url", ""))
        self.cfg_url_entry.pack(side=tk.LEFT)

        # Save and Test Buttons
        action_row = tk.Frame(card, bg=COLORS["surface"])
        action_row.pack(fill=tk.X, pady=(10, 4))

        tk.Button(
            action_row,
            text="💾 Save AI Settings",
            bg=COLORS["btn_equal"],
            fg=COLORS["btn_equal_fg"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self._save_ai_settings,
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.btn_test_conn = tk.Button(
            action_row,
            text="⚡ Test Connection",
            bg=COLORS["btn_func"],
            fg=COLORS["accent_blue"],
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self._test_ai_connection,
        )
        self.btn_test_conn.pack(side=tk.LEFT)

        self.cfg_status_label = tk.Label(
            settings_box,
            text="",
            bg=COLORS["bg"],
            fg=COLORS["accent_green"],
            font=("Segoe UI", 9, "bold"),
        )
        self.cfg_status_label.pack(anchor="w", pady=4)

    def _toggle_show_key(self) -> None:
        self.cfg_key_entry.configure(show="" if self.cfg_show_key.get() else "*")

    def _save_ai_settings(self) -> None:
        new_cfg = {
            "provider": self.cfg_provider_var.get(),
            "api_key": self.cfg_key_entry.get().strip(),
            "model": self.cfg_model_entry.get().strip(),
            "custom_base_url": self.cfg_url_entry.get().strip(),
        }
        self.ai_cloud.save_config(new_cfg)
        self.cfg_status_label.configure(text="✓ Settings successfully saved!", fg=COLORS["accent_green"])

        # Update badge on tab 3
        has_key = bool(new_cfg["api_key"])
        mode_text = f"Mode: {new_cfg['provider']} Cloud Engine" if has_key else "Mode: Offline Mathematical Engine (Zero Setup)"
        mode_fg = COLORS["accent_green"] if has_key else COLORS["accent_peach"]
        self.ai_mode_badge.configure(text=f"● {mode_text}", fg=mode_fg)

    def _test_ai_connection(self) -> None:
        self._save_ai_settings()
        self.cfg_status_label.configure(text="Connecting to model service...", fg=COLORS["accent_peach"])
        self.btn_test_conn.configure(state=tk.DISABLED)

        def on_ok(res: AIResult) -> None:
            def _ui():
                self.btn_test_conn.configure(state=tk.NORMAL)
                self.cfg_status_label.configure(
                    text=f"✓ Connection verified via {res.source}!",
                    fg=COLORS["accent_green"]
                )
            self.after(0, _ui)

        def on_fail(err: str) -> None:
            def _ui():
                self.btn_test_conn.configure(state=tk.NORMAL)
                self.cfg_status_label.configure(
                    text=f"Notice: ({err}). Offline Math Engine will be used.",
                    fg=COLORS["accent_peach"]
                )
            self.after(0, _ui)

        self.ai_cloud.query_async("compute 3 + 5", [], on_ok, on_fail)

    # ------------------------------------------------------------------
    # Quick Actions from Calculator Tab
    # ------------------------------------------------------------------
    def _quick_plot_current(self) -> None:
        expr = self.expression.strip()
        if not expr:
            expr = "sin(x)"
        self.plot_external_function(expr)

    def _quick_ai_explain_current(self) -> None:
        expr = self.expression.strip()
        if not expr:
            return
        self.notebook.select(self.tab_ai)
        self._set_ai_query(f"Explain and solve step-by-step: {expr}")

    # ------------------------------------------------------------------
    # Display & Expression Handling
    # ------------------------------------------------------------------
    def _update_display(self) -> None:
        self.expr_label.configure(text=self.expression)
        try:
            val = int(float(self.expression)) if self.expression else 0
            self.base_labels["DEC"].configure(text=f"DEC: {val}")
            self.base_labels["HEX"].configure(text=f"HEX: {hex(val).upper()}")
            self.base_labels["OCT"].configure(text=f"OCT: {oct(val)}")
            self.base_labels["BIN"].configure(text=f"BIN: {bin(val)}")
        except (ValueError, OverflowError):
            self.base_labels["DEC"].configure(text="DEC: 0")
            self.base_labels["HEX"].configure(text="HEX: 0x0")
            self.base_labels["OCT"].configure(text="OCT: 0o0")
            self.base_labels["BIN"].configure(text="BIN: 0b0")

    def _show_result(self, value: str) -> None:
        self.result_label.configure(text=value, fg=COLORS["display_fg"])

    def _show_error(self, msg: str) -> None:
        self.result_label.configure(text=msg, fg=COLORS["error_fg"])

    def _update_mem_indicator(self) -> None:
        if self.engine.memory != 0:
            self.mem_label.configure(text=f"M = {self.engine.memory:g}")
        else:
            self.mem_label.configure(text="")

    # ------------------------------------------------------------------
    # Command Callbacks
    # ------------------------------------------------------------------
    def _digit(self, d: str):
        return lambda: self._append(d)

    def _insert(self, ch: str):
        return lambda: self._append(ch)

    def _fn(self, name: str):
        def _action():
            self._append(f"{name}(")
        return _action

    def _insert_const(self, const: str):
        return lambda: self._append(const)

    def _insert_ans(self):
        self._append(f"{self.engine.last():g}")

    def _append(self, text: str) -> None:
        self.expression += text
        self._update_display()

    def _clear(self) -> None:
        self.expression = ""
        self._show_result("0")
        self.history_label.configure(text="")
        self._update_display()

    def _backspace(self) -> None:
        if self.expression:
            self.expression = self.expression[:-1]
            self._update_display()
        if not self.expression:
            self._show_result("0")

    def _negate(self) -> None:
        if not self.expression:
            return
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression
        self._update_display()

    def _pow2(self) -> None:
        self.expression += "**2"
        self._update_display()

    def _factorial(self) -> None:
        self.expression += "factorial("
        self._update_display()

    def _perm(self) -> None:
        self.expression += "perm("
        self._update_display()

    def _comb(self) -> None:
        self.expression += "comb("
        self._update_display()

    def _evaluate(self) -> None:
        if not self.expression:
            return
        try:
            result = self.engine.evaluate(self.expression)
            formatted = self._format_number(result)
            self.history_label.configure(text=self.expression + " =")
            self.engine.history.append(f"{self.expression} = {formatted}")
            self.expression = str(formatted)
            self._show_result(formatted)
            self._update_display()
        except ZeroDivisionError:
            self._show_error("Error: division by zero")
        except ValueError as exc:
            self._show_error(f"Error: {exc}")
        except TypeError as exc:
            self._show_error(f"Error: {exc}")
        except Exception as exc:
            self._show_error(f"Error: {exc}")

    @staticmethod
    def _format_number(value: float | complex | int) -> str:
        if isinstance(value, complex):
            return str(value)
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        if abs(value) > 1e15 or (abs(value) < 1e-10 and value != 0):
            return f"{value:.10e}"
        return f"{value:.12g}"

    def _on_angle_change(self) -> None:
        self.engine.angle_mode = self.angle_var.get()

    def _mem_clear(self) -> None:
        self.engine.mem_clear()
        self._update_mem_indicator()

    def _mem_recall_btn(self) -> None:
        val = self.engine.mem_recall()
        self._append(f"{val:g}")

    def _mem_add_btn(self) -> None:
        try:
            val = float(self.result_label.cget("text"))
            self.engine.mem_add(val)
            self._update_mem_indicator()
        except ValueError:
            pass

    def _mem_sub_btn(self) -> None:
        try:
            val = float(self.result_label.cget("text"))
            self.engine.mem_sub(val)
            self._update_mem_indicator()
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Keyboard Navigation
    # ------------------------------------------------------------------
    def _bind_keyboard(self) -> None:
        self.bind("<Key>", self._on_key)
        self.bind("<Return>", lambda e: self._evaluate())
        self.bind("<BackSpace>", lambda e: self._backspace())
        self.bind("<Escape>", lambda e: self._clear())
        self.bind("<Delete>", lambda e: self._clear())

    def _on_key(self, event: tk.Event) -> None:
        # Don't capture keys if an Entry widget in another tab has focus
        focused = self.focus_get()
        if isinstance(focused, (tk.Entry, tk.Text)):
            return

        char = event.char
        key_map = {
            "0": self._digit("0"),
            "1": self._digit("1"),
            "2": self._digit("2"),
            "3": self._digit("3"),
            "4": self._digit("4"),
            "5": self._digit("5"),
            "6": self._digit("6"),
            "7": self._digit("7"),
            "8": self._digit("8"),
            "9": self._digit("9"),
            ".": self._insert("."),
            "+": self._insert("+"),
            "-": self._insert("-"),
            "*": self._insert("*"),
            "/": self._insert("/"),
            "(": self._insert("("),
            ")": self._insert(")"),
            "^": self._insert("^"),
            "%": self._insert("%"),
        }
        if char in key_map:
            key_map[char]()


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    calc = ScientificCalculator()
    calc.update_idletasks()
    w = calc.winfo_width()
    h = calc.winfo_height()
    sw = calc.winfo_screenwidth()
    sh = calc.winfo_screenheight()
    x = max(0, (sw - w) // 2)
    y = max(0, (sh - h) // 2)
    calc.geometry(f"+{x}+{y}")
    calc.mainloop()


if __name__ == "__main__":
    main()
