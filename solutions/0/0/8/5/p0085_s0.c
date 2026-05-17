/* Solution to Euler Problem 85: Counting Rectangles. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int num_rectangles(int height, int width) {
    int count = 0;
    for (int h = 1; h <= height; h++) {
        for (int w = 1; w <= width; w++) {
            count += (height - h + 1) * (width - w + 1);
        }
    }
    return count;
}

long long solve(int argc, char *argv[]) {
    int max_error = atoi(argv[1]);
    int max_side  = atoi(argv[2]);
    int target    = atoi(argv[3]);

    /* results: store best (height, width, area) keyed by rectangle count.
     * We only need to track the closest to target, so just track best area. */
    int best_area  = -1;
    int best_delta = -1;

    for (int height = 2; height < max_side; height++) {
        for (int width = 2; width < max_side; width++) {
            int num = num_rectangles(height, width);
            int d   = abs(num - target);
            if (best_delta < 0 || d < best_delta) {
                best_delta = d;
                best_area  = height * width;
            }
            if (d <= max_error) {
                goto done;
            }
        }
    }
done:
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