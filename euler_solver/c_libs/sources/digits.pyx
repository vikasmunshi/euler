# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

cpdef tuple[int, ...] digits(const long long int n):
    cdef list result = []
    cdef long long int num = n
    while num > 0:
        result.append(num % 10)
        num //= 10
    result.reverse()
    return tuple(result)

__signature__ = 'def digits(n: int) -> tuple[int, ...]: ...'