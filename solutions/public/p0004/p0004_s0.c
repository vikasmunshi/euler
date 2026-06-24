/* Solution to Euler Problem 4: Largest Palindrome Product. */
#include "runner.h"

static int is_palindromic(long long number) {
    char buf[32];
    snprintf(buf, sizeof(buf), "%lld", number);
    int len = (int)strlen(buf);
    for (int i = 0, j = len - 1; i < j; i++, j--) {
        if (buf[i] != buf[j]) return 0;
    }
    return 1;
}

/* Descending pruned search for the largest palindromic product of two n-digit numbers.
   Every even-length palindrome is divisible by 11, so one factor must supply that 11:
   when `a` is not a multiple of 11 the inner factor `b` steps by 11, skipping ten of
   every eleven candidates. Iterating downward with a monotone a*b early exit prunes the
   rest. O(d^2 / 11) worst case in the count d = 9*10^(n-1) of n-digit numbers. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int n = parse_int(argv[1]);

    long long max_number = 1;
    for (int i = 0; i < n; i++) max_number *= 10;
    max_number -= 1;

    long long min_number = 1;
    for (int i = 0; i < n - 1; i++) min_number *= 10;

    long long max_multiple_11 = max_number - max_number % 11;

    long long largest_palindrome = 0;
    long long a_max = 0, b_max = 0;

    for (long long a = max_number; a > min_number; a--) {
        int a_is_multiple_11 = (a % 11 == 0);
        long long b_start = a_is_multiple_11 ? max_number : max_multiple_11;
        long long b_step  = a_is_multiple_11 ? 1 : 11;

        for (long long b = b_start; b >= a; b -= b_step) {
            long long ab = a * b;
            if (ab <= largest_palindrome) break;
            if (is_palindromic(ab)) {
                a_max = a; b_max = b; largest_palindrome = ab;
                break;
            }
        }
    }

    if (show)
        printf("Largest palindrome that is a multiple of two %d-digit numbers is "
               "%lld (%lldx%lld)\n", n, largest_palindrome, a_max, b_max);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(largest_palindrome)); return _answer; }
}
