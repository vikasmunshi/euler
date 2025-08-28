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
// To keep the interface simple and avoid exposing cache management to Python,
// we maintain a static cache inside this translation unit. The cache stores
// lengths for inputs up to a fixed bound. For values exceeding the bound, the
// function still works correctly (recursively) but without caching those terms.

// Reasonable default cache size: cache results for n in [0, CACHE_MAX].
// For Project Euler usage (n <= 10^7 when scanning), many recursive calls
// go below 10^7, but using a large static array would bloat the binary.
// We therefore pick a moderate cache size focused on the "hot" region.
#ifndef P0014_CACHE_MAX
#define P0014_CACHE_MAX 10000000  // 10 million entries (80 MB as int64_t) -> too big for many envs.
#endif

// To reduce memory pressure while preserving memoization benefits, we allocate
// the cache dynamically on first use up to a safer default. Override with
// compile-time -DP0014_CACHE_MAX=<value> if needed.
#ifndef P0014_CACHE_MAX_RUNTIME
#define P0014_CACHE_MAX_RUNTIME 2000000  // 2 million entries (~16 MB) safer default
#endif

static int64_t *g_cache = NULL;
static int64_t g_cache_size = 0;
static int g_cache_initialized = 0;

static void ensure_cache(void) {
    if (g_cache_initialized) return;
    int64_t size = P0014_CACHE_MAX_RUNTIME + 1; // include index == size-1
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
    ensure_cache();
    return collatz_recursive(n);
}
