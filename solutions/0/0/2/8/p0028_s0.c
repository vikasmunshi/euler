/* Solution to Euler Problem 28: Number Spiral Diagonals. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static long long number_spiral_with_diagonal_sum(long long size) {
    int half = (int)(size / 2);
    int dim = (int)size;
    int *grid = calloc((size_t)(dim * dim), sizeof(int));
    if (!grid) return -1;

    /* grid[(row+half)*dim + (col+half)] holds the spiral value at (col, row) */
    int x = 0, y = 0;
    grid[half * dim + half] = 1;

    /* right, down, left, up — matching Python's adjacent order */
    static const int dx[] = {1, 0, -1, 0};
    static const int dy[] = {0, -1, 0, 1};

    for (int number = 2; number <= dim * dim; number++) {
        int best_x = 0, best_y = 0, best_dist = dim * dim + 1;
        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx < -half || nx > half || ny < -half || ny > half) continue;
            if (grid[(ny + half) * dim + (nx + half)] != 0) continue;
            int dist = nx * nx + ny * ny;
            if (dist < best_dist) {
                best_dist = dist;
                best_x = nx;
                best_y = ny;
            }
        }
        x = best_x;
        y = best_y;
        grid[(y + half) * dim + (x + half)] = number;
    }

    printf("Generated spiral for size %lld with diagonal elements highlighted in\x1b[34m blue\x1b[0m:\n", size);
    for (int row = half; row >= -half; row--) {
        for (int col = -half; col <= half; col++) {
            int val = grid[(row + half) * dim + (col + half)];
            if (col == row || col == -row)
                printf("\x1b[34m%2d\x1b[0m", val);
            else
                printf("%2d", val);
            if (col < half) printf(" ");
        }
        printf("\n");
    }

    long long diagonal_sum = 0;
    for (int row = -half; row <= half; row++)
        for (int col = -half; col <= half; col++)
            if (col == row || col == -row)
                diagonal_sum += grid[(row + half) * dim + (col + half)];

    long long formula_result = (size * (size * (4 * size + 3) + 8) - 9) / 6;
    const char *mark = (formula_result == diagonal_sum)
        ? "\x1b[32m\xe2\x9c\x93" : "\x1b[31m\xe2\x9c\x97";
    printf("%s size=%lld; formula_result=%lld; diagonal_sum=%lld\x1b[0m\n",
           mark, size, formula_result, diagonal_sum);

    free(grid);
    return diagonal_sum;
}

long long solve(int argc, char *argv[], int show) {
    long long size = atoll(argv[1]);
    if (show && size <= 10)
        return number_spiral_with_diagonal_sum(size);
    return (size * (size * (4 * size + 3) + 8) - 9) / 6;
}

/* Usage: ./file <size> [--runs=1] [--show]
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