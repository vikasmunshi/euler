/*******************************************************************************
 * File: p0078.c
 *
 * Description:
 *   C implementation for Project Euler Problem 78 helper function.
 *   Computes the least n such that the partition number p(n) is divisible
 *   by a given divisor, using Euler's pentagonal number theorem.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/

#include <stdlib.h>
#include <stdint.h>

/*
 * Compute the least n such that p(n) % divisor == 0.
 * Returns -1 on unexpected failure (e.g., allocation issues should be rare).
 *
 * The implementation stores partition values modulo 'divisor' to keep values
 * bounded in 32-bit int. Algorithmic complexity is roughly O(n * sqrt(n)).
 */
int least_number_with_partitions_divisible_by(int divisor) {
    if (divisor <= 0) {
        return -1;
    }

    // Dynamic array for partitions modulo divisor: p(0) = 1
    int capacity = 1024;
    int size = 1; // currently stored up to index 0
    int *p = (int *)malloc((size_t)capacity * sizeof(int));
    if (!p) {
        return -1;
    }
    p[0] = 1 % divisor;

    for (int n = 1; ; ++n) {
        // Ensure capacity
        if (n >= capacity) {
            int new_capacity = capacity * 2;
            int *np = (int *)realloc(p, (size_t)new_capacity * sizeof(int));
            if (!np) {
                free(p);
                return -1;
            }
            p = np;
            capacity = new_capacity;
        }
        if (n >= size) {
            size = n + 1;
        }

        long long total = 0; // accumulate in wider type to avoid intermediate overflow
        int sign = 1;         // pattern: +, +, -, -, +, +, ... per k step

        for (int k = 1; ; ++k) {
            // generalized pentagonal numbers
            // g1 = k*(3k-1)/2, g2 = k*(3k+1)/2
            int g1 = k * (3 * k - 1) / 2;
            if (g1 > n) {
                break;
            }
            int idx1 = n - g1;
            total += sign * (long long)p[idx1];

            int g2 = k * (3 * k + 1) / 2;
            if (g2 <= n) {
                int idx2 = n - g2;
                total += sign * (long long)p[idx2];
            }

            sign = -sign; // flip sign after the pair
        }

        int value = (int)(total % divisor);
        if (value < 0) value += divisor; // ensure non-negative modulo
        p[n] = value;

        if (value == 0) {
            free(p);
            return n;
        }
    }

    // Unreachable, but for completeness
    free(p);
    return -1;
}
