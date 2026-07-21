# Documentation conventions

These govern the `notes.html` worked-solution article. They are distinct from the
[Source documentation conventions](convention_source_documentation.md),
which govern the in-source docstrings and comments.

Write `notes.html` as a single `<article>` of worked-solution notes for a
"Programming Techniques" course — the audience being engineers learning to write efficient,
well-reasoned programs. Voice: **first person** ("I chose…", "My approach…"), clear, precise, and
authoritative. Explain not just *what* but *why* — justify every algorithmic and implementation
decision so a reader can learn to reason the same way. Readability, consistency, and accuracy all
matter: a reader should come away understanding and appreciating the mathematical depth of the
solution.

Use only semantic HTML5: `<article>`, `<h3>`, `<h4>`, `<p>`, `<ul>` / `<li>`, `<table>`, `<code>`,
and `<a>`. No `<html>` / `<head>` / `<body>`, no markdown, no code fences, and no preamble — the
file is the HTML only. Do not repeat the problem statement verbatim, and do not include the problem
title as a heading.

**Mathematics:** the page renders math with MathJax configured for **TeX only** — inline as
`$…$` and display as `$$…$$`. Write every mathematical expression, variable, subscript,
superscript, or operator as TeX inside those delimiters: `$2 \times n$`, `$10^{16}$`,
`$c_{j+k} = c_j$`, `$n \bmod k = 0$`, `$O(k \log \text{MOD})$`, and so on. **Never** emit
`<math>` / MathML tags or HTML entities (`&times;`, `&isin;`, `&le;`, …) for math — MathJax
treats a `<math>` element as MathML and renders a red "Math input error", and entities inside
math are not interpreted. Reserve `<code>` for literal code identifiers and snippets, not for
mathematical notation. Escape a literal dollar sign that is not a math delimiter as `\$`.

Exactly two sections:

1. **`<h3>Problem Analysis</h3>`** — one or two paragraphs on the mathematical ideas (number
   theory, combinatorics, dynamic programming, …), the key observations that make the problem
   tractable, and the asymptotic complexity class. Define every technical term for an engineer
   meeting it for the first time, and explain why each observation matters.
2. **`<h3>Solution Approach</h3>`** — an `<h4>` subsection for *each distinct algorithm* (each
   solution index). If a Python and a C file share an index, cover them together and note any
   language-specific differences. Name the approach from the *code*, not the filename. Explain the
   algorithm step by step, justify each significant design choice, and map the code to the
   algorithm. When more than one solution exists, compare them using the recorded `average` times
   (which is fastest or most elegant, and why), basing every timing claim on the benchmark results;
   with a single solution, omit any comparison and do not mention the absence of others.

**Scope — analysis and approach only.** `notes.html` covers *what the problem is* and *how each
solution works*. It does **not** enumerate programming techniques or list transferable takeaways:
those are captured as **tags** (`tags.json`, see [Tag conventions](convention_tags.md)) and
discussed in the topic articles under `topics/`. Do not add a `Programming Techniques` or
`Key Takeaways` section, and do not end with a bulleted list of general principles.

**Hyperlinking technical terms:** **every** occurrence of each non-trivial technical term (e.g.
"Sieve of Eratosthenes", "dynamic programming", "modular exponentiation", "memoization",
"continued fraction") must be wrapped in a hyperlink to an authoritative public source — preferably
the relevant Wikipedia article, or else a reputable reference (official docs, MathWorld, OEIS).
Link **every** instance, including repeats — not just the first. Use exactly:
`<a href="URL" class="reference-source" target="_blank" rel="noopener noreferrer">technical term</a>`
— the `class="reference-source"` attribute is mandatory, and links must open in a new tab.