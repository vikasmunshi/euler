/** Runner framework for Project Euler solutions with benchmarking and validation.
 *
 * Header-only C analogue of `runner.py`. A solution source file includes this
 * header and implements `solve()`; the framework supplies `main()`, argument
 * parsing, benchmarking, and consistency checking.
 *
 *     #include "runner.h"
 *
 *     const char *solve(int argc, char *argv[]) { ... }
 *
 * Helpers are `static inline` so an including translation unit may use only the
 * ones it needs without tripping `-Werror` on unused functions. `main()` is
 * defined here, so each solution remains a single-source, single-executable
 * build (see scripts/c/compile.sh).
 *
 * Declarations follow the same order as runner.py: solve, get_text_file, show,
 * main, parse_int, parse_list.
 */
#ifndef SOLVER_RUNNER_H
#define SOLVER_RUNNER_H

#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/** Solve the Project Euler problem; implemented by the solution source file.
 *
 * Returns the answer as a string so any result type (integer, big number,
 * concatenation, ...) is expressible. The returned pointer is owned by solve()
 * and must stay valid until the next call — return a string literal or write
 * into a `static` buffer; do not return a per-call malloc'd buffer (it would
 * leak across --runs). Return NULL to signal failure.
 *
 * @param argc Number of forwarded arguments (argv[0] is the program name).
 * @param argv Forwarded positional arguments with --runs= and --show removed.
 * @return The computed answer as a NUL-terminated string, or NULL on failure.
 */
const char *solve(int argc, char *argv[]);

/* The invoking program path (argv[0]); set by main(), read by get_text_file().
 * Mirrors runner.py resolving resources from argv[0] rather than the binary's own
 * location — directory-of-argv[0] is the solution dir regardless of cwd. */
static const char *runner_argv0 = "";

/** Return the contents of a file from the 'resources' directory next to the solution.
 *
 * Resolves the path relative to the invoking program's directory (argv[0]'s parent),
 * looking in a sibling 'resources' subdirectory. Handles URLs by extracting the
 * filename.
 *
 * @param src File path or URL. Only the filename (after last '/') is used, and
 *            query parameters (after '?') are stripped.
 * @return The complete file contents as a null-terminated string, or NULL on
 *         error. The caller is responsible for freeing the returned buffer.
 */
static inline char *get_text_file(const char *src) {
    const char *slash = strrchr(src, '/');
    const char *name_start = slash ? slash + 1 : src;
    const char *q = strchr(name_start, '?');
    size_t name_len = q ? (size_t)(q - name_start) : strlen(name_start);

    char prog[4096];  /* mutable copy — dirname() may modify its argument */
    if ((size_t)snprintf(prog, sizeof(prog), "%s", runner_argv0) >= sizeof(prog)) return NULL;

    char path[4096];
    int pn = snprintf(path, sizeof(path), "%s/resources/%.*s", dirname(prog), (int)name_len, name_start);
    if (pn < 0 || (size_t)pn >= sizeof(path)) return NULL;

    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return NULL; }
    rewind(f);
    char *buf = malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return NULL; }
    if (fread(buf, 1, (size_t)sz, f) != (size_t)sz) { free(buf); fclose(f); return NULL; }
    buf[sz] = '\0';
    fclose(f);
    return buf;
}

/* Whether --show was passed; set by main(), read directly inside solve(). */
static int show = 0;

/** Run the solver with benchmarking and consistency checking.
 *
 * Executes solve() one or more times, validates that results are consistent
 * across runs, and prints timing and result information. Errors go to stderr.
 *
 * Output format (stdout): "<runs> <avg_seconds> <result>".
 *
 * Command-line arguments:
 *     <kwarg>...: Problem-specific parameters (forwarded to solve()).
 *     --runs=N:   Execute solve() N times (default 1) for benchmarking.
 *     --show:     Set the `show` flag for intermediate output inside solve().
 *
 * @return 0 on success, 1 if results were inconsistent across runs.
 */
int main(int argc, char *argv[]) {
    int runs = 1;
    runner_argv0 = argv[0];  /* for get_text_file(): resolves resources/ next to the solution */

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) {
        fprintf(stderr, "runner: out of memory\n");
        return 1;
    }
    int solve_argc = 0;
    solve_argv[solve_argc++] = argv[0];

    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '\0') continue;
        if (strncmp(argv[i], "--runs=", 7) == 0) {
            int r = atoi(argv[i] + 7);
            if (r >= 1) runs = r;
            continue;
        }
        if (strcmp(argv[i], "--show") == 0) {
            show = 1;
            continue;
        }
        solve_argv[solve_argc++] = argv[i];
    }

    char *result = NULL;  /* strdup'd copy of the latest result, owned by the runner */
    double total = 0.0;
    int rc = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        const char *cur = solve(solve_argc, solve_argv);  /* <= timed call */
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (!cur) {
            fprintf(stderr, "Expected a result, got NULL\n");
            rc = 1;
            continue;
        }
        if (result && strcmp(cur, result) != 0) {
            fprintf(stderr, "Expected consistent result, got %s previous result=%s\n",
                    cur, result);
            rc = 1;
        }
        free(result);
        result = strdup(cur);
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "(null)");
    free(result);
    return rc;
}

/** Parse an int given as a plain integer, power notation, or with underscores.
 *
 * @param token The argument string, e.g. "1000", "2**20", or "1_000_000". A "**"
 *              separator marks integer exponentiation and any '_' digit
 *              separators are ignored.
 * @return The parsed value as a long long integer.
 */
static inline long long parse_int(const char *token) {
    char clean[64];
    size_t j = 0;
    for (size_t i = 0; token[i] != '\0' && j + 1 < sizeof(clean); i++) {
        if (token[i] != '_') clean[j++] = token[i];
    }
    clean[j] = '\0';

    const char *sep = strstr(clean, "**");
    if (sep) {
        long long base = atoll(clean);
        long long exp = atoll(sep + 2);
        long long result = 1;
        for (long long i = 0; i < exp; i++) result *= base;
        return result;
    }
    return atoll(clean);
}

/** Parse a bracketed list of integers, e.g. "[1, 2, 3]" -> {1, 2, 3}.
 *
 * Brackets, whitespace, and commas are treated as separators; signed decimal
 * integers between them are collected. "[]" yields an empty list.
 *
 * @param token The list literal, e.g. "[1,2,3]" or "[-4, 5]".
 * @param count Out-parameter set to the number of parsed integers.
 * @return A malloc'd array of the parsed values, or NULL on allocation failure.
 *         The caller is responsible for freeing the returned buffer.
 */
static inline long long *parse_list(const char *token, int *count) {
    size_t cap = 1;
    for (const char *p = token; *p; p++) if (*p == ',') cap++;
    long long *out = malloc(cap * sizeof(long long));
    int n = 0;
    if (out) {
        const char *p = token;
        while (*p) {
            while (*p && *p != '-' && *p != '+' && !(*p >= '0' && *p <= '9')) p++;
            if (!*p) break;
            char *end;
            long long v = strtoll(p, &end, 10);
            if (end == p) break;
            out[n++] = v;
            p = end;
        }
    }
    if (count) *count = n;
    return out;
}

#endif /* SOLVER_RUNNER_H */