/* Solution to Euler Problem 43: Sub-string Divisibility. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static const char *valid_multiples_of_17[] = {
    "017", "034", "051", "068", "085", "102", "136", "153", "170", "187",
    "204", "238", "289", "306", "340", "357", "374", "391", "408", "425",
    "459", "476", "493", "510", "527", "561", "578", "612", "629", "680",
    "697", "714", "731", "748", "765", "782", "816", "850", "867", "901",
    "918", "935", "952", "986"
};
static const int num_multiples_of_17 = 44;

/* Divisor chain going backwards: 17->13->11->7->5->3->2 */
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

/* current_number: string of digits built so far (right portion)
 * divisor: the divisor to apply when prepending the next digit
 * len: length of current_number string
 */
static void gen_special_numbers(const char *current_number, int len, int divisor, int show) {
    int ndiv = next_divisor(divisor);

    for (char d = '0'; d <= '9'; d++) {
        /* Check digit not already used */
        int found = 0;
        for (int i = 0; i < len; i++) {
            if (current_number[i] == d) { found = 1; break; }
        }
        if (found) continue;

        /* Build next_num = d + current_number */
        char next_num[12];
        next_num[0] = d;
        memcpy(next_num + 1, current_number, (size_t)len);
        next_num[len + 1] = '\0';
        int next_len = len + 1;

        /* Check divisibility: first 3 chars of next_num */
        int window = (next_num[0] - '0') * 100 + (next_num[1] - '0') * 10 + (next_num[2] - '0');
        if (window % divisor != 0) continue;

        if (ndiv == 0) {
            /* next_len should be 9 (positions d2..d10), find the remaining digit for d1 */
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

long long solve(int argc, char *argv[], int show) {
    (void)argc; (void)argv;
    total_sum = 0;

    for (int i = 0; i < num_multiples_of_17; i++) {
        gen_special_numbers(valid_multiples_of_17[i], 3, 13, show);
    }

    return total_sum;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;
    int show = 0;

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) {
        fprintf(stderr, "runner: out of memory\n");
        return 1;
    }
    int solve_argc = 0;
    solve_argv[solve_argc++] = argv[0];

    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '\0') continue;
        if (strncmp(argv[i], "--runs=", 7) == 0) {
            int r = atoi(argv[i] + 7);
            if (r >= 1) runs = r;
            continue;
        }
        if (strcmp(argv[i], "--show") == 0) { show = 1; continue; }
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv, show);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (has_result && cur != result) {
            fprintf(stderr, "Expected consistent result, got %lld previous result=%lld\n",
                    cur, result);
            rc = 1;
        }
        result = cur;
        has_result = 1;
    }

    free(solve_argv);
    printf("%d %.17g %lld\n", runs, total / (double)runs, result);
    return rc;
}