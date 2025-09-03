/*******************************************************************************
 * File: matrix_path_sums.c
 *
 * Description: C implementations of functions used in Project Euler problem 81, 82, and 83.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>

// Public API (ctypes):
// long long path_sum_two_ways_from_csv(const char* content)
// long long path_sum_three_ways_from_csv(const char* content)
// long long path_sum_four_ways_from_csv(const char* content)

// Simple helpers
static inline const char* skip_spaces(const char* s) {
    while (*s == ' ' || *s == '\t' || *s == '\r') ++s;
    return s;
}

static inline const char* skip_line_end(const char* s) {
    if (*s == '\r') ++s;
    if (*s == '\n') ++s;
    return s;
}

// Parse an integer (non-negative) from string; updates pointer
static bool parse_int64(const char** p, long long* out) {
    const char* s = skip_spaces(*p);
    if (!*s) return false;
    long long val = 0;
    bool any = false;
    while (*s && isdigit((unsigned char)*s)) {
        any = true;
        val = val * 10 + (long long)(*s - '0');
        ++s;
    }
    if (!any) return false;
    *out = val;
    *p = skip_spaces(s);
    return true;
}

// Count rows and columns (expects square matrix). Returns 0 on success.
static int count_dims(const char* content, int* out_size) {
    const char* s = content;
    int rows = 0;
    int cols_first = -1;
    while (*s) {
        // Skip leading whitespace and blank lines
        const char* line_start = s;
        // Detect empty line (only whitespace and newline)
        bool only_ws = true;
        while (*s && *s != '\n') {
            if (!isspace((unsigned char)*s)) only_ws = false;
            s++;
        }
        int line_len = (int)(s - line_start);
        if (!only_ws && line_len > 0) {
            // count numbers separated by commas on this line
            int cols = 0;
            const char* t = line_start;
            long long tmp;
            while (*t && *t != '\n') {
                if (!parse_int64(&t, &tmp)) return 2; // parse error
                cols++;
                if (*t == ',') { t++; }
                t = skip_spaces(t);
            }
            if (cols_first == -1) cols_first = cols;
            else if (cols != cols_first) return 3; // ragged rows
            rows++;
        }
        if (*s == '\n') s++;
    }
    if (rows <= 0 || cols_first != rows) return 4; // require square matrix
    *out_size = rows;
    return 0;
}

// Allocate and fill matrix[size][size] from CSV content. Caller must free matrix[0] and matrix.
static int parse_matrix(const char* content, long long*** out_mat, int* out_size) {
    int size;
    int rc = count_dims(content, &size);
    if (rc != 0) return rc;
    long long** mat = (long long**)malloc((size_t)size * sizeof(long long*));
    if (!mat) return 10;
    long long* data = (long long*)malloc((size_t)size * (size_t)size * sizeof(long long));
    if (!data) { free(mat); return 11; }
    for (int i = 0; i < size; ++i) mat[i] = data + (size_t)i * (size_t)size;

    const char* s = content;
    int row = 0;
    while (*s && row < size) {
        // detect if this line has numbers
        const char* line_start = s;
        bool only_ws = true;
        while (*s && *s != '\n') {
            if (!isspace((unsigned char)*s)) only_ws = false;
            s++;
        }
        int line_len = (int)(s - line_start);
        if (!only_ws && line_len > 0) {
            const char* t = line_start;
            for (int col = 0; col < size; ++col) {
                long long v;
                if (!parse_int64(&t, &v)) { free(data); free(mat); return 12; }
                mat[row][col] = v;
                if (*t == ',') t++;
                t = skip_spaces(t);
            }
            row++;
        }
        if (*s == '\n') s++;
    }
    *out_mat = mat;
    *out_size = size;
    return 0;
}

long long path_sum_two_ways_from_csv(const char* content) {
    if (!content) return -1;
    long long** mat = NULL; int n = 0;
    int rc = parse_matrix(content, &mat, &n);
    if (rc != 0) return -(rc);
    // In-place DP from bottom-right to top-left
    for (int r = n - 1; r >= 0; --r) {
        for (int c = n - 1; c >= 0; --c) {
            long long down = (r + 1 < n) ? mat[r + 1][c] : LLONG_MAX;
            long long right = (c + 1 < n) ? mat[r][c + 1] : LLONG_MAX;
            if (down == LLONG_MAX && right == LLONG_MAX) {
                // bottom-right cell, keep as is
            } else if (down == LLONG_MAX) {
                mat[r][c] += right;
            } else if (right == LLONG_MAX) {
                mat[r][c] += down;
            } else {
                mat[r][c] += (down < right ? down : right);
            }
        }
    }
    long long result = mat[0][0];
    free(mat[0]);
    free(mat);
    return result;
}

// Problem 82 helpers: compute for a given column the new minimal values for col-1 as per Python reduce_column
static void reduce_column_c(long long** matrix, int n, int col) {
    // new_entries[row] = min over target of (sum(matrix[cell][col-1] from row..target) + matrix[target][col])
    long long* new_entries = (long long*)malloc((size_t)n * sizeof(long long));
    for (int row = 0; row < n; ++row) {
        long long best = LLONG_MAX;
        for (int target = 0; target < n; ++target) {
            int start = (row < target) ? row : target;
            int end = (row > target) ? row : target;
            long long accum = 0;
            for (int cell = start; cell <= end; ++cell) {
                accum += matrix[cell][col - 1];
            }
            long long cand = accum + matrix[target][col];
            if (cand < best) best = cand;
        }
        new_entries[row] = best;
    }
    for (int row = 0; row < n; ++row) {
        matrix[row][col - 1] = new_entries[row];
    }
    free(new_entries);
}

long long path_sum_three_ways_from_csv(const char* content) {
    if (!content) return -1;
    long long** mat = NULL; int n = 0;
    int rc = parse_matrix(content, &mat, &n);
    if (rc != 0) return -(rc);
    for (int col = n - 1; col >= 1; --col) {
        reduce_column_c(mat, n, col);
    }
    // min over rows in first column
    long long best = LLONG_MAX;
    for (int row = 0; row < n; ++row) {
        if (mat[row][0] < best) best = mat[row][0];
    }
    free(mat[0]);
    free(mat);
    return best;
}

// Problem 83: Dijkstra on grid (4 directions). Use simple O(N^2) selection like Python.
long long path_sum_four_ways_from_csv(const char* content) {
    if (!content) return -1;
    long long** mat = NULL; int n = 0;
    int rc = parse_matrix(content, &mat, &n);
    if (rc != 0) return -(rc);

    int total = n * n;
    long long* distances = (long long*)malloc((size_t)total * sizeof(long long));
    bool* unvisited = (bool*)malloc((size_t)total * sizeof(bool));

    // Compute infinity as sum of all weights + 1
    long long infinity = 1;
    for (int r = 0; r < n; ++r) {
        for (int c = 0; c < n; ++c) {
            infinity += mat[r][c];
        }
    }

    for (int i = 0; i < total; ++i) {
        distances[i] = infinity;
        unvisited[i] = true;
    }
    distances[0] = mat[0][0];

    int target_idx = total - 1;

    // While target is unvisited
    while (unvisited[target_idx]) {
        // find current = argmin distances among unvisited
        int current = -1;
        long long best = infinity + 1;
        for (int i = 0; i < total; ++i) {
            if (unvisited[i] && distances[i] < best) {
                best = distances[i];
                current = i;
            }
        }
        if (current == -1) break; // disconnected (shouldn't happen)
        int cr = current / n;
        int cc = current % n;

        // neighbors: up, down, left, right
        int neighs[4][2] = { {cr - 1, cc}, {cr + 1, cc}, {cr, cc - 1}, {cr, cc + 1} };
        for (int k = 0; k < 4; ++k) {
            int nr = neighs[k][0];
            int nc = neighs[k][1];
            if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
                int ni = nr * n + nc;
                if (unvisited[ni]) {
                    long long nd = distances[current] + mat[nr][nc];
                    if (nd < distances[ni]) distances[ni] = nd;
                }
            }
        }
        unvisited[current] = false;
    }

    long long result = distances[target_idx];
    free(distances);
    free(unvisited);
    free(mat[0]);
    free(mat);
    return result;
}
