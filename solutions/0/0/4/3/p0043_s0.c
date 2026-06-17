/* Solution to Euler Problem 43: Sub-string Divisibility. */
#include "runner.h"

/* The 44 three-digit multiples of 17 with no repeated digit; these are the only
 * legal values for the rightmost window d8 d9 d10 and seed the search. */
static const char *valid_multiples_of_17[] = {
    "017", "034", "051", "068", "085", "102", "136", "153", "170", "187",
    "204", "238", "289", "306", "340", "357", "374", "391", "408", "425",
    "459", "476", "493", "510", "527", "561", "578", "612", "629", "680",
    "697", "714", "731", "748", "765", "782", "816", "850", "867", "901",
    "918", "935", "952", "986"
};
static const int num_multiples_of_17 = 44;

/* Successor in the divisor chain 17->13->11->7->5->3->2; returns 0 at the end. */
static int next_divisor(int divisor) {
    switch (divisor) {
        case 17: return 13;
        case 13: return 11;
        case 11: return 7;
        case  7: return 5;
        case  5: return 3;
        case  3: return 2;
        default: return 0; /* no next divisor */
    }
}

static long long total_sum = 0;

/* Prepend one digit so the leading three-character window is divisible by the
 * current divisor, then recurse on the next divisor; accumulate completed
 * pandigitals into total_sum. Building right-to-left keeps the divisibility
 * window fixed at the front of the string.
 * current_number: digits fixed so far (the right portion of the number)
 * len: length of current_number
 * divisor: divisor the new leading window must satisfy
 */
static void gen_special_numbers(const char *current_number, int len, int divisor, int show) {
    int ndiv = next_divisor(divisor);

    for (char d = '0'; d <= '9'; d++) {
        /* Skip digits already used: linear scan is O(1) at this fixed size. */
        int found = 0;
        for (int i = 0; i < len; i++) {
            if (current_number[i] == d) { found = 1; break; }
        }
        if (found) continue;

        /* Build next_num = d + current_number. */
        char next_num[12];
        next_num[0] = d;
        memcpy(next_num + 1, current_number, (size_t)len);
        next_num[len + 1] = '\0';
        int next_len = len + 1;

        /* Prune unless the new three-digit prefix is divisible by divisor. */
        int window = (next_num[0] - '0') * 100 + (next_num[1] - '0') * 10 + (next_num[2] - '0');
        if (window % divisor != 0) continue;

        if (ndiv == 0) {
            /* Chain exhausted: next_num holds d2..d10; the single unused digit
             * is d1, which carries no constraint. */
            char remaining = 0;
            for (char r = '0'; r <= '9'; r++) {
                int used = 0;
                for (int i = 0; i < next_len; i++) {
                    if (next_num[i] == r) { used = 1; break; }
                }
                if (!used) { remaining = r; break; }
            }
            /* Full 10-digit pandigital: remaining + next_num */
            char full[12];
            full[0] = remaining;
            memcpy(full + 1, next_num, (size_t)next_len);
            full[next_len + 1] = '\0';
            /* Convert to long long */
            long long value = 0;
            for (int i = 0; i < 10; i++) {
                value = value * 10 + (full[i] - '0');
            }
            total_sum += value;
            if (show) printf("%lld\n", value);
        } else {
            gen_special_numbers(next_num, next_len, ndiv, show);
        }
    }
}

/* Right-to-left constrained backtracking over the divisor chain
 * 17->13->11->7->5->3->2, seeded by the 44 valid d8 d9 d10 windows; overlapping
 * windows prune the search to a handful of nodes. Worst case O(10!), but
 * effectively microseconds. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;
    total_sum = 0;

    for (int i = 0; i < num_multiples_of_17; i++) {
        gen_special_numbers(valid_multiples_of_17[i], 3, 13, show);
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total_sum)); return _answer; }
}