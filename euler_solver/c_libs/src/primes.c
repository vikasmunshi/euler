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

