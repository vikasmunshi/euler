/* Solution to Euler Problem 74: Digit Factorial Chains. */
#include "runner.h"

static const int digit_factorials[10] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

/* Successor under the digit-factorial map: sum of factorials of n's decimal digits. */
static int sum_of_digit_factorials(int n) {
    int result = 0;
    while (n > 0) {
        result += digit_factorials[n % 10];
        n /= 10;
    }
    return result;
}

/* Walk-and-cache memoization over the digit-factorial functional graph: from each start, walk
 * forward until hitting a node with a known chain length or closing a cycle, then back-propagate
 * the length to every node on the walk (seen[i] gets total - i). A flat array of 3,000,000 slots
 * caches chain lengths and successors, since every reachable value stays below 7*9! = 2540160.
 * Amortised O(1) per start, so O(max_num) overall. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);

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
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    /* 0 means not cached */

    /* seen list for the walk */
    int seen_capacity = 200;
    int *seen = malloc((size_t)seen_capacity * sizeof(int));
    if (!seen) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    for (int start = 2; start <= max_num; start++) {
        int seen_len = 0;
        int current = start;

        /* Walk forward until we hit a cached node or revisit a node in this walk.
         * Cycle detection uses a linear scan of seen; chain lengths are bounded near 60,
         * so this constant-bounded scan beats the overhead of a hash set. */
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
                    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
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

        /* Chain length: walk length plus the cached tail, or just the walk if we closed a cycle. */
        int length;
        if (current < cache_size && chain_length_cache[current] != 0) {
            length = seen_len + chain_length_cache[current];
        } else {
            /* cycle: current is in seen */
            length = seen_len;
        }

        /* Back-propagate: seen[i] is i steps along the same chain, so its length is total - i. */
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

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)max_chain_length_count)); return _answer; }
}