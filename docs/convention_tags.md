# Tag conventions

These govern a problem's `tags.json` — the per-problem leg of the tag graph that powers the
topic articles under `topics/`. They are distinct from the
[Documentation conventions](convention_documentation.md), which govern `notes.html`.

`notes.html` explains *what the problem is* and *how each solution works*. The **programming
techniques** a solution uses and the **transferable takeaways** it teaches are not written as prose
there — they are recorded as tags in `tags.json`, so they can be collected across problems into
topic pages.

## The graph

Every tag is one of three **facets**:

- **domain** — what the problem is *about*: the mathematical or computational subject
  (number theory, combinatorics, a specific object like a palindrome or a Pythagorean triple).
  Attaches to the **problem**.
- **technique** — *how* a solution works: an algorithm, data structure, or language/library device
  (sieve of Eratosthenes, dynamic programming, memoization, a generator, C manual memory). Attaches
  to a **solution index** — different indices use different techniques.
- **takeaway** — a **transferable principle** the problem teaches ("prefer a closed form over
  iteration", "a better algorithm beats a faster language"). Attaches to the **problem**.

The central vocabulary of allowed tags lives in `topics/tags.json`; each entry has a `slug`, a
`facet`, a human `name`, and a canonical `reference` URL. **Always choose an existing tag by its
slug.** Propose a new one (below) only when nothing in the vocabulary fits.

## The file — `tags.json`

Written as standard `json.dumps(indent=2)`. Four keys:

```json
{
  "domain": ["arithmetic-progression", "triangular-number"],
  "takeaways": ["closed-form-over-iteration", "algorithm-beats-language"],
  "techniques": {
    "s0": ["inclusion-exclusion-principle", "closed-form-expression"],
    "s1": ["brute-force-search"],
    "s2": ["arithmetic-progression"]
  },
  "new-tags": []
}
```

- `domain` / `takeaways` — flat lists of vocabulary slugs (facet `domain` / `takeaway`).
- `techniques` — a map from **each solution index** (`s0`, `s1`, …, one key per `pNNNN_sK` that
  exists) to the technique slugs *that index actually uses*. Read the code per index: index 0's list
  must reflect index 0's algorithm, not the problem in general. An index that shares an algorithm
  across Python and C lists it once. An index with no notable technique may have an empty list.
- Every slug in `domain`, `takeaways`, and each `techniques` list must exist in `topics/tags.json`
  and match its facet there. Do not put a `technique` slug under `domain`, etc.

## Adding a new tag — `new-tags`

When a solution genuinely needs a tag the vocabulary lacks, add its **full definition** to
`new-tags` (do **not** invent a bare slug in the facet lists). The maintainer's `update-tags`
command promotes each proposal into `topics/tags.json` and files it into the right bucket.

```json
"new-tags": [
  {
    "slug": "gauss-summation",
    "facet": "technique",
    "name": "Gauss summation trick",
    "reference": "https://en.wikipedia.org/wiki/1_%2B_2_%2B_3_%2B_4_%2B_%E2%8B%AF",
    "summary": "Pairing the ends of an arithmetic run to sum it in closed form.",
    "applies-to": ["s0"]
  }
]
```

- `slug` — lowercase, hyphen-separated, derived from the canonical name.
- `facet` — `domain`, `technique`, or `takeaway`.
- `reference` — an authoritative public URL (Wikipedia, official docs, MathWorld, OEIS). **Omit any
  `#bookmark`** — the base page is the reference — *unless* the anchor is the identity (a specific
  symbol on a shared docs page, e.g. `functions.html#any`), in which case keep the anchor.
  `takeaway` tags have no URL: use `null`.
- `summary` — one sentence.
- `applies-to` — for a `technique` proposal, the solution indices it applies to (`["s0", "s2"]`);
  omit for `domain` / `takeaway`.

Prefer reusing an existing tag over proposing a near-duplicate; propose sparingly.

## Choosing good tags

- **domain**: name the subject a reader would search for, not the method. Two or three is typical.
- **technique**: the algorithms, data structures, and notable language/library devices a given
  index relies on — the things a "how did this work" reader would want indexed.
- **takeaway**: only genuinely transferable lessons, phrased as advice — not restatements of the
  problem. Zero is acceptable; more than three or four is rare.
