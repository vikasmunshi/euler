/* Solution to Euler Problem 24: Lexicographic Permutations. */
#include "runner.h"

/* n! for small n; long long comfortably holds 9! = 362880. */
static long long factorial(int n) {
    long long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

/* Recursive function: digits is a null-terminated string of available digits,
   permutation_number is 1-based. Returns a heap-allocated string. */
static char *recursive_solution(const char *digits, long long permutation_number) {
    int len = (int)strlen(digits);
    if (len == 1) {
        char *result = malloc(2);
        result[0] = digits[0];
        result[1] = '\0';
        return result;
    }

    long long fact = factorial(len - 1);
    long long current = (permutation_number - 1) / fact;
    long long remaining = (permutation_number - 1) % fact;

    /* Build new digits string with digits[current] removed */
    char *new_digits = malloc((size_t)len);
    int j = 0;
    for (int i = 0; i < len; i++) {
        if (i != (int)current) {
            new_digits[j++] = digits[i];
        }
    }
    new_digits[j] = '\0';

    char *sub = recursive_solution(new_digits, remaining + 1);
    free(new_digits);

    char *result = malloc((size_t)(len + 1));
    result[0] = digits[current];
    strcpy(result + 1, sub);
    free(sub);

    return result;
}

/* Recursive unranking via the factorial number system, same algorithm as the
   Python sibling: divmod the 0-based rank by (len-1)! to pick each digit; O(n^2). */
const char *solve(int argc, char *argv[]) {
    const char *digits = argv[1];
    long long permutation_number = parse_int(argv[2]);
    return recursive_solution(digits, permutation_number);
}
