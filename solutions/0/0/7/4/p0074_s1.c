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

/* We store for each number the chain length only (derived from the list-length approach).
 * This faithfully mirrors s1's logic: build a current_chain list, extend with cached chain,
 * detect cycles, then assign each position its chain length. */

long long solve(int argc, char *argv[]) {
    int max_num = atoi(argv[1]);

    /* Max cache size: any number up to 10M maps to at most 7*362880=2540160 */
    int cache_size = 3000000;

    /* chain_length[n] = length of chain starting at n (0 = not set) */
    int *chain_length = calloc((size_t)cache_size, sizeof(int));
    if (!chain_length) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    /* current_chain: dynamically sized array */
    int chain_cap = 256;
    int *current_chain = malloc((size_t)chain_cap * sizeof(int));
    /* visited set for cycle detection: use a small boolean array indexed by position in chain */
    /* We'll use a hash set for visited since values can be large */
    /* Actually values stay < cache_size, so use a boolean array */
    char *visited_flag = calloc((size_t)cache_size, sizeof(char));
    if (!current_chain || !visited_flag) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    for (int number = 2; number <= max_num; number++) {
        if (number < cache_size && chain_length[number] != 0) {
            /* already cached; update max */
            int cl = chain_length[number];
            if (cl > max_chain_length) {
                max_chain_length = cl;
                max_chain_length_count = 1;
            } else if (cl == max_chain_length) {
                max_chain_length_count++;
            }
            continue;
        }

        /* Build current_chain like the Python s1 add_chains:
         * Walk from number, collecting into current_chain until:
         *   - we hit a node in visited (cycle), OR
         *   - we hit a node already in chain_length cache (extend with cached length)
         */
        int chain_len = 0;
        int visited_len = 0; /* track which entries we set in visited_flag */
        /* We'll track visited nodes in a small list to clear visited_flag afterwards */
        int visited_list_cap = 256;
        int *visited_list = malloc((size_t)visited_list_cap * sizeof(int));
        if (!visited_list) {
            fprintf(stderr, "Out of memory\n");
            return -1;
        }

        int num = number;
        int hit_cached = 0;   /* did we stop because of a cache hit? */
        int cached_length = 0;
        int hit_visited = 0;  /* did we stop because of a cycle? */
        int cycle_entry = -1; /* value where cycle was detected */

        while (1) {
            int in_visited = (num < cache_size) ? visited_flag[num] : 0;
            if (in_visited) {
                hit_visited = 1;
                cycle_entry = num;
                break;
            }
            if (num < cache_size && chain_length[num] != 0) {
                hit_cached = 1;
                cached_length = chain_length[num];
                /* Extend current_chain with the cached tail length (not actual values needed) */
                /* In Python, it does current_chain.extend(chains[num]) which appends the
                 * actual chain list. We only need lengths, so we record that the tail
                 * contributes cached_length entries. */
                break;
            }

            /* Add num to current_chain */
            if (chain_len >= chain_cap) {
                chain_cap *= 2;
                current_chain = realloc(current_chain, (size_t)chain_cap * sizeof(int));
                if (!current_chain) {
                    fprintf(stderr, "Out of memory\n");
                    return -1;
                }
            }
            current_chain[chain_len++] = num;

            /* Mark visited */
            if (num < cache_size) {
                visited_flag[num] = 1;
                if (visited_len >= visited_list_cap) {
                    visited_list_cap *= 2;
                    visited_list = realloc(visited_list, (size_t)visited_list_cap * sizeof(int));
                    if (!visited_list) {
                        fprintf(stderr, "Out of memory\n");
                        return -1;
                    }
                }
                visited_list[visited_len++] = num;
            }

            num = sum_of_digit_factorials(num);
        }

        /* Clear visited flags */
        for (int i = 0; i < visited_len; i++) {
            visited_flag[visited_list[i]] = 0;
        }
        free(visited_list);

        /* Compute total chain length from current_chain + tail.
         * In Python s1:
         *   if hit_cached: current_chain was extended by chains[num] (length = cached_length)
         *     total length of current_chain = chain_len + cached_length
         *   if hit_visited (cycle): loop_start = len(current_chain) - len(visited)
         *     but we don't track len(visited) separately from chain_len in the same way.
         *
         * In Python, visited is a set of nodes visited in this walk (same as current_chain nodes
         * before the cache extend). At cycle detection: visited has chain_len members.
         * loop_start = chain_len - chain_len = 0? No wait:
         *   The Python visited set grows as we walk. When we hit a cycle (num in visited),
         *   visited has chain_len entries (all entries currently in current_chain before extension).
         *   loop_start = len(current_chain) - len(visited) = chain_len - chain_len = 0.
         *   But that seems wrong. Let me re-read...
         *
         * Actually in Python s1:
         *   visited is a set; current_chain is a list.
         *   When num in chains (cached): we extend current_chain with chains[num].
         *     Then loop_start is irrelevant (num not in visited).
         *   When num in visited (cycle): loop_start = len(current_chain) - len(visited).
         *     At this point current_chain has chain_len items, visited has chain_len items
         *     (same nodes). So loop_start = 0.
         *   Then: chains[val] = current_chain[i:] for all i.
         *   So chains[val] has length (total_chain_len - i).
         *
         * Total chain length:
         *   hit_cached: total = chain_len + cached_length
         *   hit_visited: total = chain_len (the cycle is wholly within current_chain)
         */

        int total_length;
        if (hit_cached) {
            total_length = chain_len + cached_length;
        } else {
            /* hit_visited: cycle wholly in current_chain */
            total_length = chain_len;
        }

        /* Assign chain lengths back */
        for (int i = 0; i < chain_len; i++) {
            int val = current_chain[i];
            if (val < cache_size && chain_length[val] == 0) {
                chain_length[val] = total_length - i;
            }
        }

        /* Get chain length for 'number' */
        int cl = (number < cache_size) ? chain_length[number] : total_length;
        if (cl > max_chain_length) {
            max_chain_length = cl;
            max_chain_length_count = 1;
        } else if (cl == max_chain_length) {
            max_chain_length_count++;
        }
    }

    free(chain_length);
    free(current_chain);
    free(visited_flag);

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