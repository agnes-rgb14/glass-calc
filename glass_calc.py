"""Beatles-themed glass calculator: Python + CustomTkinter.

Setup:
    python -m venv venv && source venv/bin/activate
    pip install customtkinter

Run:
    python glass_calc_beatles.py

Header buttons: History (slide-out drawer) | DEG/RAD | SCI (scientific keys) | ◐ (next album theme)
Keyboard: digits, + - * / % ^ ( ), Enter/=, Backspace, Esc
          s=sin  c=cos  t=tan  r=√  p=π  e=e
"""
import ast
import math
import operator as op
import re
import tkinter as tk

import customtkinter as ctk

# ---------------------------------------------------------------- themes ----
# Each theme is loosely inspired by an album's colours. Add your own!
THEMES = {
    "Abbey Road": dict(
        tag="ABBEY ROAD · 1969", mode="dark", alpha=0.88,
        bg="#14161c", panel="#0e1015", border="#3a3f4b",
        num="#2a2d36", num_h="#383c48", fn="#22252d", fn_h="#31343f",
        op="#3d4250", op_h="#50566a", on_op="#eeeeee",
        sci="#1d2b3a", sci_h="#2b4058",
        accent="#6fae5b", accent_h="#85c46f", on_accent="#0e1015",
        text="#ececec", dim="#8d919c", stripes=["#eeeeee", "#14161c"],
    ),
    "Yellow Submarine": dict(
        tag="YELLOW SUBMARINE · 1969", mode="dark", alpha=0.88,
        bg="#16345f", panel="#102a4d", border="#3f6db3",
        num="#234a82", num_h="#2f5ea0", fn="#c2478a", fn_h="#d65c9f",
        op="#e8792b", op_h="#f28f45", on_op="#ffffff",
        sci="#1f7a8c", sci_h="#2a95a9",
        accent="#ffd21f", accent_h="#ffe066", on_accent="#1a1a1a",
        text="#fff8e1", dim="#a9c1e8",
        stripes=["#ffd21f", "#e8792b", "#c2478a", "#1f7a8c"],
    ),
    "Sgt. Pepper": dict(
        tag="SGT. PEPPER · 1967", mode="dark", alpha=0.88,
        bg="#2a0f1a", panel="#1f0a13", border="#6b2a3f",
        num="#4a1a2c", num_h="#5f2539", fn="#5a2d6e", fn_h="#6f3a86",
        op="#c9a227", op_h="#dcb73f", on_op="#2a0f1a",
        sci="#1e5a4a", sci_h="#2a7561",
        accent="#d63a3a", accent_h="#ea5555", on_accent="#ffffff",
        text="#f5e6c8", dim="#b89a7a",
        stripes=["#c9a227", "#d63a3a", "#5a2d6e", "#1e5a4a"],
    ),
    "White Album": dict(
        tag="THE BEATLES · 1968", mode="light", alpha=0.93,
        bg="#f2f2ee", panel="#e8e8e2", border="#c9c9c0",
        num="#ffffff", num_h="#e6e6e0", fn="#e9e9e3", fn_h="#d9d9d1",
        op="#dcdcd4", op_h="#cbcbc2", on_op="#1c1c1c",
        sci="#e3e3dc", sci_h="#d2d2ca",
        accent="#1a1a1a", accent_h="#3a3a3a", on_accent="#ffffff",
        text="#1c1c1c", dim="#777770", stripes=["#1a1a1a", "#f2f2ee"],
    ),
}
THEME_ORDER = list(THEMES)

# Small Easter eggs: show a song title when the result matches
EGGS = {"4": "The Fab Four", "8": "Eight Days a Week",
        "9": "Revolution 9", "64": "When I'm Sixty-Four"}

# ---------------------------------------------------- safe math evaluator ----
STATE = {"deg": True}  # degrees vs radians for trig


def _ang(x):
    return math.radians(x) if STATE["deg"] else x


FUNCS = {
    "sin": lambda x: math.sin(_ang(x)),
    "cos": lambda x: math.cos(_ang(x)),
    "tan": lambda x: math.tan(_ang(x)),
    "sqrt": math.sqrt,
    "ln": math.log,
    "log": math.log10,
}
CONSTS = {"pi": math.pi, "e": math.e}
_BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Mod: op.mod, ast.Pow: op.pow}
_UN = {ast.USub: op.neg, ast.UAdd: op.pos}


def preprocess(expr: str) -> str:
    """Turn the display string into a Python expression."""
    s = (expr.replace("÷", "/").replace("×", "*").replace("−", "-")
             .replace("^", "**").replace("√", "sqrt").replace("π", "pi"))
    s = re.sub(r"(\d+(?:\.\d+)?)%(?![\d(])", r"(\1/100)", s)   # 50%  -> 0.5
    s += ")" * (s.count("(") - s.count(")"))                    # auto-close
    s = re.sub(r"(?<=[\d)])(?=(?!e[+-]?\d)[a-z(])", "*", s)     # 2sin(30), 2(3), 2pi
    s = re.sub(r"(?<=\))(?=\d)", "*", s)                        # (2)3
    s = re.sub(r"(?<=pi)(?=[\d(a-z])", "*", s)                  # pi2, pi(2)
    return s


def safe_eval(expr: str):
    def walk(n):
        if isinstance(n, ast.Expression):
            return walk(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name) and n.id in CONSTS:
            return CONSTS[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 1000:
                raise ValueError("exponent too large")
            r = _BIN[type(n.op)](a, b)
            if isinstance(r, complex):
                raise ValueError("complex result")
            return r
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UN:
            return _UN[type(n.op)](walk(n.operand))
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id in FUNCS and len(n.args) == 1 and not n.keywords):
            return FUNCS[n.func.id](walk(n.args[0]))
        raise ValueError("unsupported expression")

    return walk(ast.parse(expr, mode="eval"))


def fmt(x) -> str:
    if abs(x) < 1e-12:          # sin(180) -> 0 instead of 1.2e-16
        x = 0
    if isinstance(x, float):
        s = str(int(x)) if x.is_integer() and abs(x) < 1e15 else f"{x:.10g}"
    else:
        s = str(x)
    return s.replace("-", "−")


# ---------------------------------------------------------------- the app ----
W, BASE_H, SCI_H, PANEL_W = 340, 540, 636, 264
INSERT = {"sin": "sin(", "cos": "cos(", "tan": "tan(", "√": "√("}
TOKENS = ("sin(", "cos(", "tan(", "√(", "ln(", "log(")
FN_KEYS, OP_KEYS = {"AC", "⌫", "%", "±"}, {"÷", "×", "−", "+"}
CONTINUE = {"÷", "×", "−", "+", "%", "^"}   # keys that continue after "="


class BeatlesCalc(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Calc")
        self.geometry(f"{W}x{BASE_H}")
        self.resizable(False, False)

        self.theme_i = 0
        self.t = THEMES[THEME_ORDER[0]]
        self.expr, self.just_evaluated = "", False
        self.sci_on, self.panel_open = False, False
        self.items = []             # history: (expression, result)
        self.buttons = []           # (widget, kind) for re-theming
        self._anim = None
        self.panel_x = W

        self.f_big = ctk.CTkFont(size=52, weight="bold")
        self.f_btn = ctk.CTkFont(size=22, weight="bold")
        self.f_sci = ctk.CTkFont(size=16, weight="bold")
        self.f_small = ctk.CTkFont(size=13)
        self.f_pill = ctk.CTkFont(size=12, weight="bold")

        self._build_header()
        self._build_display()
        self.stripe = tk.Canvas(self, height=8, highlightthickness=0, bd=0)
        self.stripe.pack(fill="x", padx=22, pady=(4, 8))
        self.stripe.bind("<Configure>", lambda e: self._draw_stripes())
        self._build_keypad()
        self._build_panel()
        self._bind_keys()
        self.apply_theme()

    # ---- construction ----
    def _pill(self, parent, text, cmd, width):
        b = ctk.CTkButton(parent, text=text, command=cmd, width=width, height=26,
                          corner_radius=13, font=self.f_pill, border_width=0)
        return b

    def _build_header(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=18, pady=(14, 0))
        self.p_hist = self._pill(bar, "History", self.toggle_panel, 64)
        self.p_hist.pack(side="left")
        self.p_theme = self._pill(bar, "◐", self.next_theme, 34)
        self.p_theme.pack(side="right")
        self.p_sci = self._pill(bar, "SCI", self.toggle_sci, 46)
        self.p_sci.pack(side="right", padx=6)
        self.p_deg = self._pill(bar, "DEG", self.toggle_deg, 46)
        self.p_deg.pack(side="right")
        self.pills = [self.p_hist, self.p_theme, self.p_sci, self.p_deg]

    def _build_display(self):
        d = ctk.CTkFrame(self, fg_color="transparent")
        d.pack(fill="x", padx=22, pady=(14, 0))
        top = ctk.CTkFrame(d, fg_color="transparent")
        top.pack(fill="x")
        self.tag = ctk.CTkLabel(top, text="", anchor="w", font=self.f_small)
        self.tag.pack(side="left")
        self.history_label = ctk.CTkLabel(top, text="", anchor="e", font=self.f_small)
        self.history_label.pack(side="right", fill="x", expand=True)
        self.result = ctk.CTkLabel(d, text="0", anchor="e", font=self.f_big)
        self.result.pack(fill="x", pady=(4, 0))

    def _key_btn(self, parent, label, kind, font, height=None):
        kw = {"height": height} if height else {}
        b = ctk.CTkButton(parent, text=label, corner_radius=18, font=font,
                          border_width=1, command=lambda l=label: self.press(l), **kw)
        self.buttons.append((b, kind))
        return b

    def _build_keypad(self):
        self.sci_frame = ctk.CTkFrame(self, fg_color="transparent")
        sci_rows = [["sin", "cos", "tan", "√"], ["(", ")", "π", "^"]]
        for c in range(4):
            self.sci_frame.grid_columnconfigure(c, weight=1, uniform="s")
        for r, row in enumerate(sci_rows):
            for c, label in enumerate(row):
                self._key_btn(self.sci_frame, label, "sci", self.f_sci, 38).grid(
                    row=r, column=c, padx=5, pady=4, sticky="nsew")

        self.pad = ctk.CTkFrame(self, fg_color="transparent")
        self.pad.pack(fill="both", expand=True, padx=14, pady=(0, 16))
        for i in range(4):
            self.pad.grid_columnconfigure(i, weight=1, uniform="c")
        for i in range(5):
            self.pad.grid_rowconfigure(i, weight=1, uniform="r")
        layout = [["AC", "⌫", "%", "÷"], ["7", "8", "9", "×"], ["4", "5", "6", "−"],
                  ["1", "2", "3", "+"], ["±", "0", ".", "="]]
        for r, row in enumerate(layout):
            for c, label in enumerate(row):
                kind = ("eq" if label == "=" else "op" if label in OP_KEYS
                        else "fn" if label in FN_KEYS else "num")
                self._key_btn(self.pad, label, kind, self.f_btn).grid(
                    row=r, column=c, padx=5, pady=5, sticky="nsew")

    def _build_panel(self):
        self.panel = ctk.CTkFrame(self, width=PANEL_W, height=BASE_H, corner_radius=18, border_width=1)
        head = ctk.CTkFrame(self.panel, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(14, 4))
        self.panel_title = ctk.CTkLabel(head, text="History",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.panel_title.pack(side="left")
        self.p_close = self._pill(head, "✕", self.toggle_panel, 30)
        self.p_close.pack(side="right")
        self.p_clear = self._pill(head, "Clear", self.clear_history, 50)
        self.p_clear.pack(side="right", padx=6)
        self.hist_list = ctk.CTkScrollableFrame(self.panel, fg_color="transparent")
        self.hist_list.pack(fill="both", expand=True, padx=6, pady=(0, 10))
        self.panel.place(x=W, y=0, relheight=1)

    # ---- theming ----
    def _colors(self, kind):
        t = self.t
        return {"num": (t["num"], t["num_h"], t["text"]),
                "op": (t["op"], t["op_h"], t["on_op"]),
                "fn": (t["fn"], t["fn_h"], t["text"]),
                "sci": (t["sci"], t["sci_h"], t["text"]),
                "eq": (t["accent"], t["accent_h"], t["on_accent"])}[kind]

    def apply_theme(self):
        t = self.t
        ctk.set_appearance_mode(t["mode"])
        self.configure(fg_color=t["bg"])
        self.attributes("-alpha", t["alpha"])
        for b, kind in self.buttons:
            fg, hv, tx = self._colors(kind)
            b.configure(fg_color=fg, hover_color=hv, text_color=tx,
                        border_color=t["border"])
        self.result.configure(text_color=t["text"])
        self.history_label.configure(text_color=t["dim"])
        self.tag.configure(text=t["tag"], text_color=t["dim"])
        self.stripe.configure(bg=t["bg"])
        self._draw_stripes()
        self.panel.configure(fg_color=t["panel"], border_color=t["border"])
        self.panel_title.configure(text_color=t["text"])
        for b in (self.p_close, self.p_clear):
            b.configure(fg_color=t["fn"], hover_color=t["fn_h"], text_color=t["text"])
        self._style_pills()
        self._rebuild_history()

    def _style_pills(self):
        t = self.t
        for p in self.pills:
            p.configure(fg_color=t["fn"], hover_color=t["fn_h"], text_color=t["text"])
        if self.sci_on:
            self.p_sci.configure(fg_color=t["accent"], hover_color=t["accent_h"],
                                 text_color=t["on_accent"])
        self.p_deg.configure(text="DEG" if STATE["deg"] else "RAD")

    def _draw_stripes(self):
        c = self.stripe
        c.delete("all")
        w = c.winfo_width() if c.winfo_width() > 1 else W - 44
        cols = self.t["stripes"]
        n = 18
        sw = w / n
        for i in range(n):
            c.create_rectangle(i * sw, 0, (i + 1) * sw - 3, 8,
                               fill=cols[i % len(cols)], outline="")

    def next_theme(self):
        self.theme_i = (self.theme_i + 1) % len(THEME_ORDER)
        self.t = THEMES[THEME_ORDER[self.theme_i]]
        self.apply_theme()

    # ---- toggles ----
    def toggle_sci(self):
        self.sci_on = not self.sci_on
        if self.sci_on:
            self.sci_frame.pack(fill="x", padx=14, before=self.pad)
            self.geometry(f"{W}x{SCI_H}")
        else:
            self.sci_frame.pack_forget()
            self.geometry(f"{W}x{BASE_H}")
        self._style_pills()

    def toggle_deg(self):
        STATE["deg"] = not STATE["deg"]
        self._style_pills()

    def toggle_panel(self):
        self.panel_open = not self.panel_open
        if self.panel_open:
            self._rebuild_history()
            self.panel.lift()
        self._slide(W - PANEL_W if self.panel_open else W)

    def _slide(self, target):
        if self._anim:
            self.after_cancel(self._anim)
        step = (target - self.panel_x) * 0.3
        if abs(target - self.panel_x) < 2:
            self.panel_x = target
            self.panel.place(x=int(self.panel_x), y=0, relheight=1)
            self._anim = None
            return
        self.panel_x += step
        self.panel.place(x=int(self.panel_x), y=0, relheight=1)
        self._anim = self.after(12, lambda: self._slide(target))

    # ---- history ----
    def _rebuild_history(self):
        for w in self.hist_list.winfo_children():
            w.destroy()
        t = self.t
        if not self.items:
            ctk.CTkLabel(self.hist_list, text="Nothing yet", text_color=t["dim"],
                         font=self.f_small).pack(pady=20)
            return
        for expr, res in self.items:
            ctk.CTkButton(
                self.hist_list, text=f"{expr}\n= {res}", anchor="e", height=50,
                corner_radius=12, fg_color="transparent", hover_color=t["num_h"],
                text_color=t["text"], font=self.f_small,
                command=lambda r=res: self._recall(r),
            ).pack(fill="x", pady=2)

    def _recall(self, res):
        self.expr, self.just_evaluated = res, True
        self._refresh()
        self.toggle_panel()

    def clear_history(self):
        self.items.clear()
        self._rebuild_history()

    # ---- calculator logic ----
    def press(self, key):
        self._reset_tag()
        if key == "AC":
            self.expr, self.just_evaluated = "", False
            self.history_label.configure(text="")
        elif key == "⌫":
            self._backspace()
        elif key == "=":
            self._evaluate()
            return
        elif key == "±":
            self._negate()
        else:
            if self.just_evaluated and key not in CONTINUE:
                self.expr = ""
            self.just_evaluated = False
            self.expr += INSERT.get(key, key)
        self._refresh()

    def _backspace(self):
        for tok in TOKENS:
            if self.expr.endswith(tok):
                self.expr = self.expr[:-len(tok)]
                return
        self.expr = self.expr[:-1]

    def _negate(self):
        i = len(self.expr)
        while i > 0 and (self.expr[i - 1].isdigit() or self.expr[i - 1] == "."):
            i -= 1
        if i > 0 and self.expr[i - 1] == "−" and (i == 1 or self.expr[i - 2] in "÷×−+(^"):
            self.expr = self.expr[:i - 1] + self.expr[i:]
        else:
            self.expr = self.expr[:i] + "−" + self.expr[i:]

    def _evaluate(self):
        if not self.expr:
            return
        src = self.expr
        try:
            value = safe_eval(preprocess(src))
        except ZeroDivisionError:
            return self._fail("Can't ÷ 0", src)
        except (ValueError, OverflowError, SyntaxError, TypeError):
            return self._fail("Error", src)
        res = fmt(value)
        self.history_label.configure(text=f"{src} =")
        self.expr, self.just_evaluated = res, True
        self.items.insert(0, (src, res))
        del self.items[50:]
        if self.panel_open:
            self._rebuild_history()
        self._refresh()
        if res in EGGS:
            self.tag.configure(text="♪ " + EGGS[res])

    def _fail(self, msg, src):
        self.history_label.configure(text=f"{src} =")
        self.expr = ""
        self.result.configure(text=msg, font=ctk.CTkFont(size=30, weight="bold"))

    def _reset_tag(self):
        self.tag.configure(text=self.t["tag"])

    def _refresh(self):
        text = self.expr or "0"
        size = 52 if len(text) <= 9 else 38 if len(text) <= 13 else 26
        self.result.configure(text=text, font=ctk.CTkFont(size=size, weight="bold"))

    def _bind_keys(self):
        for d in "0123456789.+%":
            self.bind(d, lambda e, k=d: self.press(k))
        self.bind("*", lambda e: self.press("×"))
        self.bind("/", lambda e: self.press("÷"))
        self.bind("-", lambda e: self.press("−"))
        self.bind("<parenleft>", lambda e: self.press("("))
        self.bind("<parenright>", lambda e: self.press(")"))
        self.bind("<asciicircum>", lambda e: self.press("^"))
        for k, v in {"s": "sin", "c": "cos", "t": "tan", "r": "√", "p": "π", "e": "e"}.items():
            self.bind(k, lambda e, v=v: self.press(v))
        for k in ("<Return>", "<KP_Enter>", "="):
            self.bind(k, lambda e: self.press("="))
        self.bind("<BackSpace>", lambda e: self.press("⌫"))
        self.bind("<Escape>", lambda e: self.press("AC"))


if __name__ == "__main__":
    BeatlesCalc().mainloop()

