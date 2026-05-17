/* Solution to Euler Problem 74: Digit Factorial Chains. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static const int digit_factorials[10] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

static int sum_of_digit_factorials(int n) {
    int result = 0;
    while (n > 0) {
        result += digit_factorials[n % 10];
        n /= 10;
    }
    return result;
}

long long solve(int argc, char *argv[]) {
    int max_num = atoi(argv[1]);

    /* We need a cache for chain lengths and graph (next number).
     * Numbers reachable from [1..max_num] are at most 6*9! = 2177280 for 7-digit numbers.
     * We'll use a hash map approach with open addressing. */

    /* Max reachable value: sum of digit factorials of any number up to 10M is at most 7*362880=2540160.
     * Use cache size of 3000000 to be safe. */
    int cache_size = 3000000;
    int *chain_length_cache = calloc((size_t)cache_size, sizeof(int));
    int *graph = calloc((size_t)cache_size, sizeof(int));
    if (!chain_length_cache || !graph) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }
    /* 0 means not cached */

    /* seen list for the walk */
    int seen_capacity = 200;
    int *seen = malloc((size_t)seen_capacity * sizeof(int));
    if (!seen) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    for (int start = 2; start <= max_num; start++) {
        int seen_len = 0;
        int current = start;

        /* Walk forward until we hit a cached node or revisit a node in this walk.
         * We need to detect cycles in the current walk using a small lookup.
         * Since chain lengths are bounded (~60), a linear scan is fine. */
        while (1) {
            /* Check if current is in seen (cycle detection) */
            int in_seen = 0;
            for (int i = 0; i < seen_len; i++) {
                if (seen[i] == current) {
                    in_seen = 1;
                    break;
                }
            }
            if (in_seen) break;

            /* Check if current is in cache */
            if (current < cache_size && chain_length_cache[current] != 0) break;

            /* Add to seen */
            if (seen_len >= seen_capacity) {
                seen_capacity *= 2;
                seen = realloc(seen, (size_t)seen_capacity * sizeof(int));
                if (!seen) {
                    fprintf(stderr, "Out of memory\n");
                    return -1;
                }
            }
            seen[seen_len++] = current;

            /* Compute next if not in graph */
            if (current < cache_size && graph[current] == 0) {
                graph[current] = sum_of_digit_factorials(current);
            }
            if (current < cache_size) {
                current = graph[current];
            } else {
                current = sum_of_digit_factorials(current);
            }
        }

        /* Determine length */
        int length;
        if (current < cache_size && chain_length_cache[current] != 0) {
            length = seen_len + chain_length_cache[current];
        } else {
            /* cycle: current is in seen */
            length = seen_len;
        }

        /* Back-propagate */
        for (int i = 0; i < seen_len; i++) {
            int num = seen[i];
            if (num < cache_size) {
                chain_length_cache[num] = length - i;
                /* graph[num] already set or set it now */
                if (graph[num] == 0) {
                    graph[num] = (i + 1 < seen_len) ? seen[i + 1] : current;
                }
            }
        }

        /* Check start's chain length */
        int cl = (start < cache_size) ? chain_length_cache[start] : length;
        if (cl > max_chain_length) {
            max_chain_length = cl;
            max_chain_length_count = 1;
        } else if (cl == max_chain_length) {
            max_chain_length_count++;
        }
    }

    free(chain_length_cache);
    free(graph);
    free(seen);

    return (long long)max_chain_length_count;
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