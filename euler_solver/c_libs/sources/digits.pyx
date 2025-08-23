# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3

cpdef tuple[int, ...] digits(const long long int n):
    cdef list result = []
    cdef long long int num = n
    while num > 0:
        result.append(num % 10)
        num //= 10
    result.reverse()
    return tuple(result)

__pyi__ = 'def digits(n: int) -> tuple[int, ...]: ...'