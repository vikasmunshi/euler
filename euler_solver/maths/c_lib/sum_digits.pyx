# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

cpdef int sum_of_digits(long n):
    cdef int result = 0
    while n > 0:
        result += n % 10
        n //= 10
    return result

cdef int factorial(int n):
    cdef result = 1
    cdef int i
    for i in range(1, n + 1):
        result *= i
    return result

digit_factorials: tuple[int, ...] = tuple(factorial(d) for d in range(10))

cpdef int sum_of_digit_factorials(long n):
    cdef int result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result

cpdef int find_digit_factorial_chains(long max_num, int target_length):
    cdef dict chain_cache = {}
    cdef int count = 0
    cdef long start, current
    cdef int length
    cdef list seen
    for start in range(1, max_num):
        seen = []
        current = start
        while current not in seen and current not in chain_cache:
            seen.append(current)
            current = sum_of_digit_factorials(current)
        if current in chain_cache:
            length = len(seen) + chain_cache[current]
        else:
            length = len(seen)
        for i, n in enumerate(seen):
            chain_cache[n] = length - i
        if chain_cache[start] == target_length:
            count += 1
    return count
