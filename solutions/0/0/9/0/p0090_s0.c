/* Solution to Euler Problem 90: Cube Digit Pairs. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int can_display(int *cube, int digit) {
    for (int i = 0; i < 6; i++) {
        if (cube[i] == digit) return 1;
    }
    if (digit == 6 || digit == 9) {
        for (int i = 0; i < 6; i++) {
            if (cube[i] == 6 || cube[i] == 9) return 1;
        }
    }
    return 0;
}

static int can_pair_display_all(int *cube1, int *cube2) {
    /* squares: 01,04,09,16,25,36,49,64,81 */
    int squares[9][2] = {
        {0,1},{0,4},{0,9},{1,6},{2,5},{3,6},{4,9},{6,4},{8,1}
    };
    for (int s = 0; s < 9; s++) {
        int a = squares[s][0];
        int b = squares[s][1];
        if (!((can_display(cube1, a) && can_display(cube2, b)) ||
              (can_display(cube1, b) && can_display(cube2, a)))) {
            return 0;
        }
    }
    return 1;
}

long long solve(int argc, char *argv[]) {
    /* Generate all C(10,6) = 210 combinations */
    int all_cubes[210][6];
    int cube_count = 0;

    for (int a = 0; a <= 4; a++)
    for (int b = a+1; b <= 5; b++)
    for (int c = b+1; c <= 6; c++)
    for (int d = c+1; d <= 7; d++)
    for (int e = d+1; e <= 8; e++)
    for (int f = e+1; f <= 9; f++) {
        all_cubes[cube_count][0] = a;
        all_cubes[cube_count][1] = b;
        all_cubes[cube_count][2] = c;
        all_cubes[cube_count][3] = d;
        all_cubes[cube_count][4] = e;
        all_cubes[cube_count][5] = f;
        cube_count++;
    }

    long long valid_arrangements = 0;
    for (int i = 0; i < cube_count; i++) {
        for (int j = i; j < cube_count; j++) {
            if (can_pair_display_all(all_cubes[i], all_cubes[j])) {
                valid_arrangements++;
            }
        }
    }
    return valid_arrangements;
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