#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
from functools import wraps
from multiprocessing import Pool, Process, TimeoutError
from time import sleep, time
from typing import Any, Callable, Dict, List, TypeVar, Tuple

import psutil

T = TypeVar('T')
V = TypeVar('V')

__all__ = ('evaluate_with_timeout', 'Watchdog')


def __evaluate_function__(func: Callable[[Any], T], *args, **kwargs) -> Tuple[T, float]:
    answer = kwargs.pop('answer', None)
    func_str = '{0}({1})='.format(func.__name__, ', '.join(
        [str(arg) for arg in args] + [str(k) + '=' + str(v) for k, v in kwargs.items()]))
    print(func_str, end='')
    st = time()
    result = func(*args, **kwargs)
    rt = time() - st
    print(result, end='')
    print('|calculated in {:.6f} seconds'.format(rt), end='')
    check_str = '' if answer is None else \
        '{0:9s}|\033[0m expected {1}'.format('\033[34m|ok' if answer == result else '\033[31m|err', answer)
    print(check_str)
    return result, rt


def evaluate_with_timeout(func: Callable[[Any], T], *args, **kwargs) -> T:
    timeout = kwargs.pop('timeout', 300)
    args = (func,) + args
    with Pool(processes=1) as pool:
        job = pool.apply_async(func=__evaluate_function__, args=args, kwds=kwargs)
        try:
            result = job.get(timeout=timeout)
        except TimeoutError:
            print('\033[31m timeout {} seconds \033[0m'.format(timeout))
        else:
            return result[0]


def __delayed_exit__(delay: int, pid: int) -> None:
    if delay != 0:
        sleep(delay)
        print('\033[31m watchdog timed out, going to kill process\033[0m')
        psutil.Process(pid=pid).terminate()


class Watchdog(object):
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.watchdog = Process(target=__delayed_exit__, args=(self.timeout, psutil.Process().pid))

    def __enter__(self):
        self.watchdog.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.watchdog.terminate()
        self.watchdog.join()
        self.watchdog.close()

    def reset(self):
        self.watchdog.terminate()
        self.watchdog.join()
        self.watchdog.close()
        self.watchdog = Process(target=__delayed_exit__, args=(self.timeout, psutil.Process().pid))
        self.watchdog.start()

    @staticmethod
    def evaluate(func: Callable[[Any], T]) -> Callable[[Any], T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return __evaluate_function__(func, *args, **kwargs)[0]

        return wrapper

    @staticmethod
    def evaluate_range(func: Callable[[V], T], answers: Dict) -> List[Tuple[V, T]]:
        result = tuple((arg,) + __evaluate_function__(func, arg, answer=answer) for arg, answer in answers.items())
        print('\nExecution Time Info :{}'.format([(r[0], r[2]) for r in result]))
        result = [(r[0], r[1]) for r in result]
        print('Result\t\t\t\t:{}'.format(result))
        return result

    @staticmethod
    def evaluate_compare(funcs: (Callable[[V], T], ...), answers: Dict) -> List[Tuple[V, Tuple[T, ...]]]:
        result = tuple((arg,) + tuple(__evaluate_function__(func, arg, answer=answer) for func in funcs)
                       for arg, answer in answers.items())
        print('\nExecution Time Info :{}'.format([(r[0], tuple(rr[1] for rr in r[1:])) for r in result]))
        result = [(r[0], tuple(rr[0] for rr in r[1:])) for r in result]
        print('Result\t\t\t\t:{}'.format(result))
        return result


if __name__ == '__main__':
    from os import chdir, listdir, system
    from os.path import dirname

    chdir(working_dir := dirname(__file__))
    for solution in (s for s in sorted(listdir(path=working_dir)) if s.endswith('.py') and s[0] in ('0', '1')):
        print(solution[:-3])
        if exit_code := system('python -m "{}.{}"'.format(__package__, solution[:-3])) != 0:
            exit(exit_code)
        print('\n')
