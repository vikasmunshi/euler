/*******************************************************************************
 * File: p0014.c
 *
 * Description: Implementation of collatz_sequence_length for problem 14.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdint.h>
#include <stdlib.h>

// We implement a recursive Collatz sequence length with memoization.
// The cache stores lengths for inputs up to a fixed bound.
// For values exceeding the bound, the function still works correctly
// (recursively) but without caching those terms.
// Cache size: cache results for n in [0, CACHE_MAX].
// For Project Euler usage (n <= 10^7)
#ifndef P0014_CACHE_MAX
#define P0014_CACHE_MAX 10000000  // 10 million entries (80 MB as int64_t = 10M * 8 bytes).
#endif


static int64_t *g_cache = NULL;
static int64_t g_cache_size = 0;
static int g_cache_initialized = 0;

// Ensure the memoization cache is allocated (idempotent)
void ensure_cache(void) {
    if (g_cache_initialized) return;
    int64_t size = P0014_CACHE_MAX + 1; // include index == size-1
    g_cache = (int64_t *)calloc((size_t)size, sizeof(int64_t));
    if (g_cache) {
        g_cache_size = size;
        g_cache[1] = 1; // base case
    } else {
        // Allocation failed; proceed without cache by leaving pointers NULL
        g_cache_size = 0;
    }
    g_cache_initialized = 1;
}

// Free the memoization cache if allocated (idempotent)
void free_cache(void) {
    if (g_cache) {
        free(g_cache);
        g_cache = NULL;
    }
    g_cache_size = 0;
    g_cache_initialized = 0;
}

static int64_t collatz_recursive(int64_t n) {
    if (n == 1) return 1;

    if (n > 0 && g_cache && n < g_cache_size) {
        int64_t cached = g_cache[n];
        if (cached > 0) return cached;
    }

    int64_t next;
    if ((n & 1) == 0) {
        next = n >> 1;
    } else {
        // 3n + 1; risk of overflow for extremely large n, but our inputs fit in int64_t safely
        next = 3 * n + 1;
    }

    int64_t result = 1 + collatz_recursive(next);

    if (n > 0 && g_cache && n < g_cache_size) {
        g_cache[n] = result;
    }
    return result;
}

// Public API
int64_t collatz_sequence_length(int64_t n) {
    if (n <= 0) return 0;
    return collatz_recursive(n);
}
