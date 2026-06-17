/* Solution to Euler Problem 22: Names Scores. */
#include "runner.h"



/* Alphabetical word value: sum of letter positions (A=1 .. Z=26), skipping quotes/spaces. */
static int word_to_num(const char *word) {
    int sum = 0;
    for (const char *c = word; *c; c++) {
        if (*c == '"' || *c == ' ') continue;
        sum += (*c - 64);
    }
    return sum;
}

/* qsort comparator: lexicographic order on the raw quoted tokens. */
static int cmp_str(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

/* Sort the names, then sum each name's word value weighted by its 1-based rank; O(n log n). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    const char *file_url = argv[1];

    char *text = get_text_file(file_url);
    if (!text) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    /* Count commas to estimate number of names */
    int count = 1;
    for (char *p = text; *p; p++) {
        if (*p == ',') count++;
    }

    char **names = malloc((size_t)count * sizeof(char *));
    if (!names) { free(text); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    /* Split by comma */
    int n = 0;
    char *token = strtok(text, ",");
    while (token) {
        names[n++] = token;
        token = strtok(NULL, ",");
    }

    /* Sort alphabetically */
    qsort(names, (size_t)n, sizeof(char *), cmp_str);

    long long total = 0;
    for (int i = 0; i < n; i++) {
        long long score = (long long)(i + 1) * word_to_num(names[i]);
        total += score;
    }

    free(names);
    free(text);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}
