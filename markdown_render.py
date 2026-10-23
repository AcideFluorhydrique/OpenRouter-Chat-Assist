# -*- coding: utf-8 -*-
"""
Markdown / LaTeX 渲染

把 AI 回复转换为 [(文本, 标签元组), ...] 片段列表，由 Tkinter Text 组件按标签显示。
本模块不依赖 Tk，便于单独测试。

特殊标签：
- "url:<地址>"        链接目标，界面据此打开浏览器
- "tbl:<x1>,<x2>,..." 表格制表位（像素），界面据此配置 tabs
"""

import re
import unicodedata

# ---------- LaTeX → Unicode ----------

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "ϑ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
    "pi": "π", "varpi": "ϖ", "rho": "ρ", "varrho": "ϱ", "sigma": "σ",
    "varsigma": "ς", "tau": "τ", "upsilon": "υ", "phi": "φ", "varphi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}

SYMBOLS = {
    "times": "×", "cdot": "·", "div": "÷", "pm": "±", "mp": "∓", "ast": "∗",
    "star": "⋆", "circ": "∘", "bullet": "•", "oplus": "⊕", "otimes": "⊗",
    "leq": "≤", "le": "≤", "geq": "≥", "ge": "≥", "neq": "≠", "ne": "≠",
    "lt": "<", "gt": ">", "ll": "≪", "gg": "≫", "approx": "≈", "equiv": "≡",
    "sim": "∼", "simeq": "≃", "cong": "≅", "propto": "∝",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "gets": "←",
    "leftrightarrow": "↔", "Rightarrow": "⇒", "implies": "⇒", "Leftarrow": "⇐",
    "Leftrightarrow": "⇔", "iff": "⇔", "mapsto": "↦", "longrightarrow": "⟶",
    "uparrow": "↑", "downarrow": "↓",
    "in": "∈", "notin": "∉", "ni": "∋", "subset": "⊂", "subseteq": "⊆",
    "supset": "⊃", "supseteq": "⊇", "cup": "∪", "cap": "∩", "setminus": "∖",
    "emptyset": "∅", "varnothing": "∅", "forall": "∀", "exists": "∃",
    "neg": "¬", "lnot": "¬", "land": "∧", "wedge": "∧", "lor": "∨", "vee": "∨",
    "infty": "∞", "partial": "∂", "nabla": "∇", "sum": "∑", "prod": "∏",
    "int": "∫", "iint": "∬", "iiint": "∭", "oint": "∮",
    "angle": "∠", "perp": "⊥", "parallel": "∥", "mid": "|", "vert": "|",
    "Vert": "‖", "langle": "⟨", "rangle": "⟩", "lfloor": "⌊", "rfloor": "⌋",
    "lceil": "⌈", "rceil": "⌉", "lbrace": "{", "rbrace": "}",
    "ldots": "…", "dots": "…", "cdots": "⋯", "vdots": "⋮", "ddots": "⋱",
    "prime": "′", "degree": "°", "hbar": "ℏ", "ell": "ℓ", "Re": "ℜ", "Im": "ℑ",
    "aleph": "ℵ", "therefore": "∴", "because": "∵", "top": "⊤", "bot": "⊥",
    "triangle": "△", "square": "□", "checkmark": "✓", "dagger": "†",
    "colon": ":", "quad": "  ", "qquad": "    ",
    "displaystyle": "", "textstyle": "", "limits": "", "nolimits": "",
}

# 这些符号两侧补空格
RELATIONS = set("=<>≤≥≠≈≡∼≃≅∝≪≫→←↔⇒⇐⇔↦⟶∈∉∋⊂⊆⊃⊇×÷±∓")
_PAD = "\x00"
# 多行块（矩阵、分段函数等）的标记：\x01 行\x03行 \x02
_BLOCK_START, _BLOCK_END, _ROW = "\x01", "\x02", "\x03"

BLACKBOARD = {"R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ", "C": "ℂ", "P": "ℙ", "E": "𝔼", "1": "𝟙"}

FRACTIONS = {"frac", "dfrac", "tfrac", "cfrac"}
FONT_COMMANDS = {
    "text", "textrm", "textit", "textbf", "textsf", "texttt", "mathrm", "mathit",
    "mathbf", "mathsf", "mathtt", "mathcal", "mathscr", "mathfrak", "boldsymbol",
    "bm", "operatorname", "mbox", "emph", "underbrace", "overbrace",
}
ACCENTS = {
    "vec": "⃗", "hat": "̂", "widehat": "̂", "bar": "̄",
    "overline": "̅", "tilde": "̃", "widetilde": "̃",
    "dot": "̇", "ddot": "̈", "underline": "̲",
}
DELIMITER_SIZES = {
    "left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr",
    "biggl", "biggr", "Biggl", "Biggr",
}
NEGATIONS = {"=": "≠", "<": "≮", ">": "≯", "∈": "∉", "⊂": "⊄", "≡": "≢", "≤": "≰", "≥": "≱"}

SUPERSCRIPT = dict(zip(
    "0123456789+-−=()abcdefghijklmnoprstuvwxyzABDEGHIJKLMNOPRTUVW",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻⁼⁽⁾ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂ",
))
SUPERSCRIPT.update({c: c for c in "′″‴*∗†"})
SUBSCRIPT = dict(zip(
    "0123456789+-−=()aehijklmnoprstuvxβγρφχ",
    "₀₁₂₃₄₅₆₇₈₉₊₋₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓᵦᵧᵨᵩᵪ",
))
SUBSCRIPT[","] = ","

MATRIX_DELIMITERS = {
    "matrix": ("", ""), "smallmatrix": ("", ""), "array": ("", ""),
    "pmatrix": ("(", ")"), "bmatrix": ("[", "]"), "Bmatrix": ("{", "}"),
    "vmatrix": ("|", "|"), "Vmatrix": ("‖", "‖"),
}
# 多行括号：(上, 中, 下)
TALL_DELIMITERS = {
    "(": ("⎛", "⎜", "⎝"), ")": ("⎞", "⎟", "⎠"),
    "[": ("⎡", "⎢", "⎣"), "]": ("⎤", "⎥", "⎦"),
    "{": ("⎧", "⎨", "⎩"), "}": ("⎫", "⎬", "⎭"),
    "|": ("│", "│", "│"), "‖": ("‖", "‖", "‖"),
}


def _script(text, mark):
    """上下标：能用 Unicode 上/下标字符就转换，否则写成 ^(…) / _(…)"""
    text = text.strip()
    if not text:
        return ""
    if mark == "^" and text == "∘":
        return "°"
    table = SUPERSCRIPT if mark == "^" else SUBSCRIPT
    if all(ch in table for ch in text):
        return "".join(table[ch] for ch in text)
    return mark + (text if len(text) == 1 else f"({text})")


def _wrap(text):
    """分式的分子/分母需要时加括号"""
    text = text.strip()
    if re.fullmatch(r"[\w.′]+", text) or (text.startswith("(") and text.endswith(")")):
        return text
    return f"({text})"


def _tall(delim, rows):
    """为多行内容生成竖向括号"""
    if not delim:
        return [""] * rows
    if rows == 1:
        return [delim]
    top, mid, bottom = TALL_DELIMITERS.get(delim, (delim, delim, delim))
    return [top] + [mid] * (rows - 2) + [bottom]


def _width(text):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else
               0 if unicodedata.combining(c) else 1 for c in text)


class _LatexParser:
    def __init__(self, src):
        self.s = src
        self.i = 0

    def parse(self, stop=None):
        out = []
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "}":
                self.i += 1
                if stop == "}":
                    break
            elif c == "{":
                self.i += 1
                out.append(self.parse("}"))
            elif c == "\\":
                out.append(self.command())
            elif c in "^_":
                self.i += 1
                out.append(_script(self.arg(), c))
            elif c == "~":
                self.i += 1
                out.append(" ")
            elif c == "&":
                self.i += 1
            else:
                self.i += 1
                out.append(c)
        return "".join(out)

    def skip_spaces(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def arg(self):
        """读取一个参数：{…}、\\命令 或单个字符"""
        self.skip_spaces()
        if self.i >= len(self.s):
            return ""
        c = self.s[self.i]
        if c == "{":
            self.i += 1
            return self.parse("}")
        if c == "\\":
            return self.command()
        self.i += 1
        return c

    def optional_arg(self):
        self.skip_spaces()
        if self.i < len(self.s) and self.s[self.i] == "[":
            end = self.s.find("]", self.i)
            if end != -1:
                raw = self.s[self.i + 1:end]
                self.i = end + 1
                return _LatexParser(raw).parse()
        return None

    def raw_group(self):
        self.skip_spaces()
        if self.i < len(self.s) and self.s[self.i] == "{":
            end = self.s.find("}", self.i)
            if end != -1:
                raw = self.s[self.i + 1:end]
                self.i = end + 1
                return raw
        return ""

    def command(self):
        self.i += 1  # 跳过反斜杠
        if self.i >= len(self.s):
            return "\\"
        c = self.s[self.i]
        if not c.isalpha():
            self.i += 1
            return {"\\": "\n", ",": " ", ";": " ", ":": " ", ">": " ", "!": "",
                    " ": " ", "|": "‖"}.get(c, c)

        name = re.match(r"[A-Za-z]+", self.s[self.i:]).group()
        self.i += len(name)

        if name == "begin":
            return self.environment()
        if name == "end":
            self.raw_group()
            return ""
        if name in DELIMITER_SIZES:
            self.skip_spaces()
            if self.s.startswith(".", self.i):
                self.i += 1
                return ""
            return self.arg()
        if name in FRACTIONS:
            num, den = self.arg(), self.arg()
            return f"{_wrap(num)}/{_wrap(den)}"
        if name == "binom":
            n, k = self.arg(), self.arg()
            return f"C({n.strip()},{k.strip()})"
        if name == "sqrt":
            index = self.optional_arg()
            body = self.arg().strip()
            root = {None: "√", "2": "√", "3": "∛", "4": "∜"}.get(index)
            if root is None:
                root = _script(index, "^") + "√"
            return root + (body if re.fullmatch(r"[\w.]+", body) else f"({body})")
        if name in FONT_COMMANDS:
            return self.arg()
        if name == "mathbb":
            return "".join(BLACKBOARD.get(ch, ch) for ch in self.arg())
        if name in ACCENTS:
            mark = ACCENTS[name]
            body = self.arg()
            if name in ("overline", "underline", "bar") and len(body) > 1:
                return "".join(ch + mark for ch in body)
            return body + mark
        if name in ("overset", "underset", "stackrel"):
            self.arg()
            return self.arg()
        if name in ("boxed", "fbox"):
            return f"[{self.arg().strip()}]"
        if name == "not":
            nxt = self.arg().strip(_PAD + " ")
            return _PAD + NEGATIONS.get(nxt, nxt + "̸") + _PAD
        if name in SYMBOLS:
            sym = SYMBOLS[name]
            return _PAD + sym + _PAD if sym in RELATIONS else sym
        if name in GREEK:
            return GREEK[name]
        # \sin、\log、\lim 等函数名直接输出
        return name

    def environment(self):
        env = self.raw_group()
        begin, end = "\\begin{" + env + "}", "\\end{" + env + "}"
        # 找到配对的 \end{env}
        depth, j = 1, self.i
        while depth:
            next_end = self.s.find(end, j)
            if next_end == -1:
                next_end = len(self.s)
                break
            next_begin = self.s.find(begin, j)
            if next_begin != -1 and next_begin < next_end:
                depth += 1
                j = next_begin + len(begin)
            else:
                depth -= 1
                j = next_end + len(end)
        body = self.s[self.i:next_end]
        self.i = min(len(self.s), next_end + len(end))

        base = env.rstrip("*")
        if base in ("array", "tabular"):
            body = re.sub(r"^\s*\{[^}]*\}", "", body)
        body = body.replace("\\hline", "")
        rows = [r for r in re.split(r"\\\\(?:\[[^\]]*\])?", body) if r.strip()]
        cells = [[_flatten(_LatexParser(c).parse()).strip() for c in re.split(r"(?<!\\)&", r)]
                 for r in rows]
        if not cells:
            return ""

        # 按列对齐；矩阵列间距大一些，align 等环境的 & 只是对齐点
        is_matrix = base in MATRIX_DELIMITERS or base == "cases"
        columns = max(len(r) for r in cells)
        widths = [max((_width(r[k]) for r in cells if k < len(r)), default=0) for k in range(columns)]
        lines = [("  " if is_matrix else " ").join(c + " " * (widths[k] - _width(c))
                                                   for k, c in enumerate(r)).rstrip()
                 for r in cells]
        if is_matrix:
            left, right = ("{", "") if base == "cases" else MATRIX_DELIMITERS[base]
            width = max(_width(l) for l in lines)
            lefts, rights = _tall(left, len(lines)), _tall(right, len(lines))
            lines = [f"{lefts[k]} {l}{' ' * (width - _width(l))} {rights[k]}".rstrip()
                     for k, l in enumerate(lines)]
        return _BLOCK_START + _ROW.join(lines) + _BLOCK_END


def _flatten(text):
    """嵌套的多行块压成一行"""
    return text.replace(_ROW, "; ").replace(_BLOCK_START, "").replace(_BLOCK_END, "")


def _layout(text):
    """把多行块与前后文字横向拼接，各部分垂直居中"""
    pieces = re.split(_BLOCK_START + "(.*?)" + _BLOCK_END, text, flags=re.S)
    columns = []
    for k, piece in enumerate(pieces):
        if k % 2:
            columns.append(piece.split(_ROW))
        elif piece.strip():
            columns.append([piece.replace("\n", " ")])
    if not columns:
        return ""
    height = max(len(c) for c in columns)
    rows = [""] * height
    for column in columns:
        width = max(_width(r) for r in column)
        top = (height - len(column)) // 2
        for r in range(height):
            cell = column[r - top] if 0 <= r - top < len(column) else ""
            rows[r] += cell + " " * (width - _width(cell))
    return "\n".join(rows)


def latex_to_unicode(src):
    """把 LaTeX 公式转换为尽量可读的 Unicode 文本（矩阵等可能有多行）"""
    text = _LatexParser(src).parse()
    # 关系符两侧的空格只保留一个
    text = re.sub(r"[ \x00]*\x00[ \x00]*", " ", text)
    if _BLOCK_START in text:
        text = _layout(text)
    lines = [l.rstrip() for l in text.split("\n")]
    return "\n".join(l for l in lines if l.strip()).strip("\n")


# ---------- Markdown ----------

INLINE = re.compile(r"""
    (?P<code_ticks>`+)(?P<code>.+?)(?P=code_ticks)
  | \$\$(?P<dmath>.+?)\$\$
  | \\\((?P<pmath>.+?)\\\)
  | (?<![\\$\w])\$(?P<math>[^\s$](?:[^$]*?[^\s$\\])?)\$(?![\w$])
  | \*\*\*(?P<bold_italic>.+?)\*\*\*
  | \*\*(?P<bold>.+?)\*\*
  | (?<!\w)__(?P<bold2>.+?)__(?!\w)
  | (?<![\w*])\*(?P<italic>[^\s*](?:.*?[^\s*])?)\*(?![\w*])
  | (?<!\w)_(?P<italic2>[^\s_](?:.*?[^\s_])?)_(?!\w)
  | ~~(?P<strike>.+?)~~
  | \[(?P<link_text>[^\]]+)\]\((?P<url>[^)\s]+)\)
  | <br\s*/?>
""", re.X)

FENCE = re.compile(r"^\s*(```+|~~~+)")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
RULE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
QUOTE = re.compile(r"^\s{0,3}>\s?(.*)$")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
MATH_ENV = re.compile(r"^\s*\\begin\{(equation|align|gather|multline|eqnarray)\*?\}")


def render_inline(text, tags=()):
    """解析行内格式，返回片段列表"""
    segments = []
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            segments.append((text[pos:m.start()], tags))
        pos = m.end()
        g = m.groupdict()
        if g["code"] is not None:
            segments.append((g["code"], tags + ("code_inline",)))
        elif g["dmath"] or g["pmath"] or g["math"]:
            formula = latex_to_unicode(g["dmath"] or g["pmath"] or g["math"])
            segments.append((formula.replace("\n", "; "), tags + ("math",)))
        elif g["bold_italic"]:
            segments += render_inline(g["bold_italic"], tags + ("bold", "italic"))
        elif g["bold"] or g["bold2"]:
            segments += render_inline(g["bold"] or g["bold2"], tags + ("bold",))
        elif g["italic"] or g["italic2"]:
            segments += render_inline(g["italic"] or g["italic2"], tags + ("italic",))
        elif g["strike"]:
            segments += render_inline(g["strike"], tags + ("strike",))
        elif g["link_text"]:
            segments += render_inline(g["link_text"], tags + ("link", "url:" + g["url"]))
        else:  # <br>
            segments.append(("\n", tags))
    if pos < len(text):
        segments.append((text[pos:], tags))
    return segments


def _plain(text):
    return "".join(t for t, _ in render_inline(text))


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def _table(lines, measure):
    rows = [[_plain(c).replace("\n", " ") for c in _split_row(l)] for l in lines]
    header, body = rows[0], rows[2:]
    columns = max(len(r) for r in rows)
    gap = measure("    ")
    widths = [max((measure(r[k]) for r in [header] + body if k < len(r)), default=0)
              for k in range(columns)]
    stops, x = [], 0
    for w in widths[:-1]:
        x += w + gap
        stops.append(str(x))
    tab_tag = "tbl:" + ",".join(stops)

    segments = [("\t".join(header) + "\n", ("table", "table_header", tab_tag))]
    total = sum(widths) + gap * (columns - 1)
    segments.append(("─" * max(3, round(total / max(1, measure("─")))) + "\n", ("table", "hr")))
    for r in body:
        segments.append(("\t".join(r) + "\n", ("table", tab_tag)))
    return segments


def render_markdown(text, measure=None):
    """
    把 Markdown 文本转换为片段列表。
    measure(text) -> 像素宽度，用于表格对齐；不提供时按字符宽度估算。
    """
    if measure is None:
        measure = lambda s: _width(s) * 8
    lines = text.replace("\r\n", "\n").split("\n")
    segments = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 代码块
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(marker):
                code.append(lines[i])
                i += 1
            segments.append(("\n".join(code) + "\n", ("code_block",)))

        # 独立公式：$$…$$、\[…\]、\begin{equation} 等
        elif stripped.startswith(("$$", "\\[")) or MATH_ENV.match(line):
            env = MATH_ENV.match(line)
            if env:
                prefix = env.group(0).strip()
                close = prefix.replace("\\begin", "\\end")
                collected = [line[env.end():]]
            else:
                prefix = ""
                close = "$$" if stripped.startswith("$$") else "\\]"
                collected = [stripped[2:]]
            while close not in collected[-1] and i + 1 < len(lines):
                i += 1
                collected.append(lines[i])
            formula = "\n".join(collected)
            if close in formula:
                # 环境保留 \end{…} 交给解析器；$$ / \] 直接截掉
                formula = formula[:formula.find(close) + (len(close) if prefix else 0)]
            formula = latex_to_unicode(prefix + formula)
            # 多行公式（矩阵等）需要等宽字体才能对齐
            tag = "math_grid" if "\n" in formula else "math_block"
            segments.append((formula.strip() + "\n", (tag,)))

        elif HEADING.match(line):
            level, content = HEADING.match(line).groups()
            segments += render_inline(content, ("h" + str(min(len(level), 3)),))
            segments.append(("\n", ()))

        elif RULE.match(line):
            segments.append(("─" * 30 + "\n", ("hr",)))

        # 表格：表头行 + 分隔行
        elif "|" in line and i + 1 < len(lines) and TABLE_SEPARATOR.match(lines[i + 1]) \
                and "-" in lines[i + 1]:
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            segments += _table(table_lines, measure)
            continue

        elif QUOTE.match(line):
            segments += render_inline(QUOTE.match(line).group(1), ("quote",))
            segments.append(("\n", ("quote",)))

        elif LIST_ITEM.match(line):
            indent, marker, content = LIST_ITEM.match(line).groups()
            level = min(len(indent.replace("\t", "    ")) // 2, 3)
            if marker[0].isdigit():
                bullet = marker
            else:
                bullet = "•◦▪▫"[level]
            tag = f"list{level}"
            # 任务列表
            task = re.match(r"\[([ xX])\]\s+(.*)", content)
            if task:
                bullet = "☑" if task.group(1) != " " else "☐"
                content = task.group(2)
            segments.append((bullet + " ", (tag,)))
            segments += render_inline(content, (tag,))
            segments.append(("\n", (tag,)))

        else:
            segments += render_inline(line)
            segments.append(("\n", ()))

        i += 1

    return _merge_font_tags(segments)


def _merge_font_tags(segments):
    """Tk 的一个字符只能有一种字体，粗体+斜体需合并成单独的标签"""
    result = []
    for text, tags in segments:
        if "bold" in tags and "italic" in tags:
            tags = tuple(t for t in tags if t not in ("bold", "italic")) + ("bold_italic",)
        result.append((text, tags))
    return result
