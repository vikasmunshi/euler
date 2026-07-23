---
name: claude-euler-blogger
description: Use when Claude is launched by the `claude-blog` command via
  `claude -p /claude-euler-blogger <tag-or-topic> [additional_prompt]` to write (or flesh out)
  one topic article under `topics/`. Claude runs headless at the repository root, researches the
  problems that carry the tag(s), and edits the article's Markdown directly. The `<tag-or-topic>`
  is a tag's `<facet>/<slug>` path (e.g. `technique/sieve-of-eratosthenes`), a bare tag slug, or a
  curated topic path (e.g. `number-theory/primes`). Do NOT activate for a generic "write a blog
  post" or for solving problems.
version: 0.2.0
model: opus
---

# Claude Euler Blogger (headless)

A skill that runs **headless** to write one topic page under `topics/`. The `claude-blog` shell
command launches Claude with:

```
claude -p /claude-euler-blogger <tag-or-topic> [additional_prompt]
```

A **topic** collects the problems that share a tag and explains the idea behind them. Each tag has
a page at `topics/<facet>/<slug>.md`; curated cross-cutting topics live elsewhere under `topics/`
(e.g. `topics/number-theory/primes.md`). Claude researches the covered problems, writes the page,
refreshes its Problems section, commits, and **ends the turn**.

## Read first — the conventions

The tag graph and the house voice are the two things to honour:

- **[docs/convention_tags.md](docs/convention_tags.md)** — the tag system: the three facets
  (domain / technique / takeaway), and how a page declares the tags it covers.
- **[docs/convention_documentation.md](docs/convention_documentation.md)** — the writing voice
  used in `notes.html`: a "Programming Techniques" course for engineers, first person, precise,
  *why* not just *what*. A topic page carries that same voice, one level up: it explains the idea
  across many problems, not one.

The central vocabulary is `topics/tags.json` (each tag's `name`, `reference` URL, and `refs` — the
problems/solutions that carry it). Read the exact `solver` command usage in
**[docs/commands-index.md](docs/commands-index.md)** — especially
[`topic`](docs/commands-index.md#command-topic), [`topics`](docs/commands-index.md#command-topics),
and [`update-tags`](docs/commands-index.md#command-update-tags).

## Rule — reference private problems, but never hand out their answer

Problems **> 100** live under `solutions/private/` and are encrypted at rest, because Project
Euler asks that solutions to problems past 100 not be published. Topic pages under `topics/` are
plaintext and public. The boundary that follows is about the **answer**, not the problem:

- **Do** name a private problem by number, summarise its statement, and explain the shared idea
  and the approach in your own words — that is the point of a topic page, and a page that ducks
  every private problem is a worse page.
- **Do** include a small illustrative snippet **only if it cannot compute the answer** — a
  two-line sketch of the general technique, a formula, a shape of a loop. If someone could paste
  it and get the number, it is too much.
- **Never** print a private problem's final answer, and never paste its full working solution
  code or its `notes.html` verbatim. For anything you want to *quote at length*, use a **public**
  problem (`solutions/public/pNNNN/`), whose code is already published.

When in doubt, describe the method and link the problem; the reader can open the solution
themselves if they are entitled to it.

## Execution model

Runs at the repository root and edits the one target page in place. `solver` is on `PATH`; run
subcommands directly (`solver "topic technique/sieve-of-eratosthenes"`). These Bash commands run
without confirmation; the skill also relies on `Edit`/`Write` under `topics/**` and `Read` on the
project tree — keep `.claude/settings.local.json` in sync:

    - bash solver *
    - bash git add:* / git commit:*
    - edit/write topics/**      # the article
    - read ./**

Do **not** change `cwd`; every command runs from the project root, no `./` prefix.

---

## Phase 1 — Resolve the target

The argument is one of: a `<facet>/<slug>` path, a bare tag slug, or a curated topic path.

0. **Run `solver "update-tags"` first.** It regenerates every page's **Problems** section from the
   current graph — so the list you write around is fresh, with each problem's title and a
   solved/unsolved marker baked in as of now. (You will run it again at the end.)
1. Resolve the argument to a file:
    - a `<facet>/<slug>` path → `topics/<facet>/<slug>.md`;
    - a bare slug → look it up in `topics/tags.json`, take its `facet`, target `topics/<facet>/<slug>.md`;
    - any other path → `topics/<path>.md`.
2. Run `solver "topic <path-without-.md>"` to see the tag(s) the page declares and the
   problems/solutions on their central legs.
3. Read the target file — after step 0 it always exists. It is usually a **skeleton**: a
   `<!-- tags: [...] -->` comment on line 1, a `<!-- status: draft -->` comment under it, an
   `# H1` title, a `_TODO: …_` stub, and a generated **Problems** section delimited by
   `<!-- problems (generated by update-tags) -->` … `<!-- /problems -->`. That section is
   machine-owned and **rendered** — it is the reader's list of the covered problems. You replace
   the `_TODO_` stub with prose; **leave the tags comment, the status comment, and the whole
   Problems section exactly as they are** — `update-tags` owns them, and the save gate refuses an
   edit that changes them.

The status is the page's state of writing: `draft` while it is a stub or half-written, `final` once
it is a finished article. `topics/articles.json` (the article index, maintained by `update-tags`)
mirrors it. The `claude-blog` command refuses a `final` page unless it was run with `--force`, so if
you were launched on one, the maintainer asked for a rewrite deliberately.

If the `[additional_prompt]` gave an angle or constraint, factor it in without overriding the
conventions.

## Phase 2 — Research the idea

1. Read the tag's `reference` URL and `name` from `topics/tags.json` to pin the concept.
2. From the problems on the tag's legs, read a representative handful — their `statement.html`,
   `notes.html` (Problem Analysis + Solution Approach), and, the solution code — to see how the
   idea is actually used and where it varies.
3. Note the through-line: what the idea *is*, why it recurs across these problems, the shape it
   takes, and when an engineer should reach for it.

## Phase 3 — Write the page

Replace the `_TODO_` stub (or, for a new curated topic, create the file) with a focused article:

- **Lead** — one short paragraph: what this domain / technique / takeaway is, and why it keeps
  coming back across the problems below.
- **The idea** — the shared structure or method, explained once, well. Define terms; link the
  central `reference` and other authoritative sources (Wikipedia, official docs, OEIS, MathWorld)
  inline as normal Markdown links.
- **How to reason about it** — when it applies, what it buys, the trade-offs and pitfalls.

**Do not write a problems list.** The generated **Problems** section already lists every covered
problem, with links, titles and solved markers — that is what replaces the old hand-picked "in the
wild" section. Write your prose *above* that section; you may refer to specific problems by number
in the flow of the idea (a public one when you want to quote code — see the private-problem rule),
but do not duplicate the list.

Keep it tight — a topic page, not an essay. Leave the `<!-- tags: [...] -->` comment, the
`<!-- status: … -->` comment, and the whole `<!-- problems … -->` … `<!-- /problems -->` section
exactly as they are — `update-tags` owns them. Use GitHub-flavoured Markdown (`##` headings,
tables, code fences); do **not** put raw HTML in the page (it renders to every reader and the save
gate refuses it). A new curated page must open with its own `<!-- tags: [slug, …] -->` comment,
carry a `<!-- status: draft -->` comment under it, and include an empty
`<!-- problems (generated by update-tags) -->` / `<!-- /problems -->` pair for `update-tags` to
fill.

## Phase 4 — Refresh, then finalize (always last)

1. **Mark the page final.** The article is written, so change its status comment to

       <!-- status: final -->

   Do this only for a page you actually finished — if you stopped short (missing research, an
   unresolved `update-tags` issue, a half-written section), leave it `draft`, say so in the summary,
   and stop. `final` is a claim that the page needs no more writing.
2. **Refresh the Problems section:** `solver "update-tags"` — it rewrites every article's
   Problems section (fresh titles and solved markers), reconciles the graph, and updates
   `topics/articles.json` (where your new status lands). Then `solver "update-tags --check"` must
   exit `0`; fix any issue it names (an unknown tag in your `<!-- tags: -->` comment, most likely)
   and re-run.
3. **Sanity-check:** `solver "topic <path>"` lists the tags and problems the page now resolves to.
4. **Commit with `git-commit-docs`:**

       solver "git-commit-docs 'docs(topic): <name>'"

   That command stages the whole documentation set — `topics/` included — so your page goes in
   together with everything `update-tags` touched (`topics/tags.json`, `topics/articles.json`) in
   one commit, and nothing outside that set can ride along. The message is tagged `(docs)`
   automatically. Topic pages carry no solutions, so it needs no secrecy — just say what was
   written.

   Do **not** use `solver "commit"`: that command is problem-scoped — it stages a
   `solutions/pNNNN` directory plus `problems.json`, *not* a topic page, so it would not commit
   your work at all.

Then **summarise** in one or two sentences (which page, and the idea you drew out) and end the turn.

---

## Notes & failure modes to avoid

- Write about the **idea across the problems**, not a recap of any single solution — that is what
  `notes.html` is for.
- Never print a private (`> 100`) problem's answer or paste its full solution code / notes; name
  it, summarise, and take any quotable code from a public problem (see the private-problem rule).
- Do not hand-edit the `<!-- problems … -->` section or the `<!-- tags: -->` comment's membership
  to force a problem in or out — fix the tags at their source (a problem's `tags.json`) if the
  mapping is wrong, then `update-tags`. The save gate refuses edits to those regions anyway.
- A non-zero `update-tags --check`, or a lint/commit failure, is a stop-and-report, not a reason to
  push on.
