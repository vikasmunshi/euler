/* Solution to Euler Problem 95: Amicable Chains. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

long long solve(int argc, char *argv[]) {
    int max_num = atoi(argv[1]);

    /* Build divisor sum array using additive sieve */
    int *divisor_sum = (int *)calloc((size_t)(max_num + 1), sizeof(int));
    if (!divisor_sum) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    for (int i = 1; i <= max_num / 2; i++) {
        for (int j = i * 2; j <= max_num; j += i) {
            divisor_sum[j] += i;
        }
    }

    /* seen array: 0 = not seen, positive = chain length */
    int *seen = (int *)calloc((size_t)(max_num + 1), sizeof(int));
    if (!seen) {
        fprintf(stderr, "Out of memory\n");
        free(divisor_sum);
        return -1;
    }

    /* in_path array: stores position+1 of node in current path (0 = not in path) */
    int *in_path = (int *)calloc((size_t)(max_num + 1), sizeof(int));
    if (!in_path) {
        fprintf(stderr, "Out of memory\n");
        free(divisor_sum);
        free(seen);
        return -1;
    }

    /* path buffer */
    int *path = (int *)malloc((size_t)(max_num + 1) * sizeof(int));
    if (!path) {
        fprintf(stderr, "Out of memory\n");
        free(divisor_sum);
        free(seen);
        free(in_path);
        return -1;
    }

    int smallest_member = 0;
    int longest_length = 0;

    for (int i = 1; i <= max_num; i++) {
        if (seen[i]) continue;

        /* Walk the chain from i */
        int path_len = 0;
        path[path_len++] = i;
        in_path[i] = path_len; /* position 1-indexed */

        int c = divisor_sum[i];

        while (c >= 1 && c <= max_num && !in_path[c] && !seen[c]) {
            path[path_len++] = c;
            in_path[c] = path_len;
            c = divisor_sum[c];
        }

        /* Check if we closed a cycle back to i */
        if (c == i) {
            /* The entire path is one amicable chain */
            int len_ch = path_len;
            if (len_ch > longest_length) {
                longest_length = len_ch;
                smallest_member = i;
            }
            /* Mark all nodes as seen */
            for (int k = 0; k < path_len; k++) {
                seen[path[k]] = len_ch;
            }
        } else if (c >= 1 && c <= max_num && in_path[c]) {
            /* c is in the current path but not equal to i:
             * the cycle starts at position in_path[c]-1 in the path array */
            int cycle_start_pos = in_path[c] - 1; /* 0-indexed */
            int cycle_len = path_len - cycle_start_pos;

            if (cycle_len > longest_length) {
                longest_length = cycle_len;
                /* smallest member is the minimum in the cycle */
                int min_val = path[cycle_start_pos];
                for (int k = cycle_start_pos + 1; k < path_len; k++) {
                    if (path[k] < min_val) min_val = path[k];
                }
                smallest_member = min_val;
            }
            /* Mark all nodes as seen */
            for (int k = 0; k < path_len; k++) {
                seen[path[k]] = (k >= cycle_start_pos) ? cycle_len : -1;
            }
        } else {
            /* No cycle found; mark all as seen with length -1 (tail only) */
            for (int k = 0; k < path_len; k++) {
                seen[path[k]] = -1;
            }
        }

        /* Clear in_path for all nodes in current path */
        for (int k = 0; k < path_len; k++) {
            in_path[path[k]] = 0;
        }
    }

    free(divisor_sum);
    free(seen);
    free(in_path);
    free(path);

    return (long long)smallest_member;
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

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (has_result && cur != result) {
            fprintf(stderr, "Expected consistent result, got %lld previous result=%lld\n",
                    cur, result);
            rc = 1;
        }
        result = cur;
        has_result = 1;
    }

    free(solve_argv);
    printf("%d %.17g %lld\n", runs, total / (double)runs, result);
    return rc;
}