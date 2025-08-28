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

// Compute Collatz sequence length for a positive integer n.
// Returns the number of terms including n and ending at 1.
// For n==1 -> 1; for n>1 iterative rules apply. Uses 64-bit to avoid overflow.
int64_t collatz_sequence_length(int64_t n) {
    if (n <= 0) {
        return 0; // treat non-positive as invalid
    }
    int64_t length = 1;
    while (n != 1) {
        if ((n & 1) == 0) {
            n = n >> 1;
        } else {
            // 3n+1, guard against potential overflow by using unsigned __int128 if available
            // but since we compile as C, rely on 64-bit; inputs in our usage are <= 10^7
            n = 3 * n + 1;
        }
        length += 1;
    }
    return length;
}
