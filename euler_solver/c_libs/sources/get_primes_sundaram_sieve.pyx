# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3

from libc.stdlib cimport malloc, free

cdef int primes_sundaram_sieve(const long long int max_num, long long int** primes_out):
    cdef long long int max_number = (max_num - 1) // 2
    cdef long long int i, j, index_limit
    cdef char* numbers = <char *> malloc((max_number + 1) * sizeof(char))  # Optimized C-level array
    cdef long long int prime_count = 1  # Account for number 2 as prime
    cdef long long int * primes
    cdef long long int prime_idx

    if not numbers:
        return -1  # Memory allocation failed

    # Initialize all as 1 (true)
    for i in range(max_number + 1):
        numbers[i] = 1

    # Mark non-primes using the Sundaram Sieve logic
    for i in range(1, max_number + 1):
        index_limit = (max_number - i) // (2 * i + 1)
        for j in range(i, index_limit + 1):
            numbers[i + j + 2 * i * j] = 0

    # Count primes
    for i in range(1, max_number + 1):
        if numbers[i]:
            prime_count += 1

    # Allocate memory for the primes array
    primes = <long long int *> malloc(prime_count * sizeof(long long int))
    if not primes:
        free(numbers)
        return -1  # Memory allocation failed

    # Populate primes array
    primes[0] = 2
    prime_idx = 1
    for i in range(1, max_number + 1):
        if numbers[i]:
            primes[prime_idx] = 2 * i + 1
            prime_idx += 1

    primes_out[0] = primes
    free(numbers)

    return prime_count  # Return the count of primes


cpdef get_primes_sundaram_sieve(const long long int max_num):
    cdef long long int * primes
    cdef int prime_count
    cdef list result

    prime_count = primes_sundaram_sieve(max_num, &primes)
    if prime_count < 0:
        raise MemoryError('Failed to allocate memory for sieve')

    # Convert the C array to a Python list
    result = [primes[i] for i in range(prime_count)]

    free(<void *> primes)  # Free the C array
    return tuple(result)

__pyi__ = 'def get_primes_sundaram_sieve(max_num: int) -> tuple[int, ...]: ...'
