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

bool is_prime(uint64_t n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    uint64_t limit = (uint64_t)sqrt((double)n);
    for (uint64_t i = 5; i <= limit; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}

uint64_t *prime_factors(uint64_t n, size_t *size) {
    uint64_t *factors = malloc(64 * sizeof(uint64_t));
    *size = 0;

    while (n % 2 == 0) {
        factors[(*size)++] = 2;
        n = n / 2;
    }

    for (uint64_t i = 3; i <= sqrt(n); i += 2) {
        while (n % i == 0) {
            factors[(*size)++] = i;
            n = n / i;
        }
    }

    if (n > 2) {
        factors[(*size)++] = n;
    }

    return factors;
}

uint64_t next_prime(uint64_t n) {
    if (n <= 1) return 2;

    uint64_t prime = n;
    bool found = false;

    while (!found) {
        prime++;
        if (is_prime(prime)) {
            found = true;
        }
    }

    return prime;
}


int primes_sundaram_sieve(const int max_num, int** primes_out) {
    int max_number = (max_num - 1) / 2;
    char* numbers = (char*)malloc((max_number + 1) * sizeof(char));
    int prime_count = 1;  // Account for number 2 as prime
    int* primes;
    int prime_idx;
    int i, j, index_limit;

    if (!numbers) {
        return -1;  // Memory allocation failed
    }

    // Initialize all as 1 (true)
    for (i = 0; i <= max_number; i++) {
        numbers[i] = 1;
    }

    // Mark non-primes using the Sundaram Sieve logic
    for (i = 1; i <= max_number; i++) {
        index_limit = (max_number - i) / (2 * i + 1);
        for (j = i; j <= index_limit; j++) {
            numbers[i + j + 2 * i * j] = 0;
        }
    }

    // Count primes
    for (i = 1; i <= max_number; i++) {
        if (numbers[i]) {
            prime_count++;
        }
    }

    // Allocate memory for the primes array
    primes = (int*)malloc(prime_count * sizeof(int));
    if (!primes) {
        free(numbers);
        return -1;  // Memory allocation failed
    }

    // Populate primes array
    primes[0] = 2;
    prime_idx = 1;
    for (i = 1; i <= max_number; i++) {
        if (numbers[i]) {
            primes[prime_idx] = 2 * i + 1;
            prime_idx++;
        }
    }

    *primes_out = primes;
    free(numbers);

    return prime_count;  // Return the count of primes
}

/**
 * Generates prime numbers up to max_num using the Sieve of Eratosthenes algorithm.
 * 
 * @param max_num The upper limit for generating prime numbers
 * @param primes_out Pointer to array where prime numbers will be stored
 * @return Number of prime numbers found, or -1 if memory allocation fails
 */
int primes_eratosthenes_sieve(const int max_num, int** primes_out) {
    bool* is_prime = (bool*)malloc((max_num + 1) * sizeof(bool));
    int* primes;
    int prime_count = 0;
    int i, j;

    if (!is_prime) {
        return -1;  // Memory allocation failed
    }

    // Initialize all numbers as prime
    memset(is_prime, true, (max_num + 1) * sizeof(bool));
    is_prime[0] = is_prime[1] = false;

    // Mark non-primes using Sieve of Eratosthenes
    for (i = 2; i * i <= max_num; i++) {
        if (is_prime[i]) {
            for (j = i * i; j <= max_num; j += i) {
                is_prime[j] = false;
            }
        }
    }

    // Count prime numbers
    for (i = 2; i <= max_num; i++) {
        if (is_prime[i]) {
            prime_count++;
        }
    }

    // Allocate memory for prime numbers array
    primes = (int*)malloc(prime_count * sizeof(int));
    if (!primes) {
        free(is_prime);
        return -1;  // Memory allocation failed
    }

    // Store prime numbers in array
    j = 0;
    for (i = 2; i <= max_num; i++) {
        if (is_prime[i]) {
            primes[j++] = i;
        }
    }

    *primes_out = primes;
    free(is_prime);

    return prime_count;
}

