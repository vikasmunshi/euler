/* Solution to Euler Problem 74: Digit Factorial Chains. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* s2 shares the same algorithm as s1 (add_chains with list-based chain lengths),
 * with optional visualization skipped (no ANSI/graphical output in C translation). */

static const int digit_factorials[10] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

static int sum_of_digit_factorials(int n) {
    int result = 0;
    while (n > 0) {
        result += digit_factorials[n % 10];
        n /= 10;
    }
    return result;
}

long long solve(int argc, char *argv[]) {
    int max_num = atoi(argv[1]);

    int cache_size = 3000000;

    int *chain_length = calloc((size_t)cache_size, sizeof(int));
    if (!chain_length) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    int chain_cap = 256;
    int *current_chain = malloc((size_t)chain_cap * sizeof(int));
    char *visited_flag = calloc((size_t)cache_size, sizeof(char));
    if (!current_chain || !visited_flag) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    for (int number = 2; number <= max_num; number++) {
        if (number < cache_size && chain_length[number] != 0) {
            int cl = chain_length[number];
            if (cl > max_chain_length) {
                max_chain_length = cl;
                max_chain_length_count = 1;
            } else if (cl == max_chain_length) {
                max_chain_length_count++;
            }
            continue;
        }

        int chain_len = 0;
        int visited_len = 0;
        int visited_list_cap = 256;
        int *visited_list = malloc((size_t)visited_list_cap * sizeof(int));
        if (!visited_list) {
            fprintf(stderr, "Out of memory\n");
            return -1;
        }

        int num = number;
        int hit_cached = 0;
        int cached_length = 0;

        while (1) {
            int in_visited = (num < cache_size) ? visited_flag[num] : 0;
            if (in_visited) {
                break;
            }
            if (num < cache_size && chain_length[num] != 0) {
                hit_cached = 1;
                cached_length = chain_length[num];
                break;
            }

            if (chain_len >= chain_cap) {
                chain_cap *= 2;
                current_chain = realloc(current_chain, (size_t)chain_cap * sizeof(int));
                if (!current_chain) {
                    fprintf(stderr, "Out of memory\n");
                    return -1;
                }
            }
            current_chain[chain_len++] = num;

            if (num < cache_size) {
                visited_flag[num] = 1;
                if (visited_len >= visited_list_cap) {
                    visited_list_cap *= 2;
                    visited_list = realloc(visited_list, (size_t)visited_list_cap * sizeof(int));
                    if (!visited_list) {
                        fprintf(stderr, "Out of memory\n");
                        return -1;
                    }
                }
                visited_list[visited_len++] = num;
            }

            num = sum_of_digit_factorials(num);
        }

        for (int i = 0; i < visited_len; i++) {
            visited_flag[visited_list[i]] = 0;
        }
        free(visited_list);

        int total_length = hit_cached ? (chain_len + cached_length) : chain_len;

        for (int i = 0; i < chain_len; i++) {
            int val = current_chain[i];
            if (val < cache_size && chain_length[val] == 0) {
                chain_length[val] = total_length - i;
            }
        }

        int cl = (number < cache_size) ? chain_length[number] : total_length;
        if (cl > max_chain_length) {
            max_chain_length = cl;
            max_chain_length_count = 1;
        } else if (cl == max_chain_length) {
            max_chain_length_count++;
        }
    }

    free(chain_length);
    free(current_chain);
    free(visited_flag);

    return (long long)max_chain_length_count;
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