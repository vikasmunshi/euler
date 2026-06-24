/* Solution to Euler Problem 97: Large Non-Mersenne Prime. */
#include "runner.h"

/* Modular exponentiation by square-and-multiply: a^b mod m in O(log b). */
static long long mod_pow(long long base, long long exp, long long mod) {
    long long result = 1LL;
    base %= mod;
    while (exp > 0) {
        if (exp & 1LL) {
            /* Cast to __int128 so the near-10^10 product does not overflow 64 bits. */
            result = (long long)((__int128)result * base % mod);
        }
        /* Same overflow-avoiding cast when squaring the running base. */
        base = (long long)((__int128)base * base % mod);
        exp >>= 1;
    }
    return result;
}

/* Compute (coeff * 2^exp + 1) mod 10^num_digits to read off the last num_digits
 * digits; the modular exponentiation makes this O(log exp). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    /* argv[1] = num_digits
     * argv[2..] = tokens of the prime expression
     * Concatenate all tokens after argv[1] into one string, then parse. */
    int num_digits = parse_int(argv[1]);

    long long divisor = 1LL;
    for (int i = 0; i < num_digits; i++) {
        divisor *= 10LL;
    }

    /* Build full expression string from remaining args */
    char expr[256];
    expr[0] = '\0';
    for (int i = 2; i < argc; i++) {
        if (i > 2) strcat(expr, " ");
        strcat(expr, argv[i]);
    }

    /* Parse coefficient: first token (digits at start) */
    long long coefficient = atoll(expr);

    /* Find '^' in the expression to get exponent */
    char *caret = strchr(expr, '^');
    long long exponent = 0LL;
    if (caret != NULL) {
        exponent = atoll(caret + 1);
    }

    /* result = (coefficient * 2^exponent + 1) mod divisor */
    long long power = mod_pow(2LL, exponent, divisor);
    long long result = (long long)((__int128)(coefficient % divisor) * power % divisor);
    result = (result + 1LL) % divisor;
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}