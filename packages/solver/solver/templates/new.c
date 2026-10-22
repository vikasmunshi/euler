/** Solution to Euler $problem.
 *
 * A thin solution template: `#include "runner.h"` supplies everything but `solve()`. Its
 * `main()` parses `--runs=N` / `--show`, benchmarks `solve()`, checks the result is consistent
 * across runs, and prints the `<runs> <avg_seconds> <result>` line the harness reads. The header
 * also provides the argument helpers — `parse_int` (ints, power notation, '_' separators),
 * `parse_list` ("[1,2,3]" literals), `get_text_file` (a statement-linked file, served from the
 * cached resources/ copy) — and the `show` flag (set by `--show`).
 *
 * Typical workflow:
 *     1. Implement solve(): parse each argv[i] with the runner helper it needs, then return
 *        the answer as a NUL-terminated string.
 *     2. Compile (solver compile), then run: ./file <arg>... [--runs=N] [--show]
 */
#include "runner.h"

/** Solve the Project Euler problem with the given parameters.
 *
 * Name the approach and its complexity here — e.g. "Inclusion-exclusion on the
 * closed-form arithmetic-series sum; O(1)." — then replace this placeholder with the
 * real approach. argv[0] is the program name; positional arguments follow (flags are
 * stripped by the runner).
 *
 * @param argc Number of forwarded arguments.
 * @param argv Forwarded positional arguments.
 * @return The computed answer as a NUL-terminated string (see runner.h), or NULL.
 */
const char *solve(int argc, char *argv[]) {
    /* Each line is an independent example — use whichever helper the problem needs. */
    long long arg1 = parse_int(argv[1]);               /* parse an integer (power notation, '_' separators) */
    int arg2_len;
    long long *arg2 = parse_list(argv[1], &arg2_len);  /* parse a list literal: "[1,2,3]" -> {1,2,3} */
    char *arg3 = get_text_file(argv[1]);               /* read a file from resources/ */
    if (show) {                                        /* gate intermediate output behind --show */
        printf("arg1=%lld, arg2=[", arg1);
        for (int i = 0; i < arg2_len; i++) printf("%s%lld", i ? "," : "", arg2[i]);
        printf("], arg3=%s\n", arg3 ? arg3 : "(null)");
    }
    free(arg2);
    free(arg3);
    /* Return the answer as a string. For a numeric result, format into a static
     * buffer that outlives this call, e.g.:
     *     static char answer[32];
     *     snprintf(answer, sizeof answer, "%lld", result);
     *     return answer;
     */
    fprintf(stderr, "implement solve() first\n");
    return NULL;  /* TODO: implement solve() */
}