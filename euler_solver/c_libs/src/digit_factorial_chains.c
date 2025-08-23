/*******************************************************************************
 * File: digit_factorial_chains.c
 *
 * Description: Implementation of digit factorial chains calculator that finds
 *              chains where the sum of factorial of digits leads to loops.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include "digit_factorial_chains.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Precomputed factorials for digits 0-9
static const int digit_factorials[] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

// Function to compute the sum of digit factorials for a given number
static int sum_of_digit_factorials(int n) {
    int result = 0;
    while (n > 0) {
        result += digit_factorials[n % 10];
        n /= 10;
    }
    return result;
}

int count_digit_factorial_max_length_chains(int max_num, int *max_chain_length, int *max_chain_length_count) {
    if (max_num < 2 || !max_chain_length || !max_chain_length_count) {
        return -1; // Invalid input
    }

    int *chain_length_cache = (int *)calloc(max_num + 1, sizeof(int));
    int *graph = (int *)calloc(max_num + 1, sizeof(int));

    if (!chain_length_cache) {
        fprintf(stderr, "Error: Failed to allocate memory for chain_length_cache.\n");
        free(graph);
        return -1;
    }
    if (!graph) {
        fprintf(stderr, "Error: Failed to allocate memory for graph.\n");
        free(chain_length_cache);
        return -1;
    }
        free(chain_length_cache);
        free(graph);
        return -1; // Memory allocation failure
    }

    *max_chain_length = 0;
    *max_chain_length_count = 0;

    for (int start = 2; start <= max_num; ++start) {
        int seen[512]; // Temporary array to track visited numbers, increased size for safety
        int seen_count = 0;
        int current = start;

        // Chain generation until a loop or cache hit is found
        while (current < max_num && chain_length_cache[current] == 0) {
            if (seen_count >= 512) {
                fprintf(stderr, "Error: Exceeded maximum chain length capacity.\n");
                free(chain_length_cache);
                free(graph);
                return -1;
            }
            seen[seen_count++] = current;
            if (current >= max_num) {
                break;
            }
            if (graph[current] == 0) {
                graph[current] = sum_of_digit_factorials(current);
            }
            current = graph[current];
        }

        int chain_length = 0;
        if (current <= max_num && chain_length_cache[current] > 0) {
            chain_length = chain_length_cache[current];
        } else {
            chain_length = seen_count; // Length is all non-repeating terms
        }

        // Propagate chain lengths back to all numbers in 'seen'
        for (int i = 0; i < seen_count; ++i) {
            chain_length_cache[seen[i]] = chain_length - i;
            graph[seen[i]] = (i + 1 < seen_count) ? seen[i + 1] : current;
        }

        // Update max_chain_length and max_chain_length_count
        if (chain_length_cache[start] > *max_chain_length) {
#include "digit_factorial_chains.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Precomputed factorials for digits 0-9
static const int digit_factorials[] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

// Function to compute the sum of digit factorials for a given number
static int sum_of_digit_factorials(int n) {
    int result = 0;
    while (n > 0) {
        result += digit_factorials[n % 10];
        n /= 10;
    }
    return result;
}

int count_digit_factorial_max_length_chains(int max_num, int *max_chain_length, int *max_chain_length_count) {
    if (max_num < 2 || !max_chain_length || !max_chain_length_count) {
        return -1; // Invalid input
    }

    int *chain_length_cache = (int *)calloc(max_num + 1, sizeof(int));
    int *graph = (int *)calloc(max_num + 1, sizeof(int));

    if (!chain_length_cache || !graph) {
        if (chain_length_cache) free(chain_length_cache);
        if (graph) free(graph);
        return -1; // Memory allocation failure
    }

    *max_chain_length = 0;
    *max_chain_length_count = 0;

    for (int start = 2; start <= max_num; ++start) {
        int seen[512]; // Temporary array to track visited numbers, increased capacity
        int seen_count = 0;
        int current = start;

        // Chain generation until a loop or cache hit is found
        while (current < max_num && chain_length_cache[current] == 0) {
            if (seen_count >= 512) {
                fprintf(stderr, "Error: Exceeded maximum chain length capacity.\n");
                free(chain_length_cache);
                free(graph);
                return -1;
            }
            seen[seen_count++] = current;
            if (current >= max_num) {
                break;
            }
            if (graph[current] == 0) {
                graph[current] = sum_of_digit_factorials(current);
            }
            current = graph[current];
        }

        int chain_length = 0;
        if (current <= max_num && chain_length_cache[current] > 0) {
            chain_length = chain_length_cache[current];
        } else {
            chain_length = seen_count; // Length is all non-repeating terms
        }

        // Propagate chain lengths back to all numbers in 'seen'
        for (int i = 0; i < seen_count; ++i) {
            chain_length_cache[seen[i]] = chain_length - i;
            graph[seen[i]] = (i + 1 < seen_count) ? seen[i + 1] : current;
        }

        // Update max_chain_length and max_chain_length_count
        if (chain_length_cache[start] > *max_chain_length) {
#include "digit_factorial_chains.h"
#include <stdio.h>
#include <stdlib.h>

// Precomputed factorials for digits 0-9
static const int digit_factorials[] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

// Function to compute the sum of digit factorials for a given number
int sum_of_digit_factorials(int n) {
    int result = 0;
    while (n > 0) {
        result += digit_factorials[n % 10];
        n /= 10;
    }
    return result;
}

int count_digit_factorial_max_length_chains(int max_num, int *max_chain_length, int *max_chain_length_count) {
    if (max_num < 2 || !max_chain_length || !max_chain_length_count) {
        return -1; // Invalid input
    }

    int *chain_length_cache = (int *)calloc(max_num + 1, sizeof(int));
    int *graph = (int *)calloc(max_num + 1, sizeof(int));

    if (chain_length_cache == NULL || graph == NULL) {
        free(chain_length_cache);
        free(graph);
        return -1; // Memory allocation failure
    }

    *max_chain_length = 0;
    *max_chain_length_count = 0;

    for (int start = 2; start <= max_num; ++start) {
        int seen[512]; // Temporary array to track visited numbers
        int seen_count = 0;
        int current = start;

        // Chain generation until a loop or cache hit is found
        while (current < max_num && chain_length_cache[current] == 0) {
            if (seen_count >= 512) {
                fprintf(stderr, "Error: Exceeded maximum chain length capacity.\n");
                free(chain_length_cache);
                free(graph);
                return -1;
            }
            seen[seen_count++] = current;
            if (graph[current] == 0) {
                graph[current] = sum_of_digit_factorials(current);
            }
            current = graph[current];
        }

        int chain_length = 0;
        if (current <= max_num && chain_length_cache[current] > 0) {
            chain_length = chain_length_cache[current];
        } else {
            chain_length = seen_count; // Length is all non-repeating terms
        }

        // Propagate chain lengths back to all numbers in 'seen'
        for (int i = 0; i < seen_count; ++i) {
            chain_length_cache[seen[i]] = chain_length - i;
            graph[seen[i]] = (i + 1 < seen_count) ? seen[i + 1] : current;
        }

        // Update max_chain_length and max_chain_length_count
        if (chain_length_cache[start] > *max_chain_length) {
            *max_chain_length = chain_length_cache[start];
            *max_chain_length_count = 1;
        } else if (chain_length_cache[start] == *max_chain_length) {
            (*max_chain_length_count)++;
        }
    }

    free(chain_length_cache);
    free(graph);
    return 0; // Success
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <max_num>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int max_num = atoi(argv[1]);
    if (max_num < 2) {
        fprintf(stderr, "Error: max_num must be >= 2.\n");
        return EXIT_FAILURE;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    int result = count_digit_factorial_max_length_chains(max_num, &max_chain_length, &max_chain_length_count);
    if (result != 0) {
        fprintf(stderr, "Error: Failed to compute digit factorial chains.\n");
        return EXIT_FAILURE;
    }

    printf("max_num=%d max_chain_length=%d max_chain_length_count=%d\n", max_num, max_chain_length, max_chain_length_count);
    return EXIT_SUCCESS;
}
    if (max_num < 2) {
        fprintf(stderr, "Error: max_num must be >= 2.\n");
        return EXIT_FAILURE;
    }

    // Variables to store the results
    int max_chain_length = 0;
    int max_chain_length_count = 0;

    // Call core function
    int result = count_digit_factorial_max_length_chains(max_num, &max_chain_length, &max_chain_length_count);
    if (result != 0) {
        fprintf(stderr, "Error: Failed to compute digit factorial chains.\n");
        return EXIT_FAILURE;
    }

    // Print results
    printf("max_num=%d max_chain_length=%d max_chain_length_count=%d\n", max_num, max_chain_length, max_chain_length_count);
    return EXIT_SUCCESS;
}
        fprintf(stderr, "Error: max_num must be >= 2.\n");
        return EXIT_FAILURE;
    }

    int max_chain_length = 0;
    int max_chain_length_count = 0;

    int result = count_digit_factorial_max_length_chains(max_num, &max_chain_length, &max_chain_length_count);
    if (result != 0) {
        fprintf(stderr, "Error: Failed to compute digit factorial chains.\n");
        return EXIT_FAILURE;
    }

    printf("max_num=%d max_chain_length=%d max_chain_length_count=%d\n", max_num, max_chain_length, max_chain_length_count);
    return EXIT_SUCCESS;
}