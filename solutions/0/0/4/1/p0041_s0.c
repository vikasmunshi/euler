/* Solution to Euler Problem 41: Pandigital Prime. */
#include "runner.h"

/* Trial division up to sqrt(num); adequate since candidates stay below 8 million. */
static int is_prime(int num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (int i = 3; (long long)i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

/* Advance arr to the next permutation in ascending lexicographic order; 0 when exhausted. */
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

/* Step arr to the previous permutation in descending lexicographic order; 0 when exhausted. */
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

/* Fold the first n digits of arr into an integer via num = num * 10 + digit. */
static int digits_to_number(int *arr, int n) {
    int num = 0;
    for (int i = 0; i < n; i++) {
        num = num * 10 + arr[i];
    }
    return num;
}

/* Digit-sum-mod-3 pruning leaves only lengths 7 and 4 viable; enumerate each length's
   permutations in descending order via prev_permutation and return the first prime. The
   descending walk makes that first hit the maximum. Cost O(k! * sqrt(N)), k <= 7. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
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
                { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)num)); return _answer; }
            }
        } while (prev_permutation(digits, n));
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
}