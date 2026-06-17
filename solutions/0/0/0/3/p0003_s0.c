/* Solution to Euler Problem 3: Largest Prime Factor. */
#include "runner.h"
#include <math.h>

/* Divide num by divisor repeatedly, returning the part coprime to divisor. */
static long long reduce(long long num, long long divisor) {
    num /= divisor;
    while (num % divisor == 0)
        num /= divisor;
    return num;
}

/* Trial division with full reduction of each factor found; O(sqrt(n)) worst
   case, far less once a large prime cofactor remains. Removing every factor in
   increasing order means each surviving divisor is prime, so no primality test
   is needed; the search ceiling is recomputed from the shrinking remainder.
   long long holds the 64-bit inputs that would overflow a 32-bit int. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long number = parse_int(argv[1]);
    long long remaining_number;
    long long largest_factor;

    if (number % 2 == 0) {
        remaining_number = reduce(number, 2);
        largest_factor = 2;
    } else {
        remaining_number = number;
        largest_factor = 1;
    }

    long long current_factor = 3;
    long long search_limit = (long long)sqrt((double)remaining_number);

    while (remaining_number > 1 && current_factor <= search_limit) {
        if (remaining_number % current_factor == 0) {
            remaining_number = reduce(remaining_number, current_factor);
            largest_factor = current_factor;
            search_limit = (long long)sqrt((double)remaining_number);
        }
        current_factor += 2;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((remaining_number > 1) ? remaining_number : largest_factor)); return _answer; }
}
