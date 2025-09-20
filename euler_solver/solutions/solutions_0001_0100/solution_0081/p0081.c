/*******************************************************************************
 * File: p0081.c
 *
 * Description: C implementations of functions used in Project Euler problem 81
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

// Simple helpers
static inline const char* skip_spaces(const char* s) {
    while (*s == ' ' || *s == '\t' || *s == '\r') ++s;
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

