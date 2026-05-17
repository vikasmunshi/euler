/* Solution to Euler Problem 89: Roman Numerals. */
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

char *get_text_file(const char *src) {
    const char *slash = strrchr(src, '/');
    const char *name_start = slash ? slash + 1 : src;
    const char *q = strchr(name_start, '?');
    size_t name_len = q ? (size_t)(q - name_start) : strlen(name_start);

    char exe_path[4096];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len < 0) return NULL;
    exe_path[len] = '\0';

    char path[4096];
    int pn = snprintf(path, sizeof(path), "%s/resources/%.*s", dirname(exe_path), (int)name_len, name_start);
    if (pn < 0 || (size_t)pn >= sizeof(path)) return NULL;

    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return NULL; }
    rewind(f);
    char *buf = malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return NULL; }
    if (fread(buf, 1, (size_t)sz, f) != (size_t)sz) { free(buf); fclose(f); return NULL; }
    buf[sz] = '\0';
    fclose(f);
    return buf;
}

static int char_value(char c) {
    switch (c) {
        case 'I': return 1;
        case 'V': return 5;
        case 'X': return 10;
        case 'L': return 50;
        case 'C': return 100;
        case 'D': return 500;
        case 'M': return 1000;
        default:  return 0;
    }
}

static int roman_to_number(const char *numeral, int len) {
    int value = 0, last = 0;
    for (int i = len - 1; i >= 0; i--) {
        int n = char_value(numeral[i]);
        if (last > n)
            value -= n;
        else
            value += n;
        last = n;
    }
    return value;
}

static const int numeral_values[] = {
    1000, 900, 800, 700, 600, 500, 400, 300, 200, 100,
    90, 80, 70, 60, 50, 40, 30, 20, 10,
    9, 8, 7, 6, 5, 4, 3, 2, 1
};
static const char *numeral_strings[] = {
    "M", "CM", "DCCC", "DCC", "DC", "D", "CD", "CCC", "CC", "C",
    "XC", "LXXX", "LXX", "LX", "L", "XL", "XXX", "XX", "X",
    "IX", "VIII", "VII", "VI", "V", "IV", "III", "II", "I"
};
static const int numeral_count = 28;

static int number_as_roman_numeral_length(int number) {
    int len = 0;
    while (number > 0) {
        for (int i = 0; i < numeral_count; i++) {
            if (numeral_values[i] <= number) {
                len += (int)strlen(numeral_strings[i]);
                number -= numeral_values[i];
                break;
            }
        }
    }
    return len;
}

long long solve(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <file_url>\n", argv[0]);
        return -1;
    }

    char *text = get_text_file(argv[1]);
    if (!text) return -1;

    long long characters_saved = 0;
    char *ptr = text;
    while (*ptr) {
        /* Skip any leading newline/carriage-return characters */
        while (*ptr == '\r' || *ptr == '\n') ptr++;
        if (*ptr == '\0') break;

        /* Find end of line */
        char *end = ptr;
        while (*end && *end != '\r' && *end != '\n') end++;

        int original_len = (int)(end - ptr);
        if (original_len > 0) {
            int number = roman_to_number(ptr, original_len);
            int minimal_len = number_as_roman_numeral_length(number);
            characters_saved += original_len - minimal_len;
        }
        ptr = end;
    }

    free(text);
    return characters_saved;
}

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