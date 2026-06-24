/* Solution to Euler Problem 85: Counting Rectangles. */
#include "runner.h"

/* Triangular number T(length) = length*(length+1)/2: the count of rectangles along one axis,
 * since choosing 2 of length+1 grid lines gives C(length+1, 2). */
static int triangular(int length) {
    return length * (length + 1) / 2;
}

/* Binary search: find leftmost index in numbers[0..len-1] where numbers[idx] >= x.
 * Returns len if all elements are < x. */
static int bisect_left(int *numbers, int len, int x) {
    int lo = 0, hi = len;
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        if (numbers[mid] < x) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

/* Triangular-number binary search: rectangle count factors as T(H)*T(W), so for each width W
 * binary-search the sorted triangular numbers for the height whose product is nearest target,
 * inspecting the two neighbours of the insertion point; O(max_side * log max_side). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_error = parse_int(argv[1]);
    int max_side  = parse_int(argv[2]);
    int target    = parse_int(argv[3]);

    int len_numbers = max_side - 1;  /* lengths 1 .. max_side-1 */
    int *numbers = malloc((size_t)len_numbers * sizeof(int));
    if (!numbers) {
        fprintf(stderr, "out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    for (int i = 0; i < len_numbers; i++) {
        numbers[i] = triangular(i + 1);  /* numbers[i] = T(i+1) */
    }

    int best_area  = -1;
    int best_delta = -1;
    int last_num   = 0;

    for (int width = 1; width <= len_numbers; width++) {
        int num_width = numbers[width - 1];
        if (num_width == 0) continue;

        /* find insertion point for target / num_width (integer division is fine:
         * the two bracketing neighbours still contain the true closest value) */
        int q = target / num_width;
        int j = bisect_left(numbers, len_numbers, q);

        /* check candidates j+1 and j+2 (1-indexed heights) */
        for (int k = 0; k <= 1; k++) {
            int height = j + 1 + k;  /* 1-indexed */
            if (height >= 1 && height <= len_numbers) {
                int num = numbers[height - 1] * num_width;
                int d   = abs(num - target);
                last_num = num;
                if (best_delta < 0 || d < best_delta) {
                    best_delta = d;
                    best_area  = height * width;
                }
            }
        }

        if (best_delta >= 0 && best_delta <= max_error) {
            break;
        }
    }

    (void)last_num;
    free(numbers);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)best_area)); return _answer; }
}