/* Solution to Euler Problem 2: Even Fibonacci Numbers. */
#include "runner.h"

/* Sum the even Fibonacci numbers below max_limit via the even-term recurrence
   E(k+1) = 4*E(k) + E(k-1) (every third Fibonacci term is even); O(log max_limit)
   time, O(1) space. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long max_limit = parse_int(argv[1]);
    long long even_fib_a = 2, even_fib_b = 8;
    long long total = 0;

    while (even_fib_a < max_limit) {
        total += even_fib_a;
        long long next = 4 * even_fib_b + even_fib_a;
        even_fib_a = even_fib_b;
        even_fib_b = next;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}
