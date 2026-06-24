/* Solution to Euler Problem 95: Amicable Chains. */
#include "runner.h"

/*
 * Two-phase functional-graph cycle search; O(N log N).
 *
 * Phase 1: an additive sieve fills divisor_sum[n] with the sum of n's proper
 *   divisors in O(N log N) by pushing each divisor i onto all its multiples.
 * Phase 2: treat n -> divisor_sum[n] as a functional graph and walk each
 *   unclassified node once. A functional graph decomposes into tails leading
 *   into cycles, so tracking the current path lets us detect the closing cycle
 *   (including mid-path cycles) and record the longest one. The smallest member
 *   of that longest cycle is the answer. Each node is touched O(1) times overall.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);

    /* Phase 1: additive sieve - accumulate each divisor i into its multiples. */
    int *divisor_sum = (int *)calloc((size_t)(max_num + 1), sizeof(int));
    if (!divisor_sum) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    for (int i = 1; i <= max_num / 2; i++) {
        for (int j = i * 2; j <= max_num; j += i) {
            divisor_sum[j] += i;
        }
    }

    /* Permanent classification: 0 = unvisited, positive = cycle length, -1 = tail. */
    int *seen = (int *)calloc((size_t)(max_num + 1), sizeof(int));
    if (!seen) {
        fprintf(stderr, "Out of memory\n");
        free(divisor_sum);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Transient per-walk state: 1-indexed position in current path (0 = absent),
     * so revisiting a node recovers its cycle-start index in O(1). */
    int *in_path = (int *)calloc((size_t)(max_num + 1), sizeof(int));
    if (!in_path) {
        fprintf(stderr, "Out of memory\n");
        free(divisor_sum);
        free(seen);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Ordered record of the nodes visited in the current walk. */
    int *path = (int *)malloc((size_t)(max_num + 1) * sizeof(int));
    if (!path) {
        fprintf(stderr, "Out of memory\n");
        free(divisor_sum);
        free(seen);
        free(in_path);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int smallest_member = 0;
    int longest_length = 0;

    /* Phase 2: classify every node by walking its chain at most once. */
    for (int i = 1; i <= max_num; i++) {
        if (seen[i]) continue;

        /* Walk the chain from i, recording each node and its path position. */
        int path_len = 0;
        path[path_len++] = i;
        in_path[i] = path_len; /* position 1-indexed */

        int c = divisor_sum[i];

        /* Stop on leaving range, re-entering this walk, or hitting prior work. */
        while (c >= 1 && c <= max_num && !in_path[c] && !seen[c]) {
            path[path_len++] = c;
            in_path[c] = path_len;
            c = divisor_sum[c];
        }

        /* Cycle closes back to the start: the whole path is one amicable chain. */
        if (c == i) {
            int len_ch = path_len;
            if (len_ch > longest_length) {
                longest_length = len_ch;
                smallest_member = i;
            }
            for (int k = 0; k < path_len; k++) {
                seen[path[k]] = len_ch;
            }
        } else if (c >= 1 && c <= max_num && in_path[c]) {
            /* Mid-path cycle: it begins at the recorded position of c; nodes
             * before that are tail, nodes from there on form the cycle. */
            int cycle_start_pos = in_path[c] - 1; /* 0-indexed */
            int cycle_len = path_len - cycle_start_pos;

            if (cycle_len > longest_length) {
                longest_length = cycle_len;
                /* Smallest member is the minimum over the cycle's nodes. */
                int min_val = path[cycle_start_pos];
                for (int k = cycle_start_pos + 1; k < path_len; k++) {
                    if (path[k] < min_val) min_val = path[k];
                }
                smallest_member = min_val;
            }
            /* Tail nodes get -1; cycle nodes get the cycle length. */
            for (int k = 0; k < path_len; k++) {
                seen[path[k]] = (k >= cycle_start_pos) ? cycle_len : -1;
            }
        } else {
            /* Walk ran off the range or into prior work with no cycle: all tail. */
            for (int k = 0; k < path_len; k++) {
                seen[path[k]] = -1;
            }
        }

        /* Targeted cleanup: reset in_path only for the nodes we touched. */
        for (int k = 0; k < path_len; k++) {
            in_path[path[k]] = 0;
        }
    }

    free(divisor_sum);
    free(seen);
    free(in_path);
    free(path);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)smallest_member)); return _answer; }
}