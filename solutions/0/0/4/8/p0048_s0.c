/* Solution to Euler Problem 48: Self Powers. */
#include "runner.h"

/* Modular exponentiation by squaring: base**exp mod mod in O(log exp) multiplications. */
static long long mod_pow(long long base, long long exp, long long mod) {
    long long result = 1;
    base %= mod;
    while (exp > 0) {
        /* Widen to __int128 before each multiply: operands near 10^10 give products
           up to ~10^20, which overflow a signed 64-bit long long. */
        if (exp & 1)
            result = (__int128)result * base % mod;
        base = (__int128)base * base % mod;
        exp >>= 1;
    }
    return result;
}

/* Sum i^i mod 10^10 via modular exponentiation, reducing the total each step; O(N log N). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int limit = parse_int(argv[1]);
    long long modulo = 10000000000LL; /* 10^10 */
    long long result = 0;
    for (int i = 1; i <= limit; i++) {
        long long term = mod_pow((long long)i, (long long)i, modulo);
        result = (result + term) % modulo;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}
