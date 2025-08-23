/*******************************************************************************
 * File: digit_factorial_chains.h
 *
 * Description: Header file for digit factorial chains calculator.
 *              Declares public functions and constants for use.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 ******************************************************************************/
#ifndef DIGIT_FACTORIAL_CHAINS_H
#define DIGIT_FACTORIAL_CHAINS_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Computes the maximum chain length and corresponding count for digit factorial chains.
// Parameters:
//   max_num - The maximum starting number (inclusive) for chain computation.
//   max_chain_length - Pointer to store the maximum chain length.
//   max_chain_length_count - Pointer to store the count of chains with the maximum length.
// Returns:
//   0 on success, non-zero on failure.
int count_digit_factorial_max_length_chains(int max_num, int *max_chain_length, int *max_chain_length_count);

#ifdef __cplusplus
}
#endif

#endif // DIGIT_FACTORIAL_CHAINS_H
