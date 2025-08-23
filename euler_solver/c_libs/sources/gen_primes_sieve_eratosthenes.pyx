# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3

def gen_primes_sieve_eratosthenes():
    cdef dict known_composites = {}
    cdef long long int current_number = 2
    cdef long long int composite, p

    while True:
        if current_number not in known_composites:
            # The current number is prime - yield it and mark its square as composite
            yield current_number
            composite = current_number * current_number
            known_composites[composite] = [current_number]
        else:
            # Current number is composite - update future composites
            for p in known_composites[current_number]:
                composite = p + current_number
                if composite not in known_composites:
                    known_composites[composite] = []
                known_composites[composite].append(p)
            # Remove the current composite from the dictionary to save memory
            del known_composites[current_number]
        current_number += 1

__pyi__ = 'def gen_primes_sieve_eratosthenes() -> Generator[int, None, None]: ...'
