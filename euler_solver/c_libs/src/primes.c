/*******************************************************************************
 * File: primes.c
 *
 * Description: Implementation of various prime number related functions including
 *             primality testing, prime factorization, prime number generation
 *             using different algorithms like trial division and Sundaram sieve.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define ERROR_MEMORY_ALLOCATION -1

bool is_prime(uint64_t n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    // Calculate the upper limit for trial division
    uint64_t limit = (uint64_t)sqrt((double)n);

    // Check divisors of the form 6k ± 1, starting from 5
    for (uint64_t i = 5; i <= limit; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}

int primes_sundaram_sieve(const uint64_t max_num, uint64_t* primes_out) {
    if (max_num < 2) {
        return 0;  // No primes below 2
    }

    // Sundaram sieve works on odd numbers up to max_num
    uint64_t max_number = (max_num - 1) / 2;  // number of indices for odd numbers
    char* numbers = (char*)malloc((size_t)(max_number + 1) * sizeof(char));
    if (!numbers) {
        return ERROR_MEMORY_ALLOCATION;  // Memory allocation failed
    }

    // Initialize all as 1 (true)
    for (uint64_t i = 0; i <= max_number; i++) {
        numbers[i] = 1;
    }

    // Mark non-primes using the Sundaram Sieve logic
    for (uint64_t i = 1; i <= max_number; i++) {
        uint64_t denom = 2 * i + 1;
        uint64_t index_limit = (max_number - i) / denom;
        for (uint64_t j = i; j <= index_limit; j++) {
            numbers[i + j + 2 * i * j] = 0;
        }
    }

    // Populate output array with computed prime numbers
    int prime_idx = 0;
    primes_out[prime_idx++] = 2;  // The number 2 is the only even prime

    for (uint64_t i = 1; i <= max_number; i++) {
        if (numbers[i]) {
            uint64_t p = 2 * i + 1;  // Convert index back to the original number
            if (p <= max_num) {
                primes_out[prime_idx++] = p;
            }
        }
    }

    free(numbers);
    return prime_idx;  // Return the count of primes written
}

int primes_eratosthenes_sieve(const uint64_t max_num, uint64_t* primes_out) {
    if (max_num < 2) {
        return 0;  // No primes below 2
    }

    // Sieve array for primality up to max_num
    size_t sieve_size = (size_t)(max_num + 1);
    bool* sieve = (bool*)malloc(sieve_size * sizeof(bool));
    if (!sieve) {
        return ERROR_MEMORY_ALLOCATION;  // Memory allocation failed
    }

    // Initialize all numbers as prime
    memset(sieve, true, sieve_size * sizeof(bool));
    sieve[0] = false;
    sieve[1] = false;

    // Mark non-primes using Sieve of Eratosthenes
    for (uint64_t i = 2; i <= max_num / i; i++) {
        if (sieve[i]) {
            uint64_t start = i * i;
            for (uint64_t j = start; j <= max_num; j += i) {
                sieve[j] = false;
            }
        }
    }

    // Store prime numbers in the provided output buffer
    int count = 0;
    for (uint64_t i = 2; i <= max_num; i++) {
        if (sieve[i]) {
            primes_out[count++] = i;
        }
    }

    free(sieve);
    return count;
}

// ---------------- Indefinite prime generator (incremental trial division) ----------------
// We expose a small C API to be used from Python via ctypes:
//   void* primes_generator_init();
//   bool primes_generator_next(void* state, uint64_t* out_prime);
//   void primes_generator_free(void* state);
// The implementation keeps a dynamic array of discovered primes and tests the next
// candidate by trial division up to sqrt(n) (checked via p <= n/p to avoid overflow).
// While not a strict sieve data-structure, it provides an efficient indefinite generator
// without unbounded memory structures and keeps changes minimal.

typedef struct {
    uint64_t current;      // next candidate to test (2 first, then odd numbers)
    uint64_t* primes;      // dynamic array of known primes
    size_t count;          // number of primes stored
    size_t capacity;       // allocated capacity of the primes array
} prime_gen_state_t;

static bool ensure_capacity(prime_gen_state_t* st) {
    if (st->count < st->capacity) return true;
    size_t new_cap = (st->capacity == 0) ? 16 : st->capacity * 2;
    uint64_t* new_arr = (uint64_t*)realloc(st->primes, new_cap * sizeof(uint64_t));
    if (!new_arr) return false;
    st->primes = new_arr;
    st->capacity = new_cap;
    return true;
}

void* primes_generator_init(void) {
    prime_gen_state_t* st = (prime_gen_state_t*)calloc(1, sizeof(prime_gen_state_t));
    if (!st) return NULL;
    st->current = 2;
    st->primes = NULL;
    st->count = 0;
    st->capacity = 0;
    return (void*)st;
}

bool primes_generator_next(void* state, uint64_t* out_prime) {
    if (!state || !out_prime) return false;
    prime_gen_state_t* st = (prime_gen_state_t*)state;

    while (1) {
        uint64_t n = st->current;
        if (n < 2) {
            // overflow wrap or invalid state
            return false;
        }

        // Special-case even starting point
        if (n == 2) {
            if (!ensure_capacity(st)) return false;
            st->primes[st->count++] = 2;
            *out_prime = 2;
            st->current = 3;  // next candidate
            return true;
        }

        // Skip even numbers
        if ((n & 1ull) == 0ull) {
            if (n == UINT64_MAX) return false;  // can't increment further
            st->current = n + 1;
            continue;
        }

        bool is_p = true;
        for (size_t i = 0; i < st->count; ++i) {
            uint64_t p = st->primes[i];
            if (p > 0 && p > n / p) break;  // p*p > n
            if (n % p == 0ull) { is_p = false; break; }
        }
        if (is_p) {
            if (!ensure_capacity(st)) return false;
            st->primes[st->count++] = n;
            *out_prime = n;
            if (n >= UINT64_MAX - 2) {
                st->current = UINT64_MAX; // next step will fail gracefully
            } else {
                st->current = n + 2;  // step through odd numbers
            }
            return true;
        }

        if (n == UINT64_MAX - 1) return false;
        st->current = n + 2;  // try next odd
    }
}

void primes_generator_free(void* state) {
    if (!state) return;
    prime_gen_state_t* st = (prime_gen_state_t*)state;
    if (st->primes) free(st->primes);
    free(st);
}

