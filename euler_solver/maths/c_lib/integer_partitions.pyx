# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

from itertools import count

# Define cache as a dictionary to manually store results
cdef dict cache = {}

def num_partitions(int number) -> int:
    if number in cache:
        return cache[number]
    if number <= 0:
        result = int(number == 0)
        cache[number] = result
        return result
    result = 0
    for n in count(1):
        _n, sign = -n, (-1, +1)[n % 2]
        p_1 = num_partitions(number - (n * (3 * n - 1) // 2))
        p_2 = num_partitions(number - (_n * (3 * _n - 1) // 2))
        result += sign * (p_1 + p_2)
        if p_1 == 0 and p_2 == 0:
            break
    cache[number] = result  # Store result in cache
    return result
