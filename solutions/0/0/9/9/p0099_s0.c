/* Solution to Euler Problem 99: Largest Exponential. */
#include "runner.h"
#include <math.h>


/* Rank each base^exp by the monotone surrogate exp*log(base) and take the argmax; O(N) over lines. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <file_url>\n", argv[0]);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    char *content = get_text_file(argv[1]);
    if (!content) {
        fprintf(stderr, "Error: could not load file\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Running argmax: best log value and the 1-based line that produced it. */
    int max_i = 0;
    double max_val = 0.0;
    int line_num = 0;

    char *saveptr = NULL;
    char *line = strtok_r(content, "\n", &saveptr);
    while (line != NULL) {
        /* Strip carriage return if present */
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\r') {
            line[len - 1] = '\0';
            len--;
        }

        if (len == 0) {
            line = strtok_r(NULL, "\n", &saveptr);
            continue;
        }

        line_num++;

        char *comma = strchr(line, ',');
        if (!comma) {
            fprintf(stderr, "Warning: Could not parse line %d: '%s'\n", line_num, line);
            line = strtok_r(NULL, "\n", &saveptr);
            continue;
        }

        *comma = '\0';
        long long base = atoll(line);
        long long exponent = atoll(comma + 1);

        if (base <= 0 || exponent <= 0) {
            fprintf(stderr, "Warning: Skipping invalid values at line %d: base=%lld, exponent=%lld\n",
                    line_num, base, exponent);
            line = strtok_r(NULL, "\n", &saveptr);
            continue;
        }

        /* log(base^exponent) = exponent * log(base): order-preserving and O(1) to evaluate. */
        double log_val = (double)exponent * log((double)base);
        if (log_val > max_val) {
            max_val = log_val;
            max_i = line_num;
        }

        line = strtok_r(NULL, "\n", &saveptr);
    }

    free(content);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)max_i)); return _answer; }
}