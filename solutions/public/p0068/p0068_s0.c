/* Solution to Euler Problem 68: Magic 5-gon Ring. */
#include "runner.h"

/*
 * Enumerate only the n inner-ring positions (permutations of values drawn from
 * {1..min(9, 2n)}; the cap pins 10 to an outer node so n=5 yields 16 digits) and
 * force every outer value from the line-sum constraint outer[i] = S - (inner[i] +
 * inner[i+1]) after pinning the smallest free value at outer[0] to fix rotation.
 * Reject duplicate inner sums early. Complexity O(P(min(9, 2n), n) * n).
 */

static int n_global;
static int inner_choice[20];
static int outer_choice[20];
static char max_magic_str[200];
static int used[25];

/* Compare two numeric strings: longer = larger; equal length = lexicographic. */
static int cmp_magic(const char *a, const char *b) {
    size_t la = strlen(a), lb = strlen(b);
    if (la != lb) return (la > lb) ? 1 : -1;
    return strcmp(a, b);
}

/* Backtracking over inner positions; at full depth force the outer ring and score. */
static void solve_recursive(int depth) {
    if (depth == n_global) {
        int n = n_global;
        int inner_sums[20];
        for (int i = 0; i < n; i++) {
            inner_sums[i] = inner_choice[i] + inner_choice[(i + 1) % n];
        }
        /* Equal inner sums would force two lines onto the same outer node - reject. */
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
        /* Pin the smallest free value at outer[0] to canonicalise the start. */
        outer_choice[0] = min_outer;
        oc_available[min_outer] = 0;

        /* Magic total S, then force each remaining outer value; abort on any miss. */
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

        /* Concatenate lines (outer, inner, next inner) and keep the largest. */
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

    /* Cap inner values at 9 (when applicable) so the longest digit 10 stays outside. */
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

const char *solve(int argc, char *argv[]) {
    int result_length = parse_int(argv[1]);
    int ring_size = parse_int(argv[2]);
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