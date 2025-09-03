/*******************************************************************************
 * File: p0097.c
 *
 * Description: C implementation for Project Euler problem 97 (Large non-Mersenne prime).
 * Exports a function usable via ctypes from Python.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>

// Public API (ctypes):
// long long large_non_mersenne_prime(int num_digits, const char* prime)
// prime format example: "28433 × 2^7830457 + 1" or "28433 x 2^7830457 + 1"

static long long pow10_ll(int n) {
    long long v = 1;
    for (int i = 0; i < n; ++i) {
        if (v > 0 && v > LLONG_MAX / 10) {
            return 0; // overflow signal
        }
        v *= 10;
    }
    return v;
}

// Fast modular exponentiation: compute (base^exp) mod mod
static long long mod_pow_ll(long long base, long long exp, long long mod) {
    if (mod <= 1) return 0;
    long long res = 1 % mod;
    long long b = base % mod;
    while (exp > 0) {
        if (exp & 1LL) {
            res = (long long)((__int128)res * (__int128)b % (__int128)mod);
        }
        b = (long long)((__int128)b * (__int128)b % (__int128)mod);
        exp >>= 1LL;
    }
    return res;
}

// Parse leading integer A, then find "2^" and parse exponent B
static int parse_A_B(const char* s, long long* A_out, long long* B_out) {
    if (!s || !A_out || !B_out) return 1;

    // Skip leading spaces
    while (*s && isspace((unsigned char)*s)) ++s;

    // Parse A
    long long A = 0;
    int any = 0;
    while (*s && isdigit((unsigned char)*s)) {
        any = 1;
        int d = *s - '0';
        if (A > LLONG_MAX / 10) return 2; // overflow
        A = A * 10 + d;
        ++s;
    }
    if (!any) return 3; // no leading integer

    // Find substring "2^"
    const char* p = s;
    const char* two_pow = NULL;
    while (*p) {
        if (p[0] == '2' && p[1] == '^') { two_pow = p; break; }
        ++p;
    }
    if (!two_pow) return 4;

    // Parse B after "2^"
    p = two_pow + 2;
    while (*p && isspace((unsigned char)*p)) ++p;
    long long B = 0;
    any = 0;
    while (*p && isdigit((unsigned char)*p)) {
        any = 1;
        int d = *p - '0';
        if (B > LLONG_MAX / 10) return 5; // overflow
        B = B * 10 + d;
        ++p;
    }
    if (!any) return 6;

    *A_out = A;
    *B_out = B;
    return 0;
}

long long large_non_mersenne_prime(int num_digits, const char* prime) {
    if (num_digits <= 0 || !prime) return -1;
    long long A = 0, B = 0;
    int rc = parse_A_B(prime, &A, &B);
    if (rc != 0) return -(rc);

    long long mod = pow10_ll(num_digits);
    if (mod <= 1) return -7; // invalid num_digits or overflow

    long long pow2 = mod_pow_ll(2, B, mod);
    long long part = (long long)((__int128)(A % mod) * (__int128)pow2 % (__int128)mod);
    long long result = part + 1;
    if (result >= mod) result -= mod;
    return result;
}

