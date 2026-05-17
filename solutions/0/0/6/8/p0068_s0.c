/* Solution to Euler Problem 68: Magic 5-gon Ring. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int n_global;
static int inner_choice[20];
static int outer_choice[20];
static char max_magic_str[200];
static int used[25];

/* Compare two numeric strings: longer = larger; equal length = lexicographic */
static int cmp_magic(const char *a, const char *b) {
    size_t la = strlen(a), lb = strlen(b);
    if (la != lb) return (la > lb) ? 1 : -1;
    return strcmp(a, b);
}

static void solve_recursive(int depth) {
    if (depth == n_global) {
        int n = n_global;
        int inner_sums[20];
        for (int i = 0; i < n; i++) {
            inner_sums[i] = inner_choice[i] + inner_choice[(i + 1) % n];
        }
        /* Check all distinct */
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (inner_sums[i] == inner_sums[j]) return;
            }
        }
        /* Build outer candidates availability */
        int oc_available[25];
        memset(oc_available, 0, sizeof(oc_available));
        int min_outer = 2 * n + 1;
        for (int v = 1; v <= 2 * n; v++) {
            if (!used[v]) {
                oc_available[v] = 1;
                if (v < min_outer) min_outer = v;
            }
        }
        outer_choice[0] = min_outer;
        oc_available[min_outer] = 0;

        int line_sum = min_outer + inner_sums[0];
        int valid = 1;
        for (int i = 1; i < n; i++) {
            int required = line_sum - inner_sums[i];
            if (required < 1 || required > 2 * n || !oc_available[required]) {
                valid = 0;
                break;
            }
            oc_available[required] = 0;
            outer_choice[i] = required;
        }
        if (!valid) return;

        /* Build the concatenated string */
        char magic_str[200];
        magic_str[0] = '\0';
        char buf[20];
        for (int i = 0; i < n; i++) {
            snprintf(buf, sizeof(buf), "%d", outer_choice[i]);
            strcat(magic_str, buf);
            snprintf(buf, sizeof(buf), "%d", inner_choice[i]);
            strcat(magic_str, buf);
            snprintf(buf, sizeof(buf), "%d", inner_choice[(i + 1) % n]);
            strcat(magic_str, buf);
        }
        if (max_magic_str[0] == '\0' || cmp_magic(magic_str, max_magic_str) > 0) {
            strcpy(max_magic_str, magic_str);
        }
        return;
    }

    int max_inner = (9 < 2 * n_global) ? 9 : 2 * n_global;
    for (int v = 1; v <= max_inner; v++) {
        if (!used[v]) {
            used[v] = 1;
            inner_choice[depth] = v;
            solve_recursive(depth + 1);
            used[v] = 0;
        }
    }
}

char *solve(int argc, char *argv[]) {
    int result_length = atoi(argv[1]);
    int ring_size = atoi(argv[2]);
    n_global = ring_size;

    memset(used, 0, sizeof(used));
    max_magic_str[0] = '\0';

    solve_recursive(0);

    int actual_len = (int)strlen(max_magic_str);
    if (actual_len != result_length) {
        fprintf(stderr, "Result length mismatch: expected %d, got %d, result=%s\n",
                result_length, actual_len, max_magic_str);
    }

    char *result = malloc(strlen(max_magic_str) + 1);
    if (!result) return NULL;
    strcpy(result, max_magic_str);
    return result;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;

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
        if (strcmp(argv[i], "--show") == 0) continue;
        solve_argv[solve_argc++] = argv[i];
    }

    char *result = NULL;
    double total = 0.0;
    int rc = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (result != NULL) {
            if (strcmp(cur, result) != 0) {
                fprintf(stderr, "Expected consistent result, got %s previous result=%s\n",
                        cur, result);
                rc = 1;
            }
            free(result);
        }
        result = cur;
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "");
    free(result);
    return rc;
}