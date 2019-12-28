#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
from functools import lru_cache
from collections import namedtuple


def num_divisors(n: int) -> int:
    return 1 + 2 * sum([1 for i in range(2, int(n ** 0.5) + 1) if n % i == 0]) - (1 if n % int(n ** 0.5) == 0 else 0)


@lru_cache()
def is_prime(n: int) -> bool:
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


@lru_cache()
def proper_divisors(n: int) -> (int, ...):
    n_sqrt = int(n ** 0.5)
    factors = [i for i in range(2, n_sqrt + 1) if n % i == 0]
    factors += reversed([n // i for i in factors[:len(factors) - (1 if n_sqrt ** 2 == n else 0)]])
    return (1,) + tuple(factors)


Factor = namedtuple('Factor', ('base', 'exponent'))
Factor.__repr__ = lambda f: str(f.base) + '^' + str(f.exponent).translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))


@lru_cache()
def prime_factorization(n: int) -> (Factor, ...):
    def reduce(number: int, divisor: int) -> Factor:
        result = 0
        while number % divisor == 0:
            number //= divisor
            result += 1
        return Factor(base=divisor, exponent=result)

    return tuple(reduce(n, p) for p in tuple([d for d in proper_divisors(n)[1:] if proper_divisors(d) == (1,)]) or (n,))


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        wd.evaluate_compare((prime_factorization, proper_divisors),
                            answers={100: None, 197: None, 199: None, 191279089787254: None, 7911084415538: None})
