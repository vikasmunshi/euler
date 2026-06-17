/* Solution to Euler Problem 36: Double-base Palindromes. */
#include "runner.h"

/* Test binary palindromicity by extracting bits (LSB first) and mirror-comparing; O(log n). */
static int is_binary_palindrome(long long n) {
    if (n <= 0) return 0;
    char bits[64];
    int len = 0;
    long long tmp = n;
    while (tmp > 0) {
        bits[len++] = (char)(tmp & 1);
        tmp >>= 1;
    }
    /* bits is stored LSB first, so check if it reads the same forwards and backwards */
    for (int i = 0; i < len / 2; i++) {
        if (bits[i] != bits[len - 1 - i]) return 0;
    }
    return 1;
}

/* Integer 10^exp, kept exact to avoid floating-point rounding in the half-loop bound. */
static long long int_pow10(int exp) {
    long long result = 1;
    for (int i = 0; i < exp; i++) result *= 10;
    return result;
}

/* Generate decimal palindromes from their left half, then keep the binary palindromes;
   O(sqrt(N) log N). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_digits = parse_int(argv[1]);
    long long total = 0;

    /* Single-digit palindromes: 1-9 */
    for (int digit = 1; digit <= 9; digit++) {
        if (is_binary_palindrome((long long)digit)) {
            total += digit;
        }
    }

    /* Multi-digit palindromes generated from left half */
    long long limit = int_pow10(max_digits / 2);
    for (long long digits = 1; digits < limit; digits++) {
        /* Convert digits to string */
        char digits_str[20];
        snprintf(digits_str, sizeof(digits_str), "%lld", digits);
        int num_digits = (int)strlen(digits_str);

        /* Build reversed string */
        char digits_rev[20];
        for (int i = 0; i < num_digits; i++) {
            digits_rev[i] = digits_str[num_digits - 1 - i];
        }
        digits_rev[num_digits] = '\0';

        /* Even-length palindrome: digits_str + digits_rev */
        char even_str[40];
        snprintf(even_str, sizeof(even_str), "%s%s", digits_str, digits_rev);
        long long even_num = atoll(even_str);
        if (is_binary_palindrome(even_num)) {
            total += even_num;
        }

        /* Odd-length palindromes: digits_str + mid_digit + digits_rev (interior 0 is legal) */
        if (2 * num_digits < max_digits) {
            for (int mid = 0; mid <= 9; mid++) {
                char odd_str[42];
                snprintf(odd_str, sizeof(odd_str), "%s%d%s", digits_str, mid, digits_rev);
                long long odd_num = atoll(odd_str);
                if (is_binary_palindrome(odd_num)) {
                    total += odd_num;
                }
            }
        }
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}