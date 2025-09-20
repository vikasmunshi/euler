/*******************************************************************************
 * File: p0095.c
 *
 * Description: C implementation for Project Euler problem 95 (Amicable Chains).
 * Exports a function usable via ctypes from Python.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdlib.h>
#include <string.h>

// Public C API (ctypes):
// void longest_amicable_chain(int max_num, int* out_length, int* out_smallest)
// - max_num: inclusive upper bound
// - out_length: output for the length of the longest amicable chain
// - out_smallest: output for the smallest member (starting point) of that chain
// Notes:
//   - If multiple chains have the same maximum length, the first found starting
//     index is returned (consistent with scanning from 1..max_num).
//   - If no amicable chain exists (should not happen for reasonable inputs),
//     outputs are set to 0.

static int* make_int_array(size_t n) {
    int* p = (int*)malloc(n * sizeof(int));
    if (p) memset(p, 0, n * sizeof(int));
    return p;
}

void longest_amicable_chain(int max_num, int* out_length, int* out_smallest) {
    if (out_length) *out_length = 0;
    if (out_smallest) *out_smallest = 0;
    if (max_num <= 1 || !out_length || !out_smallest) return;

    const int N = max_num;

    // Sieve: sum of proper divisors for 0..N
    int* divsum = make_int_array((size_t)N + 1);
    if (!divsum) return;

    for (int i = 1; i <= N / 2; ++i) {
        for (int j = i * 2; j <= N; j += i) {
            divsum[j] += i;
        }
    }

    // seen: 0 = unseen; >0 = chain length for nodes confirmed to be in a cycle
    int* seen = make_int_array((size_t)N + 1);
    if (!seen) { free(divsum); return; }

    // local in-chain flags reused per start; we only touch entries we add to path and then clear them
    unsigned char* in_chain = (unsigned char*)malloc((size_t)N + 1);
    if (!in_chain) { free(seen); free(divsum); return; }
    memset(in_chain, 0, (size_t)N + 1);

    // dynamic path buffer
    int cap = 64;
    int* path = (int*)malloc((size_t)cap * sizeof(int));
    if (!path) { free(in_chain); free(seen); free(divsum); return; }

    int best_len = 0;
    int best_smallest = 0;

    for (int i = 1; i <= N; ++i) {
        if (seen[i] != 0) continue;

        int len = 0;
        // reset path for this start
        int path_len = 0;

        // start chain
        int c = divsum[i];

        // push i
        if (path_len >= cap) {
            int new_cap = cap * 2;
            int* np = (int*)realloc(path, (size_t)new_cap * sizeof(int));
            if (!np) { // bail out safely
                free(path); free(in_chain); free(seen); free(divsum); return;
            }
            path = np; cap = new_cap;
        }
        path[path_len++] = i;
        in_chain[i] = 1;

        while (c >= i && c <= N && !in_chain[c]) {
            if (path_len >= cap) {
                int new_cap = cap * 2;
                int* np = (int*)realloc(path, (size_t)new_cap * sizeof(int));
                if (!np) { free(path); free(in_chain); free(seen); free(divsum); return; }
                path = np; cap = new_cap;
            }
            path[path_len++] = c;
            in_chain[c] = 1;
            c = divsum[c];
        }

        if (c == i) {
            len = path_len;
            if (len > best_len) {
                best_len = len;
                best_smallest = i;
            }
            // mark all visited in this path with chain length
            for (int k = 0; k < path_len; ++k) {
                int x = path[k];
                seen[x] = len;
                in_chain[x] = 0; // clear for reuse
            }
        } else {
            // No cycle equal to start; do not mark seen so future starts can be evaluated like Python version
            for (int k = 0; k < path_len; ++k) {
                int x = path[k];
                in_chain[x] = 0;
            }
        }
    }

    *out_length = best_len;
    *out_smallest = best_smallest;

    free(path);
    free(in_chain);
    free(seen);
    free(divsum);
}

