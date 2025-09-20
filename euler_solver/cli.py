#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Command line interface for Project Euler problems. """
from __future__ import annotations

from euler_solver.args import parse_args
from euler_solver.framework import (EvaluationResult, MAX_SHARABLE, Mode, create_summary, evaluate_range,
                                    get_key, lock_private_files, logger, set_evaluation_options, set_show_solution,
                                    set_use_py_func, unlock_private_files)

__all__ = ['main']


def main() -> int:
    start_number, end_number, args = parse_args()

    if end_number > MAX_SHARABLE:
        try:
            get_key()
        except RuntimeError:
            logger.error('Missing EULER_ENCRYPTION_KEY')
            return 1

    if args.lock:
        for euler_problem in range(start_number, end_number + 1):
            lock_private_files(euler_problem)
        return 0

    if args.unlock:
        for euler_problem in range(start_number, end_number + 1):
            unlock_private_files(euler_problem)
        return 0

    if args.setup:
        from euler_solver.framework.module import setup_solution_templates
        max_async: int = min(8, args.workers or 8)
        setup_solution_templates(start_number, end_number, force_update_doc=False, max_async=max_async)
        return 0

    if args.summary:
        create_summary(history_file='history/history.csv', problems_file='history/pe_minimal_problems.csv')
        return 0

    mode: Mode = Mode.evaluate
    num_workers: int | None = args.workers
    match args.mode:
        case 'evaluate':
            mode = Mode.evaluate
            set_evaluation_options(eval_dev=False, eval_main=True, eval_extra=False, ignore_slices=args.ignore_slices)
        case 'evaluate-extended':
            mode = Mode.evaluate
            set_evaluation_options(eval_dev=True, eval_main=True, eval_extra=True, ignore_slices=args.ignore_slices)
        case 'evaluate-dev':
            mode = Mode.evaluate
            set_evaluation_options(eval_dev=True, eval_main=False, eval_extra=False, ignore_slices=args.ignore_slices)
        case 'list':
            mode = Mode.list
            num_workers = 1
            set_evaluation_options(eval_dev=True, eval_main=True, eval_extra=True, ignore_slices=args.ignore_slices)
        case 'record':
            mode = Mode.record
            set_evaluation_options(eval_dev=True, eval_main=True, eval_extra=False, ignore_slices=args.ignore_slices)
        case 'record-all':
            mode = Mode.record
            set_evaluation_options(eval_dev=True, eval_main=True, eval_extra=True, ignore_slices=args.ignore_slices)
    set_show_solution(show=args.show)
    set_use_py_func(use_py_func=args.use_py)
    evaluation_result: EvaluationResult = evaluate_range(
            start_number=start_number,
            end_number=end_number,
            mode=mode,
            num_workers=num_workers,
            time_out_in_seconds=args.timeout,
    )
    return evaluation_result.failed_problems


if __name__ == '__main__':
    raise SystemExit(main())
