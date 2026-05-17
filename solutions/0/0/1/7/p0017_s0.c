/* Solution to Euler Problem 17: Number Letter Counts. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static const char *number_to_word[100] = {
    /* 0 */ "",
    /* 1 */ "one",
    /* 2 */ "two",
    /* 3 */ "three",
    /* 4 */ "four",
    /* 5 */ "five",
    /* 6 */ "six",
    /* 7 */ "seven",
    /* 8 */ "eight",
    /* 9 */ "nine",
    /* 10 */ "ten",
    /* 11 */ "eleven",
    /* 12 */ "twelve",
    /* 13 */ "thirteen",
    /* 14 */ "fourteen",
    /* 15 */ "fifteen",
    /* 16 */ "sixteen",
    /* 17 */ "seventeen",
    /* 18 */ "eighteen",
    /* 19 */ "nineteen",
    /* 20 */ "twenty",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 30 */ "thirty",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 40 */ "forty",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 50 */ "fifty",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 60 */ "sixty",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 70 */ "seventy",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 80 */ "eighty",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    /* 90 */ "ninety",
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
};

static const char *tens_word[10] = {
    "", "", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety"
};

/* Cache for triplet words: indices 0..999 */
static char triplet_cache[1000][64];
static int  triplet_cached[1000];

/* Returns a pointer to a static/cached buffer for the word form of number (0..999).
 * Empty string for 0. */
static const char *number_triplet_in_words(int number) {
    if (triplet_cached[number]) {
        return triplet_cache[number];
    }

    char *buf = triplet_cache[number];
    buf[0] = '\0';

    if (number < 100) {
        /* Direct lookup if available */
        if (number < 20 || (number % 10 == 0)) {
            strncpy(buf, number_to_word[number] ? number_to_word[number] : "", 63);
        } else {
            /* e.g. twenty-one */
            int tens = number / 10;
            int units = number % 10;
            snprintf(buf, 64, "%s-%s", tens_word[tens], number_to_word[units]);
        }
    } else {
        /* hundreds */
        int hundreds = number / 100;
        int rest = number % 100;
        if (rest == 0) {
            snprintf(buf, 64, "%s hundred", number_to_word[hundreds]);
        } else {
            const char *rest_word = number_triplet_in_words(rest);
            snprintf(buf, 64, "%s hundred and %s", number_to_word[hundreds], rest_word);
        }
    }

    triplet_cached[number] = 1;
    return buf;
}

/* Count letters only (skip spaces, hyphens) */
static int count_letters(const char *s) {
    int count = 0;
    while (*s) {
        char c = *s++;
        if (c != ' ' && c != '-') {
            count++;
        }
    }
    return count;
}

/* Convert a full number to words (handles 0..1000 for this problem).
 * Writes into out buffer. */
static void convert_number_to_words(int number, char *out, int out_size) {
    out[0] = '\0';
    if (number == 1000) {
        snprintf(out, (size_t)out_size, "one thousand");
        return;
    }
    /* For this problem max is 1000, so we only need up to three digits */
    if (number < 1000) {
        const char *w = number_triplet_in_words(number);
        snprintf(out, (size_t)out_size, "%s", w);
        return;
    }
    /* General: split into triplets */
    /* For robustness handle larger numbers via triplet decomposition */
    int thousands = number / 1000;
    int rest = number % 1000;
    const char *th_word = number_triplet_in_words(thousands);
    if (rest == 0) {
        snprintf(out, (size_t)out_size, "%s thousand", th_word);
    } else {
        const char *rest_word = number_triplet_in_words(rest);
        /* British English: add "and" if rest < 100 or rest has no hundreds */
        if (rest < 100) {
            snprintf(out, (size_t)out_size, "%s thousand and %s", th_word, rest_word);
        } else {
            snprintf(out, (size_t)out_size, "%s thousand %s", th_word, rest_word);
        }
    }
}

long long solve(int argc, char *argv[]) {
    int max_number = (argc > 1) ? atoi(argv[1]) : 1000;

    /* Initialize cache */
    memset(triplet_cached, 0, sizeof(triplet_cached));

    long long total = 0;
    char buf[256];
    for (int n = 1; n <= max_number; n++) {
        convert_number_to_words(n, buf, sizeof(buf));
        total += count_letters(buf);
    }
    return total;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;

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
        if (strcmp(argv[i], "--show") == 0) continue;
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv);
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