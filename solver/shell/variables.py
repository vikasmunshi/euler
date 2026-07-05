#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Variable store for shell v2.

A single, process-wide :class:`Variables` instance (the module-level
`variables` singleton) holds every name the interpreter can resolve.  In a
command block, names are referenced with `{name}`; the **interpreter** reads the
value through item access (`variables[name]`) and substitutes it while evaluating
a statement (see `interpreter.py` and `docs/syntax.md` §2). Substitution itself lives
in the interpreter, not here — this module only stores and guards the names.

Two distinct write channels (see `docs/syntax.md` — *"restricted/specials,
separate set and assign"*):

* **assign** — item access, `variables['x'] = v`.  This is the *user* channel
  used by the interpreter for `name = expr` assignments.  Reserved names are
  rejected here, so user code can never clobber a special.
* **set** — attribute access, `variables.problem = v`.  This is the *shell*
  channel for the settable specials (`problem`, `rcode`), exposed as
  read-write properties; the read-only specials (e.g. the loop value `loop`,
  which only :meth:`loop_through_iterable` may move) have no setter.

Reserved variables seeded at construction:

    config   → Config          the global configuration singleton     (read-only)
    loop     → Any             current loop value (read-only; driven by
                               :meth:`loop_through_iterable`; None outside a loop)
    problem  → Problem | None  the current problem, as an object      (shell-settable)
    rcode    → int             exit code of the most recent evaluation (shell-settable)
    reserved → list[str]       sorted list of every reserved name     (read-only)
    problems → list[Problem]   every known problem                    (computed)
    next     → int             number of the next unsolved problem    (computed)
    random   → int             number of a random unsolved problem    (computed)
    solved   → list[Problem]   the solved problems                    (computed)
    unsolved → list[Problem]   the unsolved problems                  (computed)

The *computed* specials are callables, invoked by the interpreter at each `{…}`
reference, so their value reflects current progress on every use.
"""
from __future__ import annotations

__all__ = ['Variables', 'variables']

from typing import Any, Generator, Iterable, cast

from solver.config import config
from solver.core.problems import Problem, problems


class Variables():
    """The interpreter's name store (a singleton; use the `variables` instance).

    The instance `__dict__` *is* the backing store, so reserved names live
    alongside user names in a single mapping the interpreter resolves by item
    access. Protection is layered on top: the item-access dunders guard the
    *assign* channel, while the statically defined per-name properties guard
    the *set* channel.
    """

    __slots__ = ('__dict__', '__reserved__')
    problems: list[Problem]
    solved: list[Problem]
    unsolved: list[Problem]
    last: int
    next: int
    random: int

    def __init__(self) -> None:
        self.__dict__: dict[str, Any] = {
            'config': config,
            'loop': None,
            'problem': None,
            'rcode': 0,
            'last': lambda: problems.last_solved_problem.number,
            'next': lambda: problems.next_unsolved_problem.number,
            'random': lambda: problems.random_problem.number,
            'problems': lambda: problems.problems_list,
            'solved': lambda: problems.solved_problems,
            'unsolved': lambda: problems.unsolved_problems,
            'reserved': [],
        }
        self.__reserved__: set[str] = set(self.__dict__.keys())
        self.__dict__['reserved'] = sorted(self.__reserved__)

    # -- assign channel (user variables; reserved names rejected) -----------

    def __getitem__(self, name: str) -> Any:
        return self.__dict__[name]

    def __setitem__(self, name: str, value: Any) -> None:
        if name in self.__reserved__:
            raise KeyError(f'Variable {name} is reserved')
        self.__dict__[name] = value

    def __delitem__(self, name: str) -> None:
        if name in self.__reserved__:
            raise KeyError(f'Variable {name} is reserved')
        del self.__dict__[name]

    def __contains__(self, name: str) -> bool:
        return name in self.__dict__

    # -- introspection ------------------------------------------------------

    def vars(self) -> Generator[str, None, None]:
        """Yield every name in the store (reserved specials included)."""
        yield from self.__dict__.keys()

    def vals(self) -> Generator[Any, None, None]:
        """Yield every stored value."""
        yield from self.__dict__.values()

    def items(self) -> Generator[tuple[str, Any], None, None]:
        """Yield every `(name, value)` pair."""
        yield from self.__dict__.items()

    def loop_through_iterable(self, values: Iterable[Any] | None = None) -> Generator[Any, None, None]:
        """Iterate *values*, exposing each as the loop value `loop`.

        For every value, `loop` is set and the value yielded, so the caller
        can run the loop body once per value with `{loop}` resolving to the
        current one:

            for _ in variables.loop_through_iterable(problem_list):
                ...  # body sees the current value as {loop}

        `None` or an empty *values* runs the body exactly once with
        `loop is None`. `loop` is restored to `None` when iteration finishes
        or the generator is closed.
        """
        try:
            for value in (values or [None]):
                self.__dict__['loop'] = value
                yield value
        finally:
            self.__dict__['loop'] = None

    # -- defined (set channel wiring, static to satisfy mypy that complains on dynamic wiring) --

    @property
    def loop(self) -> Any:
        """The current loop value, exposed as `loop` in the body of
        :meth:`loop_through_iterable` (`None` outside a loop)."""
        return self.__dict__['loop']

    @property
    def problem(self) -> Problem:
        """The current problem, exposed as `problem`."""
        if self.__dict__['problem'] is None:
            self.__dict__['problem'] = problems.last_solved_problem
        return cast(Problem, self.__dict__['problem'])

    @problem.setter
    def problem(self, problem: Problem) -> None:
        """The current problem, exposed as `problem`."""
        if not isinstance(problem, Problem):
            raise TypeError(f'problem must be a Problem, not {problem!r}')
        self.__dict__['problem'] = problem

    def set_problem(self, problem_number: int) -> None:
        """Set the active `problem` by number; raises ValueError if it is unknown."""
        self.problem = Problem.from_number(problem_number)

    @property
    def rcode(self) -> int:
        """The return code, exposed as `rcode`."""
        return cast(int, self.__dict__['rcode'])

    @rcode.setter
    def rcode(self, value: int) -> None:
        """The return code, exposed as `rcode`."""
        if not isinstance(value, int):
            raise TypeError(f'rcode must be an int, not {value!r}')
        self.__dict__['rcode'] = value


variables = Variables()
