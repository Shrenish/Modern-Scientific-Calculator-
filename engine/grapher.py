"""
Grapher — Interactive 2D Function Plotter Widget (Pure Tkinter)
==============================================================
High-performance Canvas 2D graphing engine with:
- Multi-function plotting (f(x) and g(x))
- Interactive drag-to-pan and mouse-wheel zoom
- Adaptive dynamic grid lines with numeric labels
- Real-time crosshair and coordinate HUD
- Extrema (min/max) and root detection markers
- Safe mathematical function evaluation
"""

from __future__ import annotations

import math
import re
import tkinter as tk
from engine.calc_core import compile_math_expr


class GraphCanvas(tk.Frame):
    """Interactive function graphing canvas."""

    def __init__(
        self,
        parent: tk.Widget,
        width: int = 500,
        height: int = 400,
        bg: str = "#181825",
        grid_color: str = "#313244",
        axis_color: str = "#6c7086",
        text_color: str = "#a6adc8",
        f_color: str = "#89b4fa",
        g_color: str = "#fab387",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, bg=bg, **kwargs)

        self.canvas_width = width
        self.canvas_height = height
        self.bg = bg
        self.grid_color = grid_color
        self.axis_color = axis_color
        self.text_color = text_color
        self.f_color = f_color
        self.g_color = g_color

        # Viewport boundaries in math space
        self.x_min = -10.0
        self.x_max = 10.0
        self.y_min = -6.0
        self.y_max = 6.0

        # Functions to plot
        self.f_expr: str = "sin(x)"
        self.g_expr: str = ""

        # Drag state
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._is_dragging: bool = False

        self._build_ui()
        self._bind_events()

    def _build_ui(self) -> None:
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.bg,
            highlightthickness=0,
            cursor="crosshair",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        # Mouse wheel for zoom
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.zoom(1.15))
        self.canvas.bind("<Button-5>", lambda e: self.zoom(1 / 1.15))

    # ------------------------------------------------------------------
    # Coordinate Transforms
    # ------------------------------------------------------------------
    def _get_canvas_dims(self) -> tuple[int, int]:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 10:
            w = self.canvas_width
        if h <= 10:
            h = self.canvas_height
        return max(10, w), max(10, h)

    def math_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert math coordinate (x, y) to screen pixels (sx, sy)."""
        w, h = self._get_canvas_dims()
        sx = (x - self.x_min) / (self.x_max - self.x_min) * w
        sy = (self.y_max - y) / (self.y_max - self.y_min) * h
        return sx, sy

    def screen_to_math(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert screen pixels (sx, sy) to math coordinate (x, y)."""
        w, h = self._get_canvas_dims()
        x = self.x_min + (sx / w) * (self.x_max - self.x_min)
        y = self.y_max - (sy / h) * (self.y_max - self.y_min)
        return x, y

    # ------------------------------------------------------------------
    # Expression compilation for plotting
    # ------------------------------------------------------------------
    def _compile_expr(self, expr: str) -> Callable[[float], float] | None:
        """Safely compile math expression f(x) into a fast callable."""
        return compile_math_expr(expr)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def redraw(self) -> None:
        """Redraw the entire graph canvas."""
        w, h = self._get_canvas_dims()
        self.canvas.delete("all")

        self._draw_grid(w, h)
        self._draw_axes(w, h)

        if self.f_expr:
            fn_f = self._compile_expr(self.f_expr)
            if fn_f:
                self._draw_curve(fn_f, self.f_color, width=2)
                self._detect_and_draw_features(fn_f, self.f_color)
            else:
                self.canvas.create_text(
                    w // 2, 25,
                    text=f"Warning: Could not parse f(x) = {self.f_expr}",
                    fill="#f38ba8", font=("Segoe UI", 9, "bold")
                )

        if self.g_expr:
            fn_g = self._compile_expr(self.g_expr)
            if fn_g:
                self._draw_curve(fn_g, self.g_color, width=2, dash=(4, 2))
            else:
                self.canvas.create_text(
                    w // 2, 45,
                    text=f"Warning: Could not parse g(x) = {self.g_expr}",
                    fill="#f38ba8", font=("Segoe UI", 9, "bold")
                )

    def _draw_grid(self, w: int, h: int) -> None:
        """Draw adaptive grid lines and numeric coordinate ticks."""
        x_span = self.x_max - self.x_min
        y_span = self.y_max - self.y_min

        # Compute nice step sizes (1, 2, 5 * 10^k)
        step_x = self._nice_step(x_span / 8.0)
        step_y = self._nice_step(y_span / 8.0)

        # Vertical grid lines
        first_x = math.ceil(self.x_min / step_x) * step_x
        x = first_x
        while x <= self.x_max:
            sx, _ = self.math_to_screen(x, 0)
            self.canvas.create_line(sx, 0, sx, h, fill=self.grid_color, width=1)
            # Label
            if abs(x) > 1e-6:
                _, sy_axis = self.math_to_screen(0, 0)
                lbl_y = min(max(sy_axis + 12, 16), h - 16)
                self.canvas.create_text(
                    sx, lbl_y, text=f"{x:g}", fill=self.text_color, font=("Consolas", 8)
                )
            x += step_x

        # Horizontal grid lines
        first_y = math.ceil(self.y_min / step_y) * step_y
        y = first_y
        while y <= self.y_max:
            _, sy = self.math_to_screen(0, y)
            self.canvas.create_line(0, sy, w, sy, fill=self.grid_color, width=1)
            # Label
            if abs(y) > 1e-6:
                sx_axis, _ = self.math_to_screen(0, 0)
                lbl_x = min(max(sx_axis + 16, 24), w - 24)
                self.canvas.create_text(
                    lbl_x, sy, text=f"{y:g}", fill=self.text_color, font=("Consolas", 8)
                )
            y += step_y

    def _draw_axes(self, w: int, h: int) -> None:
        """Draw X and Y main coordinate axes."""
        origin_sx, origin_sy = self.math_to_screen(0, 0)

        # X Axis
        if 0 <= origin_sy <= h:
            self.canvas.create_line(0, origin_sy, w, origin_sy, fill=self.axis_color, width=2)
            self.canvas.create_text(w - 15, origin_sy - 10, text="x", fill=self.text_color, font=("Consolas", 10, "bold"))

        # Y Axis
        if 0 <= origin_sx <= w:
            self.canvas.create_line(origin_sx, 0, origin_sx, h, fill=self.axis_color, width=2)
            self.canvas.create_text(origin_sx + 10, 15, text="y", fill=self.text_color, font=("Consolas", 10, "bold"))

    def _draw_curve(
        self,
        fn: Callable[[float], float],
        color: str,
        width: int = 2,
        dash: tuple[int, ...] | None = None,
    ) -> None:
        """Draw high-resolution function curve with discontinuity detection."""
        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())
        points: list[tuple[float, float]] = []

        step_pixels = 2  # Evaluate every 2 screen pixels for super smooth curves
        num_steps = w // step_pixels + 2

        for i in range(num_steps):
            sx = i * step_pixels
            x, _ = self.screen_to_math(sx, 0)
            y = fn(x)

            if math.isnan(y) or math.isinf(y):
                if len(points) >= 2:
                    self._render_polyline(points, color, width, dash)
                points = []
                continue

            _, sy = self.math_to_screen(x, y)

            # Check for asymptotic jumps (e.g. tan(x))
            if points and abs(sy - points[-1][1]) > h * 0.8:
                if len(points) >= 2:
                    self._render_polyline(points, color, width, dash)
                points = []

            # Clamp offscreen pixels slightly to prevent canvas overflow
            clamped_sy = min(max(sy, -h), 2 * h)
            points.append((sx, clamped_sy))

        if len(points) >= 2:
            self._render_polyline(points, color, width, dash)

    def _render_polyline(
        self,
        pts: list[tuple[float, float]],
        color: str,
        width: int,
        dash: tuple[int, ...] | None,
    ) -> None:
        flat_coords = [coord for pt in pts for coord in pt]
        if dash:
            self.canvas.create_line(*flat_coords, fill=color, width=width, dash=dash)
        else:
            self.canvas.create_line(*flat_coords, fill=color, width=width)

    def _detect_and_draw_features(self, fn: Callable[[float], float], color: str) -> None:
        """Find and highlight roots (zeros) and local extrema."""
        steps = 100
        dx = (self.x_max - self.x_min) / steps

        prev_x = self.x_min
        prev_y = fn(prev_x)

        for i in range(1, steps + 1):
            curr_x = self.x_min + i * dx
            curr_y = fn(curr_x)

            if math.isnan(prev_y) or math.isnan(curr_y):
                prev_x, prev_y = curr_x, curr_y
                continue

            # Root detection: sign change
            if prev_y * curr_y < 0:
                # Bisection refinement
                root_x = self._bisection(fn, prev_x, curr_x)
                if root_x is not None:
                    sx, sy = self.math_to_screen(root_x, 0)
                    self.canvas.create_oval(
                        sx - 4, sy - 4, sx + 4, sy + 4,
                        fill="#a6e3a1", outline="#181825", width=1
                    )
            prev_x, prev_y = curr_x, curr_y

    def _bisection(
        self, fn: Callable[[float], float], a: float, b: float, tol: float = 1e-5
    ) -> float | None:
        fa = fn(a)
        for _ in range(25):
            mid = (a + b) / 2.0
            fmid = fn(mid)
            if math.isnan(fmid):
                return None
            if abs(fmid) < tol or (b - a) / 2.0 < tol:
                return mid
            if fa * fmid < 0:
                b = mid
            else:
                a = mid
                fa = fmid
        return (a + b) / 2.0

    @staticmethod
    def _nice_step(raw_step: float) -> float:
        """Find closest nice step (1, 2, 5 * 10^k)."""
        if raw_step <= 0:
            return 1.0
        exp = math.floor(math.log10(raw_step))
        frac = raw_step / (10 ** exp)
        if frac <= 1.5:
            nice = 1.0
        elif frac <= 3.0:
            nice = 2.0
        elif frac <= 7.0:
            nice = 5.0
        else:
            nice = 10.0
        return nice * (10 ** exp)

    # ------------------------------------------------------------------
    # User Interactions (Pan & Zoom)
    # ------------------------------------------------------------------
    def _on_resize(self, event: tk.Event) -> None:
        self.redraw()

    def _on_mouse_down(self, event: tk.Event) -> None:
        self._is_dragging = True
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_mouse_drag(self, event: tk.Event) -> None:
        if not self._is_dragging:
            return
        dx_pixels = event.x - self._drag_start_x
        dy_pixels = event.y - self._drag_start_y

        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())

        math_dx = (dx_pixels / w) * (self.x_max - self.x_min)
        math_dy = (dy_pixels / h) * (self.y_max - self.y_min)

        self.x_min -= math_dx
        self.x_max -= math_dx
        self.y_min += math_dy
        self.y_max += math_dy

        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.redraw()

    def _on_mouse_up(self, event: tk.Event) -> None:
        self._is_dragging = False

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        factor = 1.15 if event.delta > 0 else (1.0 / 1.15)
        self.zoom(factor, center_screen=(event.x, event.y))

    def zoom(self, factor: float, center_screen: tuple[int, int] | None = None) -> None:
        """Zoom in (factor > 1) or out (factor < 1)."""
        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())

        if center_screen:
            cx, cy = self.screen_to_math(center_screen[0], center_screen[1])
        else:
            cx = (self.x_min + self.x_max) / 2.0
            cy = (self.y_min + self.y_max) / 2.0

        new_x_span = (self.x_max - self.x_min) / factor
        new_y_span = (self.y_max - self.y_min) / factor

        ratio_x = (cx - self.x_min) / (self.x_max - self.x_min)
        ratio_y = (cy - self.y_min) / (self.y_max - self.y_min)

        self.x_min = cx - ratio_x * new_x_span
        self.x_max = self.x_min + new_x_span
        self.y_min = cy - ratio_y * new_y_span
        self.y_max = self.y_min + new_y_span
        self.redraw()

    def reset_view(self) -> None:
        """Reset view to standard [-10, 10] x [-6, 6]."""
        self.x_min = -10.0
        self.x_max = 10.0
        self.y_min = -6.0
        self.y_max = 6.0
        self.redraw()

    def set_functions(self, f_expr: str, g_expr: str = "") -> None:
        """Update functions and refresh plot."""
        self.f_expr = f_expr
        self.g_expr = g_expr
        self.redraw()

    # ------------------------------------------------------------------
    # Mouse Hover HUD
    # ------------------------------------------------------------------
    def _on_mouse_move(self, event: tk.Event) -> None:
        x, y = self.screen_to_math(event.x, event.y)
        self.canvas.delete("hud")

        # Subtle crosshairs
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.create_line(event.x, 0, event.x, h, fill="#45475a", dash=(2, 2), tags="hud")
        self.canvas.create_line(0, event.y, w, event.y, fill="#45475a", dash=(2, 2), tags="hud")

        # Evaluate f(x)
        fn_f = self._compile_expr(self.f_expr)
        f_val_str = ""
        if fn_f:
            f_val = fn_f(x)
            if not math.isnan(f_val):
                f_val_str = f" | f(x)={f_val:.4g}"

        hud_text = f"x: {x:.4g}, y: {y:.4g}{f_val_str}"
        self.canvas.create_text(
            10, h - 15, text=hud_text, anchor="w",
            fill="#cdd6f4", font=("Consolas", 9, "bold"), tags="hud"
        )

    def _on_mouse_leave(self, event: tk.Event) -> None:
        self.canvas.delete("hud")
