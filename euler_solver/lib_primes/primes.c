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
#define ERROR_INSUFFICIENT_BUFFER -2

// ---------------- Trial Division Primality Test ----------------
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

// ---------------- Fast deterministic Miller–Rabin for 64-bit ----------------
static inline uint64_t mulmod_u64(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)((__uint128_t)a * b % mod);
}

static uint64_t powmod_u64(uint64_t a, uint64_t e, uint64_t mod) {
    uint64_t result = 1 % mod;
    uint64_t base = a % mod;
    while (e) {
        if (e & 1ull) result = mulmod_u64(result, base, mod);
        base = mulmod_u64(base, base, mod);
        e >>= 1ull;
    }
    return result;
}

bool fast_is_prime(uint64_t n) {
    if (n < 2) return false;

    // Quick checks for small primes and divisibility
    static const uint64_t small_primes[] = {2ull,3ull,5ull,7ull,11ull,13ull,17ull,19ull,23ull,29ull,31ull,37ull};
    for (size_t i = 0; i < sizeof(small_primes)/sizeof(small_primes[0]); ++i) {
        uint64_t p = small_primes[i];
        if (n == p) return true;
        if (n % p == 0ull) return false;
    }

    // Write n-1 = 2^s * d with d odd
    uint64_t d = n - 1;
    unsigned int s = 0;
    while ((d & 1ull) == 0ull) { d >>= 1ull; ++s; }

    // Deterministic set of bases for testing all 64-bit integers
    static const uint64_t bases[] = {2ull, 325ull, 9375ull, 28178ull, 450775ull, 9780504ull, 1795265022ull};

    for (size_t i = 0; i < sizeof(bases)/sizeof(bases[0]); ++i) {
        uint64_t a = bases[i] % n;
        if (a == 0ull) continue; // base not informative
        uint64_t x = powmod_u64(a, d, n);
        if (x == 1ull || x == n - 1) continue;
        bool witness = true;
        for (unsigned int r = 1; r < s; ++r) {
            x = mulmod_u64(x, x, n);
            if (x == n - 1) { witness = false; break; }
        }
        if (witness) return false;
    }
    return true;
}

// ---------------- Prime Generation Sundaram Sieve ----------------
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

// ---------------- Prime Generation Eratosthenes Sieve ----------------
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

// ---------------- Divisor count for n using trial division ----------------
// Mirrors the Python reference implementation:
// def num_factors(n: int) -> int:
//     count = 0
//     sqrt_n = int(n ** 0.5)
//     for i in range(1, sqrt_n + 1):
//         if n % i == 0:
//             count += 2
//     if sqrt_n * sqrt_n == n:
//         count -= 1
//     return count
// For n == 0 we return 0 (undefined/infinite mathematically; avoid negative/overflow).
uint64_t num_factors(uint64_t n) {
    if (n == 0ull) {
        return 0ull;
    }
    uint64_t count = 0ull;
    uint64_t sqrt_n = (uint64_t)(sqrt((long double)n));
    for (uint64_t i = 1ull; i <= sqrt_n; ++i) {
        if (n % i == 0ull) {
            count += 2ull; // i and n / i
        }
    }
    if (sqrt_n * sqrt_n == n) {
        // perfect square was double-counted
        count -= 1ull;
    }
    return count;
}

// ---------------- Sum of proper divisors using trial division ----------------
// Mirrors the Python reference implementation:
// def sum_proper_divisors(n: int) -> int:
//     if n < 2:
//         return 0
//     n_sqrt = int(n ** 0.5)
//     total = 1
//     for i in range(2, n_sqrt + 1):
//         if n % i == 0:
//             total += i
//             if i != n // i:
//                 total += n // i
//     return total
uint64_t sum_proper_divisors(uint64_t n) {
    if (n < 2ull) {
        return 0ull;
    }
    uint64_t total = 1ull;
    uint64_t n_sqrt = (uint64_t)(sqrt((long double)n));
    for (uint64_t i = 2ull; i <= n_sqrt; ++i) {
        if (n % i == 0ull) {
            total += i;
            uint64_t other = n / i;
            if (other != i) {
                total += other;
            }
        }
    }
    return total;
}

// ---------------- Prime factor count (unique prime factors) ----------------
// Mirrors Python prime_factor_count using wheel-like gaps.
// Returns the number of distinct prime factors of n. For n<=1 returns 0.
uint64_t prime_factor_count(uint64_t n) {
    if (n <= 1ull) return 0ull;
    uint64_t num_factors = 0ull;
    uint64_t factor = 1ull;
    while (factor <= (uint64_t)sqrt((long double)n)) {
        static const uint64_t small_gaps[5] = {1ull,1ull,2ull,2ull,4ull};
        static const uint64_t large_gaps[8] = {2ull,4ull,2ull,4ull,6ull,2ull,6ull,4ull};
        const uint64_t* gaps = (factor < 11ull) ? small_gaps : large_gaps;
        int glen = (factor < 11ull) ? 5 : 8;
        for (int gi = 0; gi < glen; ++gi) {
            factor += gaps[gi];
            bool is_new = true;
            while (factor != 0ull && n % factor == 0ull) {
                n /= factor;
                if (is_new) { num_factors += 1ull; is_new = false; }
            }
            if (factor > 0ull && factor > (uint64_t)sqrt((long double)n)) {
                break;
            }
        }
    }
    return num_factors + (n == 1ull ? 0ull : 1ull);
}

// ---------------- Divisor count for n^2 using prime factorization ----------------
// Mirrors Python logic from solution_0108: counts divisors of n^2.
// Uses primes_sundaram_sieve to generate primes up to sqrt(n).
// Returns 0 on memory allocation error.
uint64_t count_divisors_square(uint64_t n) {
    if (n == 1ull) {
        return 1ull;
    }
    uint64_t temp = n;
    uint64_t num_divisors = 1ull;

    // Compute limit = floor(sqrt(n)) + 1
    uint64_t limit = (uint64_t)(sqrt((long double)n)) + 1ull;
    // Allocate buffer for primes from Sundaram sieve: at most limit/2 + 1 entries (conservative)
    size_t array_size = (size_t)(limit / 2ull + 2ull);
    uint64_t* primes = (uint64_t*)malloc(array_size * sizeof(uint64_t));
    if (!primes) {
        return 0ull;  // indicate failure (MemoryError on Python side if checked)
    }

    int prime_count = primes_sundaram_sieve(limit, primes);
    if (prime_count == ERROR_MEMORY_ALLOCATION) {
        free(primes);
        return 0ull;
    }

    for (int i = 0; i < prime_count; ++i) {
        uint64_t p = primes[i];
        if (p == 0ull) continue;
        if (temp % p == 0ull) {
            unsigned int power = 0u;
            while (temp % p == 0ull) {
                ++power;
                temp /= p;
            }
            num_divisors *= (uint64_t)(2u * power + 1u);
        }
        if (temp == 1ull) {
            break;
        }
    }

    if (temp > 1ull) {
        // remaining factor is a prime > sqrt(n); its square contributes 3 divisors
        num_divisors *= 3ull;
    }

    free(primes);
    return num_divisors;
}

// ---------------- Prime factorization (bases + exponents) ----------------
// Factorization using primes from Sundaram sieve up to sqrt(n).
// Returns:
//  - >=0: number of factor pairs written to outputs
//  - ERROR_MEMORY_ALLOCATION on allocation failure
//  - ERROR_INSUFFICIENT_BUFFER if max_pairs too small to hold all factors
int prime_factorization(uint64_t n, uint64_t* bases_out, uint32_t* exponents_out, size_t max_pairs) {
    if (!bases_out || !exponents_out) {
        return ERROR_MEMORY_ALLOCATION; // treat as error
    }
    if (n <= 1ull) {
        return 0; // no prime factors for 0,1 in this API
    }

    uint64_t temp = n;
    // limit = floor(sqrt(n)) + 1
    uint64_t limit = (uint64_t)(sqrt((long double)n)) + 1ull;

    // Conservative array size: limit/2 + 2 for Sundaram
    size_t array_size = (size_t)(limit / 2ull + 2ull);
    uint64_t* primes = (uint64_t*)malloc(array_size * sizeof(uint64_t));
    if (!primes) {
        return ERROR_MEMORY_ALLOCATION;
    }

    int prime_count = primes_sundaram_sieve(limit, primes);
    if (prime_count == ERROR_MEMORY_ALLOCATION) {
        free(primes);
        return ERROR_MEMORY_ALLOCATION;
    }

    size_t written = 0;
    for (int i = 0; i < prime_count; ++i) {
        uint64_t p = primes[i];
        if (p == 0ull) continue;
        if (p > temp) break; // no need to check primes larger than remaining temp
        if (temp % p == 0ull) {
            uint32_t exp = 0u;
            while (temp % p == 0ull) {
                temp /= p;
                ++exp;
            }
            if (exp > 0u) {
                if (written >= max_pairs) {
                    free(primes);
                    return ERROR_INSUFFICIENT_BUFFER;
                }
                bases_out[written] = p;
                exponents_out[written] = exp;
                ++written;
            }
        }
        if (temp == 1ull) break;
    }

    if (temp > 1ull) {
        // remaining temp is a prime factor > sqrt(n)
        if (written >= max_pairs) {
            free(primes);
            return ERROR_INSUFFICIENT_BUFFER;
        }
        bases_out[written] = temp;
        exponents_out[written] = 1u;
        ++written;
    }

    free(primes);
    return (int)written;
}
