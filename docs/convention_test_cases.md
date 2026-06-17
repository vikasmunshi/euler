# Generating test cases

Produce the `test_cases.json` for a problem: a JSON array of cases that follow the schema and rules
below.

Test case schema:

{
"category": "dev" | "main" | "extra",
"input": { "<param_name>": <value>, ... },
"answer": <number> | <string> | null
}

Analyse the problem statement (file 'statement.html') carefully, then produce a JSON array of
test cases that follow the schema above and the rules below.

1. **`dev` test cases** — Extract every worked example in the problem statement whose
   answer is stated explicitly. Use `"category": "dev"`.

2. **`main` test case** — Extract the actual problem input (the one whose answer is being sought).
   Use `"category": "main"` and set `"answer": null`, since the problem is not yet solved.

3. **`extra` test cases** — Add 1–2 cases with inputs larger than `main` to serve as benchmarks.
   Use `"category": "extra"` and set `"answer": null`. Size them so that a correct, efficient
   solution finishes within roughly 60 seconds; if `main` is already at the high end of what is
   reasonably solvable, skip the `extra` cases.

4. **Input keys** — Choose concise, snake_case key names that describe each parameter
   (e.g. `"limit"`, `"n"`, `"max_n"`, `"grid_size"`). If the problem takes no variable input
   (a fixed puzzle), use `"input": {}`.

   **A statement-linked data file is always passed as `file_url`** (its projecteuler.net URL),
   which the solution reads via `get_text_file` from the locally cached `resources/` copy. An
   **empty** `file_url` (`""`) means *use data embedded in the solution module as a variable*
   instead of reading a file — common for a small `dev` case whose data is short enough to inline.
   The solution branches on it: a non-empty `file_url` reads the resource; an empty one falls back
   to the embedded variable.

5. **Type consistency** — The answer type must be identical across `dev`, `main`, and `extra` for
   the same problem. If the `dev` answers are integers, then `main` and `extra` will be integers
   once solved (so their `null` values should later be filled with integers); the same applies to
   strings and lists. Do not mix answer types across categories.

6. **Ordering** — List the `dev` cases first, then `main`, then the `extra` cases last.