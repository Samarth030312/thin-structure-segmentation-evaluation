#!/usr/bin/env python3
"""Convert the master monograph Markdown to LaTeX and compile with pdflatex.

luaotfload is broken in this TeX install, so we target pdflatex and substitute all
non-ASCII Unicode: math symbols -> math commands, box-drawing -> ASCII in verbatim.

    python scripts/build_monograph_pdf.py docs/UAV_Roadmark_Master_Monograph.md
"""
import os
import re
import subprocess
import sys

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{longtable,array}
\usepackage{xcolor}
\usepackage{fvextra}
\usepackage{mdframed}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\definecolor{codebg}{gray}{0.95}
\surroundwithmdframed[backgroundcolor=codebg,linewidth=0pt,innerleftmargin=5pt,
  innerrightmargin=5pt,innertopmargin=3pt,innerbottommargin=3pt]{Verbatim}
\titleformat{\section}{\Large\bfseries\sffamily}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\sffamily}{}{0pt}{}
\titlespacing*{\section}{0pt}{10pt}{6pt}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\sloppy \hbadness=10000 \vbadness=10000 \emergencystretch=3em
\title{\textbf{When mIoU Lies}\\[4pt]\large A Master Monograph on Thin-Structure
Segmentation, Evaluation Metrics, and the Width-Coupling Law}
\author{}\date{}
\begin{document}\maketitle\thispagestyle{empty}
"""
POST = r"\end{document}"

# multi-codepoint preprocess (combining marks) -> sentinels
PRE = [("δ̂", "DHAT"), ("̂", "")]

# Unicode -> bare math command (used inside math mode)
MATH = {
    "δ": r"\delta", "θ": r"\theta", "τ": r"\tau", "η": r"\eta", "β": r"\beta",
    "α": r"\alpha", "γ": r"\gamma", "Δ": r"\Delta", "Σ": r"\Sigma", "ℝ": r"\mathbb{R}",
    "→": r"\rightarrow", "←": r"\leftarrow", "≈": r"\approx", "×": r"\times",
    "−": "-", "·": r"\cdot", "±": r"\pm", "≥": r"\geq", "≤": r"\leq", "∞": r"\infty",
    "∂": r"\partial", "∩": r"\cap", "∪": r"\cup", "∈": r"\in", "⊂": r"\subset",
    "⊄": r"\not\subset", "∇": r"\nabla", "√": r"\surd", "≫": r"\gg", "≳": r"\gtrsim",
    "⌊": r"\lfloor", "⌋": r"\rfloor", "ℓ": r"\ell", "²": "^{2}", "ᵢ": "_{i}",
    "ⱼ": "_{j}", "ⁿ": "^{n}", "ᵀ": r"^{\top}", "ᵐ": "^{m}", "₁": "_{1}", "₂": "_{2}",
    "ŷ": r"\hat{y}", "…": r"\ldots", "✓": r"\checkmark", "§": r"\S", "ℝ": r"\mathbb{R}",
}
# Unicode -> text/prose replacement (wrap math symbols in $...$)
PROSE = {
    "—": "---", "–": "--", "…": r"\ldots{}", "§": r"\S{}", "·": r"$\cdot$",
    "×": r"$\times$", "−": r"$-$", "±": r"$\pm$", "≥": r"$\geq$", "≤": r"$\leq$",
    "≈": r"$\approx$", "→": r"$\rightarrow$", "←": r"$\leftarrow$", "∞": r"$\infty$",
    "²": r"\textsuperscript{2}", "✓": r"$\checkmark$", "≫": r"$\gg$", "≳": r"$\gtrsim$",
    "∂": r"$\partial$", "∩": r"$\cap$", "∪": r"$\cup$", "∈": r"$\in$", "⊂": r"$\subset$",
    "⊄": r"$\not\subset$", "∇": r"$\nabla$", "ℝ": r"$\mathbb{R}$", "Σ": r"$\Sigma$",
    "⌊": r"$\lfloor$", "⌋": r"$\rfloor$", "ℓ": r"$\ell$", "√": r"$\surd$",
}
for g in ["δ", "θ", "τ", "η", "β", "α", "γ", "Δ"]:
    PROSE[g] = "$" + MATH[g] + "$"
for sub in ["ᵢ", "ⱼ", "ⁿ", "ᵀ", "ᵐ", "₁", "₂", "ŷ"]:
    PROSE[sub] = "$" + MATH[sub] + "$"

# verbatim ASCII fallbacks for box-drawing and symbols
ASCII = {
    "─": "-", "│": "|", "┌": "+", "┐": "+", "└": "+", "┘": "+", "├": "+", "┤": "+",
    "┬": "+", "┴": "+", "┼": "+", "┃": "|", "►": ">", "◄": "<", "▼": "v", "▲": "^",
    "↓": "|", "↑": "|", "→": "->", "←": "<-", "█": "#", "░": ".", "—": "--", "–": "-",
    "δ": "d", "θ": "th", "τ": "t", "η": "eta", "β": "b", "α": "a", "γ": "g", "Δ": "D",
    "≈": "~=", "×": "x", "−": "-", "·": ".", "±": "+/-", "≥": ">=", "≤": "<=",
    "∞": "inf", "²": "^2", "∂": "d", "∩": "&", "∪": "|", "≫": ">>", "≳": ">~",
    "√": "sqrt", "Σ": "Sum", "ℝ": "R", "…": "...", "✓": "[x]", "§": "S",
    "ᵢ": "i", "ⱼ": "j", "ⁿ": "n", "ᵀ": "T", "ᵐ": "m", "₁": "1", "₂": "2", "ŷ": "y^",
    "∈": "in", "⊂": "subset", "⊄": "notsubset", "∇": "grad", "ℓ": "l",
    "⌊": "floor(", "⌋": ")", "DHAT": "dhat",
}


def pre(s):
    for a, b in PRE:
        s = s.replace(a, b)
    return s


def asciify(s):
    s = s.replace("DHAT", "dhat")
    return "".join(ASCII.get(c, c if ord(c) < 128 else "?") for c in s)


def mathify(s):
    s = s.replace("DHAT", r"\hat{\delta}")
    return "".join(MATH.get(c, c if ord(c) < 128 else "") for c in s)


def esc(t):
    t = t.replace("DHAT", r"$\hat{\delta}$")
    t = t.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}"), ("$", r"\$")]:
        t = t.replace(a, b)
    out = []
    for c in t:
        if ord(c) < 128:
            out.append(c)
        else:
            out.append(PROSE.get(c, ""))
    return "".join(out)


def inline(text):
    slots = []

    def stash(s):
        slots.append(s)
        return f"\0{len(slots)-1}\0"

    text = re.sub(r"\$\$(.+?)\$\$",
                  lambda m: stash(r"\[" + mathify(m.group(1)) + r"\]"), text, flags=re.S)
    text = re.sub(r"\$(.+?)\$",
                  lambda m: stash(r"\(" + mathify(m.group(1)) + r"\)"), text)
    text = re.sub(r"`([^`]+)`",
                  lambda m: stash(r"\texttt{" + esc(m.group(1)) + r"}"), text)
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)", r"\\textit{\1}", text)
    for i, s in enumerate(slots):
        text = text.replace(f"\0{i}\0", s)
    return text


def is_sep(row):
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    return len(cells) > 0 and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def table(rows):
    header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    n = len(header)
    w = round(15.0 / n, 2)
    colspec = "|" + "|".join([r">{\raggedright\arraybackslash}p{%scm}" % w] * n) + "|"
    out = [r"{\footnotesize", r"\begin{longtable}{%s}\hline" % colspec,
           " & ".join(r"\textbf{%s}" % inline(c) for c in header) + r" \\ \hline",
           r"\endhead"]
    for r in rows[2:]:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        cells += [""] * (n - len(cells))
        out.append(" & ".join(inline(c) for c in cells[:n]) + r" \\ \hline")
    out += [r"\end{longtable}", "}"]
    return "\n".join(out)


def convert(md):
    md = pre(md)
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(asciify(lines[j])); j += 1
            out.append(r"\begin{Verbatim}[breaklines=true,breakanywhere=true,"
                       r"fontsize=\footnotesize]")
            out.extend(buf); out.append(r"\end{Verbatim}")
            i = j + 1; continue
        if "|" in ln and i + 1 < len(lines) and is_sep(lines[i + 1]):
            j = i; buf = []
            while j < len(lines) and lines[j].strip() and "|" in lines[j]:
                buf.append(lines[j]); j += 1
            out.append(table(buf)); i = j; continue
        m = re.match(r"!\[(.*?)\]\((.+?)\)", ln)
        if m:
            ap = os.path.abspath(os.path.join(DOCS, m.group(2)))
            out.append(r"\begin{center}")
            out.append(r"\includegraphics[width=0.9\linewidth,height=0.46\textheight,"
                       r"keepaspectratio]{%s}\\[2pt]" % ap)
            out.append(r"{\small\textit{%s}}" % inline(m.group(1)))
            out.append(r"\end{center}"); i += 1; continue
        if ln.startswith("### "):
            out.append(r"\subsubsection*{%s}" % inline(ln[4:])); i += 1; continue
        if ln.startswith("## "):
            out.append(r"\subsection*{%s}" % inline(ln[3:])); i += 1; continue
        if ln.startswith("# "):
            t = inline(ln[2:])
            out.append(r"\clearpage\section*{%s}" % t)
            out.append(r"\addcontentsline{toc}{section}{%s}" % t); i += 1; continue
        if ln.strip() == "---":
            out.append(r"\vspace{3pt}\hrule\vspace{3pt}"); i += 1; continue
        if ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(lines[i][2:]); i += 1
            out.append(r"\begin{quote}\itshape " + inline(" ".join(buf)) + r"\end{quote}")
            continue
        if re.match(r"\s*[-*] ", ln) or re.match(r"\s*\d+\. ", ln):
            ordered = bool(re.match(r"\s*\d+\. ", ln))
            env = "enumerate" if ordered else "itemize"
            out.append(r"\begin{%s}\setlength{\itemsep}{1pt}" % env)
            while i < len(lines) and (re.match(r"\s*[-*] ", lines[i])
                                      or re.match(r"\s*\d+\. ", lines[i])):
                item = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i])
                out.append(r"\item " + inline(item)); i += 1
            out.append(r"\end{%s}" % env); continue
        if ln.strip() == "":
            out.append(""); i += 1; continue
        buf = [ln]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"(```|#|!\[|> |\s*[-*] |\s*\d+\. )", lines[i]) and not (
                "|" in lines[i] and i + 1 < len(lines) and is_sep(lines[i + 1])):
            buf.append(lines[i]); i += 1
        out.append(inline(" ".join(buf)))
    return "\n".join(out)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        DOCS, "UAV_Roadmark_Master_Monograph.md")
    body = convert(open(src).read())
    tex = PREAMBLE + r"\tableofcontents\clearpage" + "\n" + body + "\n" + POST
    base = os.path.splitext(os.path.basename(src))[0]
    open(os.path.join(DOCS, base + ".tex"), "w").write(tex)
    print("wrote tex (%d chars)" % len(tex))
    r = None
    for _ in range(3):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", base + ".tex"],
                           cwd=DOCS, capture_output=True, text=True)
    pdf = os.path.join(DOCS, base + ".pdf")
    if os.path.exists(pdf):
        pages = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
        print("PDF OK:", pdf)
        for l in pages.split("\n"):
            if l.startswith("Pages"):
                print(l)
    else:
        for l in (r.stdout + r.stderr).split("\n"):
            if l.startswith("!"):
                print("LATEX:", l)
        print("FAILED")


if __name__ == "__main__":
    main()
