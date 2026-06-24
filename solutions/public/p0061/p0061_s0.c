/* Solution to Euler Problem 61: Cyclical Figurate Numbers. */
#include "runner.h"
#include <math.h>

#define MAX_NUMS 600
#define MAX_LENGTH 8
#define MAX_RESULTS 200

static int nth_triangle(int n)   { return n * (n + 1) / 2; }
static int nth_square(int n)     { return n * n; }
static int nth_pentagonal(int n) { return n * (3 * n - 1) / 2; }
static int nth_hexagonal(int n)  { return n * (2 * n - 1); }
static int nth_heptagonal(int n) { return n * (5 * n - 3) / 2; }
static int nth_octagonal(int n)  { return n * (3 * n - 2); }

typedef int (*gen_func)(int);

/* Function-pointer table: one closed-form generator per polygon type, indexed 0..5. */
static gen_func generators[6] = {
    nth_triangle, nth_square, nth_pentagonal,
    nth_hexagonal, nth_heptagonal, nth_octagonal
};

static int p_numbers[6][MAX_NUMS];
static int p_counts[6];
static int num_types_global;

static int all_nums[MAX_NUMS];
static int all_count = 0;

static int successors[MAX_NUMS][MAX_NUMS];
static int succ_counts[MAX_NUMS];

static int results[MAX_RESULTS][MAX_LENGTH];
static int result_sums[MAX_RESULTS];
static int result_count = 0;

static int path_idx[MAX_LENGTH];
static int visited[MAX_NUMS];
static int target_length;

/* True if the cycle has exactly one member per polygon type, accounting for numbers that belong to
   several families: a multi-type number cannot simultaneously be the sole representative of every
   one of its types, or some type would be left unfilled. */
static int verify_polygon_types(int *cycle, int len, int ntypes) {
    int type_member_count[6];
    memset(type_member_count, 0, sizeof(type_member_count));

    /* For each type, count how many cycle members belong to it */
    for (int t = 0; t < ntypes; t++) {
        for (int i = 0; i < len; i++) {
            int num = cycle[i];
            for (int j = 0; j < p_counts[t]; j++) {
                if (p_numbers[t][j] == num) {
                    type_member_count[t]++;
                    break;
                }
            }
        }
        if (type_member_count[t] == 0) return 0;
    }

    /* Build reverse: for each number in cycle, which types contain it */
    int num_type_list[MAX_LENGTH][6];
    int num_type_count[MAX_LENGTH];
    memset(num_type_count, 0, sizeof(num_type_count));

    for (int i = 0; i < len; i++) {
        int num = cycle[i];
        for (int t = 0; t < ntypes; t++) {
            for (int j = 0; j < p_counts[t]; j++) {
                if (p_numbers[t][j] == num) {
                    num_type_list[i][num_type_count[i]++] = t;
                    break;
                }
            }
        }
    }

    /* For ambiguous numbers: if all their types have exactly 1 member each, it's a conflict */
    for (int i = 0; i < len; i++) {
        if (num_type_count[i] > 1) {
            int all_single = 1;
            for (int k = 0; k < num_type_count[i]; k++) {
                int t = num_type_list[i][k];
                if (type_member_count[t] > 1) {
                    all_single = 0;
                    break;
                }
            }
            if (all_single) return 0;
        }
    }

    return 1;
}

/* True if the sorted form of this cycle already appears in results (canonical-form dedup). */
static int already_found(int *cycle, int len) {
    int sorted[MAX_LENGTH];
    memcpy(sorted, cycle, len * sizeof(int));
    /* Insertion sort */
    for (int i = 1; i < len; i++) {
        int key = sorted[i];
        int j = i - 1;
        while (j >= 0 && sorted[j] > key) {
            sorted[j+1] = sorted[j];
            j--;
        }
        sorted[j+1] = key;
    }
    for (int r = 0; r < result_count; r++) {
        int match = 1;
        for (int i = 0; i < len; i++) {
            if (results[r][i] != sorted[i]) { match = 0; break; }
        }
        if (match) return 1;
    }
    return 0;
}

/* Append the cycle in canonical (sorted) form plus its member sum to the results table. */
static void store_result(int *cycle, int len) {
    if (result_count >= MAX_RESULTS) return;
    int sorted[MAX_LENGTH];
    memcpy(sorted, cycle, len * sizeof(int));
    for (int i = 1; i < len; i++) {
        int key = sorted[i];
        int j = i - 1;
        while (j >= 0 && sorted[j] > key) {
            sorted[j+1] = sorted[j];
            j--;
        }
        sorted[j+1] = key;
    }
    memcpy(results[result_count], sorted, len * sizeof(int));
    int s = 0;
    for (int i = 0; i < len; i++) s += sorted[i];
    result_sums[result_count] = s;
    result_count++;
}

/* Backtracking DFS extending the path one successor at a time; on reaching target_length it
   records the cycle when it closes back to the start (last two digits == start's first two) and
   passes the type-coverage check. visited enforces distinct members. */
static void dfs(int start_idx, int current_idx, int depth) {
    if (depth == target_length) {
        int cur_num   = all_nums[current_idx];
        int start_num = all_nums[start_idx];
        if ((cur_num % 100) == (start_num / 100)) {
            int cycle[MAX_LENGTH];
            for (int i = 0; i < depth; i++) {
                cycle[i] = all_nums[path_idx[i]];
            }
            if (!already_found(cycle, depth) &&
                verify_polygon_types(cycle, depth, num_types_global)) {
                store_result(cycle, depth);
            }
        }
        return;
    }

    int sc = succ_counts[current_idx];
    for (int i = 0; i < sc; i++) {
        int next_idx = successors[current_idx][i];
        if (!visited[next_idx]) {
            visited[next_idx] = 1;
            path_idx[depth] = next_idx;
            dfs(start_idx, next_idx, depth + 1);
            visited[next_idx] = 0;
        }
    }
}

/* Model the digit-linking rule (last two digits of A == first two of B) as a directed sparse graph
   over 4-digit figurate numbers, then DFS for length-`length` cycles covering all polygon types.
   O(V^length) worst case, but short successor lists make it near-instant in practice. */
const char *solve(int argc, char *argv[]) {
    int length = 6;
    if (argc > 1) length = parse_int(argv[1]);

    int min_val = 1000;
    int max_val = 9999;
    int ntypes = length;
    num_types_global = ntypes;

    /* Generate figurate numbers for each type */
    for (int t = 0; t < ntypes; t++) {
        p_counts[t] = 0;
        gen_func gf = generators[t];
        int n = 1;
        while (gf(n) < min_val) n++;
        while (1) {
            int val = gf(n);
            if (val > max_val) break;
            if (p_counts[t] < MAX_NUMS)
                p_numbers[t][p_counts[t]++] = val;
            n++;
        }
    }

    /* Collect all unique numbers */
    all_count = 0;
    for (int t = 0; t < ntypes; t++) {
        for (int j = 0; j < p_counts[t]; j++) {
            int num = p_numbers[t][j];
            int found = 0;
            for (int k = 0; k < all_count; k++) {
                if (all_nums[k] == num) { found = 1; break; }
            }
            if (!found && all_count < MAX_NUMS) {
                all_nums[all_count++] = num;
            }
        }
    }

    /* Build successor graph */
    memset(succ_counts, 0, sizeof(succ_counts));
    for (int i = 0; i < all_count; i++) {
        int prev_last2 = all_nums[i] % 100;
        /* Only consider valid 2-digit prefixes (>=10): a prefix below 10 cannot start a 4-digit number */
        for (int j = 0; j < all_count; j++) {
            if (i == j) continue;
            int next_first2 = all_nums[j] / 100;
            if (prev_last2 == next_first2 && prev_last2 >= 10) {
                if (succ_counts[i] < MAX_NUMS)
                    successors[i][succ_counts[i]++] = j;
            }
        }
    }

    /* DFS from each starting node */
    target_length = length;
    result_count = 0;

    for (int start = 0; start < all_count; start++) {
        if (succ_counts[start] == 0) continue;
        memset(visited, 0, all_count * sizeof(int));
        visited[start] = 1;
        path_idx[0] = start;
        dfs(start, start, 1);
    }

    /* Sort results by sum (insertion sort) */
    for (int i = 1; i < result_count; i++) {
        int key_sum = result_sums[i];
        int key_res[MAX_LENGTH];
        memcpy(key_res, results[i], length * sizeof(int));
        int j = i - 1;
        while (j >= 0 && result_sums[j] > key_sum) {
            result_sums[j+1] = result_sums[j];
            memcpy(results[j+1], results[j], length * sizeof(int));
            j--;
        }
        result_sums[j+1] = key_sum;
        memcpy(results[j+1], key_res, length * sizeof(int));
    }

    /* Build JSON output */
    char *buf = malloc(8192);
    if (!buf) return NULL;

    if (result_count == 0) {
        snprintf(buf, 8192, "[0, []]");
    } else if (result_count == 1) {
        snprintf(buf, 8192, "[1, %d]", result_sums[0]);
    } else {
        int pos = 0;
        pos += snprintf(buf + pos, 8192 - pos, "[%d, [", result_count);
        for (int i = 0; i < result_count; i++) {
            if (i > 0) pos += snprintf(buf + pos, 8192 - pos, ", ");
            pos += snprintf(buf + pos, 8192 - pos, "%d", result_sums[i]);
        }
        snprintf(buf + pos, 8192 - pos, "]]");
    }

    return buf;
}