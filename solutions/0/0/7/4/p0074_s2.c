/* Solution to Euler Problem 74: Digit Factorial Chains. */
#include "runner.h"

/* s2 shares the same algorithm as s1 (add_chains with list-based chain lengths),
 * with optional visualization skipped (no ANSI/graphical output in C translation). */

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

/* Identical to s1: walk-and-cache memoization over the digit-factorial functional graph, storing
 * only chain lengths, with cycle detection via a boolean visited_flag cleared per walk through
 * visited_list. The s2 Python sibling adds optional coloured visualisation; that is dropped here.
 * Amortised O(1) per start, O(max_num) total. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);

    int cache_size = 3000000;

    int *chain_length = calloc((size_t)cache_size, sizeof(int));
    if (!chain_length) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int chain_cap = 256;
    int *current_chain = malloc((size_t)chain_cap * sizeof(int));
    char *visited_flag = calloc((size_t)cache_size, sizeof(char));
    if (!current_chain || !visited_flag) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    for (int number = 2; number <= max_num; number++) {
        if (number < cache_size && chain_length[number] != 0) {
            int cl = chain_length[number];
            if (cl > max_chain_length) {
                max_chain_length = cl;
                max_chain_length_count = 1;
            } else if (cl == max_chain_length) {
                max_chain_length_count++;
            }
            continue;
        }

        int chain_len = 0;
        int visited_len = 0;
        int visited_list_cap = 256;
        int *visited_list = malloc((size_t)visited_list_cap * sizeof(int));
        if (!visited_list) {
            fprintf(stderr, "Out of memory\n");
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }

        int num = number;
        int hit_cached = 0;
        int cached_length = 0;

        /* Walk until a cycle (visited_flag set) or a cached node (whose length is the tail). */
        while (1) {
            int in_visited = (num < cache_size) ? visited_flag[num] : 0;
            if (in_visited) {
                break;
            }
            if (num < cache_size && chain_length[num] != 0) {
                hit_cached = 1;
                cached_length = chain_length[num];
                break;
            }

            if (chain_len >= chain_cap) {
                chain_cap *= 2;
                current_chain = realloc(current_chain, (size_t)chain_cap * sizeof(int));
                if (!current_chain) {
                    fprintf(stderr, "Out of memory\n");
                    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
                }
            }
            current_chain[chain_len++] = num;

            if (num < cache_size) {
                visited_flag[num] = 1;
                if (visited_len >= visited_list_cap) {
                    visited_list_cap *= 2;
                    visited_list = realloc(visited_list, (size_t)visited_list_cap * sizeof(int));
                    if (!visited_list) {
                        fprintf(stderr, "Out of memory\n");
                        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
                    }
                }
                visited_list[visited_len++] = num;
            }

            num = sum_of_digit_factorials(num);
        }

        for (int i = 0; i < visited_len; i++) {
            visited_flag[visited_list[i]] = 0;
        }
        free(visited_list);

        int total_length = hit_cached ? (chain_len + cached_length) : chain_len;

        /* Assign chain lengths back: position i sits i steps along the chain. */
        for (int i = 0; i < chain_len; i++) {
            int val = current_chain[i];
            if (val < cache_size && chain_length[val] == 0) {
                chain_length[val] = total_length - i;
            }
        }

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

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)max_chain_length_count)); return _answer; }
}