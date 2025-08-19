# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True

def large_non_mersenne_prime_p0097_s0(*, num_digits: int, prime: str) -> int:
    divisor: int = 10 ** num_digits
    prime_parts: list[str] = prime.split()
    number: int
    exponent: int
    number, exponent = (int(prime_parts[0]), int(prime_parts[2][2:]))
    for _ in range(exponent):
        number *= 2
        number %= divisor
    number += 1
    number %= divisor
    return number
