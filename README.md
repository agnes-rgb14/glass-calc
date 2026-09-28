# 🧮 glass-calc — Beatles-Themed Glassmorphism Calculator

A desktop calculator built with **Python + CustomTkinter**, featuring a frosted-glass look,
four Beatles album-inspired themes, a slide-out history drawer, and a safe math evaluator.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f6aa5)
![Platform](https://img.shields.io/badge/platform-Linux%20%C2%B7%20Windows%20%C2%B7%20macOS-lightgrey)

---

## ✨ Features

- **Glassmorphism UI** — translucent window (`-alpha`), rounded keys, album-colored accent stripes
- **4 album themes** — cycle with the ◐ button:
  | Theme | Vibe |
  |---|---|
  | 🟢 Abbey Road | Zebra-crossing stripes, muted green |
  | 🟡 Yellow Submarine | Psychedelic blue / yellow / orange / pink |
  | 🔴 Sgt. Pepper | Deep maroon, gold, regimental colors |
  | ⚪ White Album | Minimal light mode |
- **Scientific mode (SCI)** — `sin` `cos` `tan` `√` `π` `^` `(` `)`, plus `ln` / `log` via keyboard
- **DEG / RAD toggle** — trigonometry in degrees or radians
- **History drawer** — slide-out panel (last 50 entries); click any entry to recall its result; Clear button
- **Smart input**
  - Implicit multiplication: `2(3+4)` → `14`, `2π` → `6.28…`, `2sin(30)` → `1`
  - Auto-closed parentheses: `√(9` just works
  - Percent shorthand: `50%` → `0.5`
  - Continue calculations with an operator right after `=`
- **Easter eggs** — results like `4`, `8`, `9`, `64` show a song title ♪
- **Safe evaluation** — expressions are parsed with Python's `ast` module (no `eval()`), so only whitelisted arithmetic, functions and constants can execute

## 🖥️ Screenshots

&gt; Add screenshots here (one per theme looks great):

```text
docs/screenshots/abbey-road.png
docs/screenshots/yellow-submarine.png
docs/screenshots/sgt-pepper.png
docs/screenshots/white-album.png
```

## 🚀 Getting Started

### Requirements

- Python **3.10+**
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 5.x

### Install & run

```bash
git clone https://github.com/&lt;you&gt;/glass-calc.git
cd glass-calc

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install customtkinter
python glass_calc.py
```

&gt; ⚠️ Make sure `customtkinter` is installed **inside** the same venv you run the app with.

## 🎮 Usage

### On-screen controls

| Control | Action |
|---|---|
| `History` | Slide the history drawer in / out |
| `DEG` / `RAD` | Toggle angle unit for trig functions |
| `SCI` | Show / hide scientific keys |
| `◐` | Cycle to the next album theme |
| `AC` `⌫` `%` `±` | All-clear, backspace, percent, negate |
| `=` | Evaluate (also continues into chained ops) |

### Keyboard shortcuts

| Keys | Action |
|---|---|
| `0–9` `.` `+` `-` `*` `/` `%` `^` `(` `)` | Type digits & operators |
| `Enter` / `=` / `KP_Enter` | Evaluate |
| `Backspace` | Delete last token (whole `sin(` etc. at once) |
| `Esc` | All-clear |
| `s` `c` `t` | `sin(` `cos(` `tan(` |
| `r` `p` `e` | `√(` `π` `e` |

### Example expressions

```text
2(3+4)          → 14
50% + 2         → 2.5
2^10            → 1024
sin(30)         → 0.5        (DEG mode)
2sin(45)        → 1.4142135624
√(9             → 3          (auto-closed)
5 ÷ 0           → Can't ÷ 0
```

## 🗂️ Project structure

```text
glass-calc/
├── glass_calc.py      # The whole app (single file, ~450 lines)
├── README.md
├── .gitignore         # venv / __pycache__
└── docs/
    └── screenshots/   # theme screenshots
```

## 🔧 How it works

- **Themes** — a `THEMES` dict of color palettes (`fg/hover/text` per key kind, plus the stripe colors). `apply_theme()` re-colors every registered button in one pass.
- **Safe evaluator** — `preprocess()` normalizes display glyphs (`÷×−√π^`, `%`, implicit `*`, auto-close parens), then `safe_eval()` walks the `ast` tree and only allows `+ - * / % **`, negation, six functions and `π`/`e`. Anything else raises → the UI shows `Error`. Complex results and absurd exponents (`|b| &gt; 1000`) are rejected.
- **History** — capped at 50 entries, newest first; clicking an entry loads the result and closes the drawer.
- **History drawer** — a `place()`-managed frame animated with a simple easing loop (`after(12, …)`); `width` is set in the widget constructor (CustomTkinter requires that — passing `width=` to `.place()` raises).

## 🤝 Contributing

Issues and PRs welcome — especially new album themes! To add one, just drop another entry into `THEMES` (copy an existing palette and swap the hex values), and optionally add an `EGGS` entry for a fun result.

## 📄 License

MIT — see [LICENSE](LICENSE).
