/*******************************************************************************
 * File: p0074.c
 *
 * Description: Implementation of digit factorial chains calculator that finds
 *              chains where the sum of factorial of digits leads to loops.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>

#define ERROR_NULL_OUTPUT_PTRS 1
#define ERROR_MEMORY_ALLOCATION_CACHE 2
#define ERROR_MEMORY_ALLOCATION_SEEN 3
#define ERROR_MEMORY_REALLOCATION_SEEN 4

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

// Function to clean up dynamically allocated memory
static void cleanup(int *chain_length_cache, int *seen) {
    if (chain_length_cache) free(chain_length_cache);
    if (seen) free(seen);
}

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
        return DIGIT_FACTORIALS[9];
    }
    int digits = 0;
    int temp = max_num;
    while (temp > 0) {
        digits++;
        temp /= 10;
    }
    int max_val = digits * DIGIT_FACTORIALS[9]; // for numbers with 7 or more digits, this is less than the number
    return (max_val < max_num) ? max_num : max_val;
}

int count_digit_factorial_max_length_chains(int max_num,
                                            int *out_max_chain_length,
                                            int *out_max_chain_length_count) {
    if (!out_max_chain_length || !out_max_chain_length_count) {
        return ERROR_NULL_OUTPUT_PTRS;
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
        return ERROR_MEMORY_ALLOCATION_CACHE;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    // workspace for seen chain, grow as needed
    int seen_capacity = 64;
    int *seen = (int *)malloc((size_t)seen_capacity * sizeof(int));
    if (!seen) {
        free(chain_length_cache);
        return ERROR_MEMORY_ALLOCATION_SEEN;
    }
    bool *seen_bitmap = (bool *)calloc((size_t)cache_size, sizeof(bool));
    if (!seen_bitmap) {
        cleanup(chain_length_cache, seen);
        return ERROR_MEMORY_ALLOCATION_SEEN;
    }

    for (int start = 2; start <= max_num; ++start) {
        int seen_count = 0;
        int current = start;

        // Walk the chain until repeat or a cached value is found
        while (1) {
            int cached_len = (current < cache_size) ? chain_length_cache[current] : 0;

            // Check if current already in seen (using bitmap for optimization)
            if ((current < cache_size && seen_bitmap[current]) || cached_len > 0) {
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
                    cleanup(chain_length_cache, seen);
                    free(seen_bitmap);
                    return ERROR_MEMORY_REALLOCATION_SEEN;
                }
                seen = tmp;
                seen_capacity = new_cap;
            }
            seen[seen_count++] = current;
            if (current < cache_size) {
                seen_bitmap[current] = true;
            }
            current = sum_of_digit_factorials_int(current);
        }

        // Reset seen_bitmap for this iteration
        for (int i = 0; i < seen_count; ++i) {
            if (seen[i] < cache_size) {
                seen_bitmap[seen[i]] = false;
            }
        }
    }

    free(seen);
    free(seen_bitmap);
    *out_max_chain_length = max_chain_length;
    *out_max_chain_length_count = max_chain_length_count;

    free(chain_length_cache);
    return 0;
}