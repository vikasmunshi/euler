# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, initializedcheck=False

from libc.stdlib cimport malloc, free

cpdef get_primes_sundaram_sieve(const long long int max_num):
    cdef long long int max_number = (max_num - 1) // 2
    cdef long long int i, j, index_limit
    cdef char * numbers = <char *> malloc((max_number + 1) * sizeof(char))  # Optimized C-level array
    cdef long long int prime_count = 1  # Account for number 2 as prime

    if not numbers:
        raise MemoryError("Failed to allocate memory for sieve bit array")

    # Initialize all as 1 (true)
    for i in range(max_number + 1):
        numbers[i] = 1

    # Mark non-primes using the Sundaram Sieve logic
    for i in range(1, max_number + 1):
        index_limit = (max_number - i) // (2 * i + 1)
        for j in range(i, index_limit + 1):
            numbers[i + j + 2 * i * j] = 0

    # Count primes and calculate output tuple size
    for i in range(1, max_number + 1):
        if numbers[i]:
            prime_count += 1

    # Populate output tuple
    cdef tuple results = tuple((0,) * prime_count)
    results[0] = 2

    prime_index = 1
    for i in range(1, max_number + 1):
        if numbers[i]:
            results[prime_index] = 2 * i + 1
            prime_index += 1

    # Free allocated memory
    free(numbers)

    return results

__signature__ = 'def get_primes_sundaram_sieve(max_num: int) -> tuple[int, ...]: ...'
