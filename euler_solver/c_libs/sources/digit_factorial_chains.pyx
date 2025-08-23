# distutils: language = c
# cython: boundscheck=False, wraparound=False, cdivision=True, language_level=3

digit_factorials: tuple[int, ...] = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880,)

def sum_of_digit_factorials(n: int) -> int:
    result = 0
    while n > 0:
        result += digit_factorials[n % 10]
        n //= 10
    return result

cpdef bint add_chains(chains: dict[int, list[int]], number: int):
    if number in chains:
        return False
    num: int = number
    current_chain: list[int] = []
    visited: set[int] = set()
    while num not in visited:
        visited.add(num)
        if num in chains:
            current_chain.extend(chains[num])
            break
        current_chain.append(num)
        num = sum_of_digit_factorials(num)
    loop_start: int = len(current_chain) - len(visited) if num in visited else -1
    for i, val in enumerate(current_chain):
        if val not in chains:
            chains[val] = (current_chain[i:] if i >= loop_start else current_chain[i:])
    return True

cpdef int count_digit_factorial_chains_of_length(max_num: int, target_length: int):
    count: int = 0
    chain_length_cache: dict[int, int] = {}
    graph: dict[int, int] = {}
    for start in range(2, max_num + 1):
        seen: list[int] = []
        current: int = start
        while current not in seen and current not in chain_length_cache:
            seen.append(current)
            if current not in graph:
                graph[current] = sum_of_digit_factorials(current)
            current = graph[current]
        if current in chain_length_cache:
            # Add precomputed chain length if `current` exists in `chain_length_cache`
            length = len(seen) + chain_length_cache[current]
        else:
            # Length is simply the non-repeating terms from `seen`
            length = len(seen)
        # Propagate chain lengths back to all numbers in `seen`
        for i, num in enumerate(seen):
            chain_length_cache[num] = length - i
            graph[num] = seen[i + 1] if i + 1 < len(seen) else current
        if chain_length_cache[start] == target_length:
            count += 1
    return count

__pyi__ = ('def digit_factorial_chains(max_num: int, target_length: int) -> int: ...\n'
           'def digit_factorial_chain_lengths(max_num: int) -> tuple[int]: ...\n'
           'def digit_factorial_chain(start_number: int) -> tuple[int]: ...\n')
