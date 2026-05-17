/* Solution to Euler Problem 85: Counting Rectangles. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Triangular number: sum of (length - k + 1) for k in 1..length = length*(length+1)/2 */
static int triangular(int length) {
    return length * (length + 1) / 2;
}

/* Binary search: find leftmost index in numbers[0..len-1] where numbers[idx] >= x.
 * Returns len if all elements are < x. */
static int bisect_left(int *numbers, int len, int x) {
    int lo = 0, hi = len;
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        if (numbers[mid] < x) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

long long solve(int argc, char *argv[]) {
    int max_error = atoi(argv[1]);
    int max_side  = atoi(argv[2]);
    int target    = atoi(argv[3]);

    int len_numbers = max_side - 1;  /* lengths 1 .. max_side-1 */
    int *numbers = malloc((size_t)len_numbers * sizeof(int));
    if (!numbers) {
        fprintf(stderr, "out of memory\n");
        return -1;
    }
    for (int i = 0; i < len_numbers; i++) {
        numbers[i] = triangular(i + 1);  /* numbers[i] = T(i+1) */
    }

    int best_area  = -1;
    int best_delta = -1;
    int last_num   = 0;

    for (int width = 1; width <= len_numbers; width++) {
        int num_width = numbers[width - 1];
        if (num_width == 0) continue;

        /* find insertion point for target / num_width */
        int q = target / num_width;
        int j = bisect_left(numbers, len_numbers, q);

        /* check candidates j+1 and j+2 (1-indexed heights) */
        for (int k = 0; k <= 1; k++) {
            int height = j + 1 + k;  /* 1-indexed */
            if (height >= 1 && height <= len_numbers) {
                int num = numbers[height - 1] * num_width;
                int d   = abs(num - target);
                last_num = num;
                if (best_delta < 0 || d < best_delta) {
                    best_delta = d;
                    best_area  = height * width;
                }
            }
        }

        if (best_delta >= 0 && best_delta <= max_error) {
            break;
        }
    }

    (void)last_num;
    free(numbers);
    return (long long)best_area;
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