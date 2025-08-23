/*******************************************************************************
 * File: digit_factorial_chains.h
 *
 * Description: Header file for digit factorial chains calculator.
 *              Declares public functions and constants for use.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 ******************************************************************************/
#ifndef EULER_SOLVER_DIGIT_FACTORIAL_CHAINS_H
#define EULER_SOLVER_DIGIT_FACTORIAL_CHAINS_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Computes the maximum chain length and how many starting numbers (2..max_num)
 * achieve that maximum for digit factorial chains.
 *
 * Parameters:
 *  - max_num: upper bound of starting numbers (inclusive), must be >= 2
 *  - out_max_chain_length: output pointer to receive maximum chain length
 *  - out_max_chain_length_count: output pointer to receive count of starters
 *    that achieve the maximum chain length
 *
 * Returns:
 *  - 0 on success
 *  - non-zero on invalid arguments
 */
int count_digit_factorial_max_length_chains(int max_num,
                                            int *out_max_chain_length,
                                            int *out_max_chain_length_count);

#ifdef __cplusplus
}
#endif

#endif /* EULER_SOLVER_DIGIT_FACTORIAL_CHAINS_H */

