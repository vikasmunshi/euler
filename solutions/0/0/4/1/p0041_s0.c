/* Solution to Euler Problem 41: Pandigital Prime. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int is_prime(int num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (int i = 3; (long long)i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

/* Generate permutations of digits[0..n-1] in lexicographic order.
   digits array is modified in place (Heap's algorithm style, but we use
   next-permutation approach on a sorted/reverse-sorted array). */

static int next_permutation(int *arr, int n) {
    /* Find largest i such that arr[i] < arr[i+1] */
    int i = n - 2;
    while (i >= 0 && arr[i] >= arr[i + 1]) i--;
    if (i < 0) return 0; /* last permutation */
    /* Find largest j such that arr[i] < arr[j] */
    int j = n - 1;
    while (arr[j] <= arr[i]) j--;
    /* Swap */
    int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    /* Reverse suffix starting at i+1 */
    int left = i + 1, right = n - 1;
    while (left < right) {
        tmp = arr[left]; arr[left] = arr[right]; arr[right] = tmp;
        left++; right--;
    }
    return 1;
}

static int prev_permutation(int *arr, int n) {
    /* Find largest i such that arr[i] > arr[i+1] */
    int i = n - 2;
    while (i >= 0 && arr[i] <= arr[i + 1]) i--;
    if (i < 0) return 0; /* first permutation */
    /* Find largest j such that arr[i] > arr[j] */
    int j = n - 1;
    while (arr[j] >= arr[i]) j--;
    /* Swap */
    int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    /* Reverse suffix starting at i+1 */
    int left = i + 1, right = n - 1;
    while (left < right) {
        tmp = arr[left]; arr[left] = arr[right]; arr[right] = tmp;
        left++; right--;
    }
    return 1;
}

static int digits_to_number(int *arr, int n) {
    int num = 0;
    for (int i = 0; i < n; i++) {
        num = num * 10 + arr[i];
    }
    return num;
}

long long solve(int argc, char *argv[]) {
    (void)argc; (void)argv;

    /* Only lengths 4 and 7 can yield pandigital primes (digit-sum pruning).
       Search in descending order: try length 7 first, then length 4.
       For descending permutations, start from largest (e.g. 7654321) and
       use prev_permutation until exhausted. */

    int lengths[2] = {7, 4};

    for (int li = 0; li < 2; li++) {
        int n = lengths[li];
        /* Initialize digits in descending order: n, n-1, ..., 1 */
        int digits[9];
        for (int i = 0; i < n; i++) {
            digits[i] = n - i;
        }
        /* Iterate over all permutations in descending order */
        do {
            int num = digits_to_number(digits, n);
            if (is_prime(num)) {
                return (long long)num;
            }
        } while (prev_permutation(digits, n));
    }

    return -1;
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