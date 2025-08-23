/*******************************************************************************
 * File: digit_factorial_chains.c
 *
 * Description: Implementation of digit factorial chains calculator that finds
 *              chains where the sum of factorial of digits leads to loops.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#include "digit_factorial_chains.h"

static const int DIGIT_FACTORIALS[10] = {
    1,        // 0!
    1,        // 1!
    2,        // 2!
    6,        // 3!
    24,       // 4!
    120,      // 5!
    720,      // 6!
    5040,     // 7!
    40320,    // 8!
    362880    // 9!
};

static inline int sum_of_digit_factorials_int(int n) {
    int result = 0;
    while (n > 0) {
        result += DIGIT_FACTORIALS[n % 10];
        n /= 10;
    }
    return result;
}

/* Compute maximum possible value reachable from numbers up to max_num. */
static int max_reachable_value(int max_num) {
    if (max_num < 10) {
        return 9 * DIGIT_FACTORIALS[9];
    }
    int digits = 0;
    int temp = max_num;
    while (temp > 0) {
        digits++;
        temp /= 10;
    }
    long long max_val = (long long)digits * (long long)DIGIT_FACTORIALS[9];
    if (max_val < max_num) {
        return max_num; // cache at least up to max_num
    }
    if (max_val > INT_MAX - 1) {
        return INT_MAX - 1; // avoid overflow
    }
    return (int)max_val;
}

int count_digit_factorial_max_length_chains(int max_num,
                                            int *out_max_chain_length,
                                            int *out_max_chain_length_count) {
    if (!out_max_chain_length || !out_max_chain_length_count) {
        return 1;
    }
    if (max_num < 2) {
        *out_max_chain_length = 0;
        *out_max_chain_length_count = 0;
        return 0;
    }

    int cache_limit = max_reachable_value(max_num);
    int cache_size = cache_limit + 1;

    int *chain_length_cache = (int *)calloc((size_t)cache_size, sizeof(int));
    if (!chain_length_cache) {
        return 2;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    // workspace for seen chain, grow as needed
    int seen_capacity = 64;
    int *seen = (int *)malloc((size_t)seen_capacity * sizeof(int));
    if (!seen) {
        free(chain_length_cache);
        return 3;
    }

    for (int start = 2; start <= max_num; ++start) {
        int seen_count = 0;
        int current = start;

        // Walk the chain until repeat or a cached value is found
        while (1) {
            // If current exceeds cache, extend cache? It shouldn't if cache_limit computed properly,
            // but guard anyway by computing directly without caching for out-of-range values.
            int cached_len = (current < cache_size) ? chain_length_cache[current] : 0;

            // Check if current already in seen
            int in_seen_index = -1;
            for (int i = 0; i < seen_count; ++i) {
                if (seen[i] == current) { in_seen_index = i; break; }
            }
            if (in_seen_index != -1 || cached_len > 0) {
                int length;
                if (cached_len > 0) {
                    length = seen_count + cached_len;
                } else {
                    // loop detected within seen: length is number of non-repeating terms
                    length = seen_count;
                }
                // Propagate lengths back to all numbers in seen
                for (int i = 0; i < seen_count; ++i) {
                    int num = seen[i];
                    int val = length - i;
                    if (num < cache_size && chain_length_cache[num] == 0) {
                        chain_length_cache[num] = val;
                    }
                }
                int chain_length_start = (start < cache_size) ? chain_length_cache[start] : length;
                if (chain_length_start > max_chain_length) {
                    max_chain_length = chain_length_start;
                    max_chain_length_count = 1;
                } else if (chain_length_start == max_chain_length) {
                    max_chain_length_count += 1;
                }
                break;
            }

            // append current to seen
            if (seen_count == seen_capacity) {
                int new_cap = seen_capacity * 2;
                int *tmp = (int *)realloc(seen, (size_t)new_cap * sizeof(int));
                if (!tmp) {
                    free(seen);
                    free(chain_length_cache);
                    return 4;
                }
                seen = tmp;
                seen_capacity = new_cap;
            }
            seen[seen_count++] = current;
            current = sum_of_digit_factorials_int(current);
        }
    }

    free(seen);
    *out_max_chain_length = max_chain_length;
    *out_max_chain_length_count = max_chain_length_count;

    free(chain_length_cache);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <max_num>\n", argv[0]);
        return 1;
    }
    char *endptr = NULL;
    long val = strtol(argv[1], &endptr, 10);
    if (endptr == argv[1] || val <= 0 || val > INT_MAX) {
        fprintf(stderr, "Invalid max_num: %s\n", argv[1]);
        return 2;
    }
    int max_num = (int)val;

    int max_chain_length = 0;
    int max_chain_length_count = 0;
    int rc = count_digit_factorial_max_length_chains(max_num, &max_chain_length, &max_chain_length_count);
    if (rc != 0) {
        fprintf(stderr, "Error computing chains (rc=%d)\n", rc);
        return rc;
    }
    printf("max_num=%d max_chain_length=%d max_chain_length_count=%d\n", max_num, max_chain_length, max_chain_length_count);
    return 0;
}
