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

Four specials are seeded at construction, because they are the store's own state
rather than anybody's data:

    config   → Config          the global configuration singleton     (read-only)
    loop     → Any             current loop value (read-only; driven by
                               :meth:`loop_through_iterable`; None outside a loop)
    problem  → Problem | None  the current problem, as an object      (shell-settable)
    rcode    → int             exit code of the most recent evaluation (shell-settable)
    reserved → list[str]       sorted list of every reserved name     (read-only)

Everything else is **registered** with :func:`variable`, next to the code that knows
how to compute it — the problem sets below, and the live reads that other modules
declare (`open_prs` in `solver.core.git`, `threads` in the message commands). A
registered variable is a zero-argument callable, invoked by the interpreter at *each*
`{…}` reference, so its value reflects the world at the moment it is read: `{random}`
yields a fresh pick, and `{open_prs}` a queue that may have changed since the last
command. The cost is the other side of the same coin — two references in one block are
two reads — which is why an expensive one belongs in a `loop` header (evaluated once)
rather than in the body.

Registration is at import, so `solver/modules.csv` decides which variables exist, exactly
as it decides which commands do. It is also what lets one declaration serve two surfaces:
a menu (`Ask(choices='open_prs')`) and a loop (`loop {open_prs}:`) read the same list.
"""
from __future__ import annotations

__all__ = ['VariableInfo', 'Variables', 'variable', 'variables']

from dataclasses import dataclass
from typing import Any, Callable, Generator, Iterable, Literal, TypeVar, cast

from solver.config import config
from solver.core.problems import Problem, problems

#: A registered variable: no arguments, and a fresh value on every call.
Compute = Callable[[], Any]

_F = TypeVar('_F', bound=Compute)

#: How a name is written, for the reader of `docs/syntax.md` §3.
Kind = Literal['computed', 'shell-set', 'read-only']


@dataclass(frozen=True)
class VariableInfo:
    """What is known about one name: enough to document it without reading the source."""

    name: str
    kind: Kind
    #: The declared type, verbatim from the source — `list[Problem]`, `int`. Registered
    #: variables take it from the function's return annotation (a string, because this
    #: package is `from __future__ import annotations`), so it cannot drift from the code.
    type_name: str
    description: str


#: The names the store seeds itself, which no module may register over: they are the
#: interpreter's own state, and their writers are the shell rather than a computation.
_SEEDED: dict[str, tuple[Kind, str, str]] = {
    'config': ('read-only', 'Config', 'the global configuration singleton'),
    'loop': ('shell-set', 'Any', 'the current loop value; None outside a loop'),
    'problem': ('shell-set', 'Problem | None', 'the workspace problem, as an object'),
    'rcode': ('shell-set', 'int', 'exit code of the most recently run evaluation'),
    'reserved': ('read-only', 'list[str]', 'sorted list of every reserved name'),
}


class Variables():
    """The interpreter's name store (a singleton; use the `variables` instance).

    The instance `__dict__` *is* the backing store, so reserved names live
    alongside user names in a single mapping the interpreter resolves by item
    access. Protection is layered on top: the item-access dunders guard the
    *assign* channel, while the statically defined per-name properties guard
    the *set* channel.
    """

    __slots__ = ('__dict__', '__reserved__', '__info__')
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
            'reserved': [],
        }
        self.__reserved__: set[str] = set(self.__dict__.keys())
        self.__info__: dict[str, VariableInfo] = {
            name: VariableInfo(name, kind, type_name, description)
            for name, (kind, type_name, description) in _SEEDED.items()
        }
        self.__dict__['reserved'] = sorted(self.__reserved__)

    # -- registration (the `variable` decorator's channel) -------------------

    def define(self, name: str, compute: Compute, description: str, type_name: str = '') -> None:
        """Register *compute* as the computed special *name*.

        The declared type is read from *compute*'s return annotation unless *type_name* says
        otherwise — here rather than in the decorator, so every route in records it and a
        re-registration (a test restoring what it replaced) cannot quietly lose it.

        Raises:
            KeyError: if *name* is one the store seeds itself. Those five are the
                interpreter's own state — a module that redefined `rcode` would be
                rewriting what `&&` means, from a file nobody reading a chain would think
                to look in.
        """
        if name in _SEEDED:
            raise KeyError(f'{name} is a built-in special and cannot be registered over')
        self.__dict__[name] = compute
        declared = type_name or str(compute.__annotations__.get('return', ''))
        self.__info__[name] = VariableInfo(name, 'computed', declared, description)
        self.__reserved__.add(name)
        self.__dict__['reserved'] = sorted(self.__reserved__)

    def info(self, name: str) -> VariableInfo | None:
        """What is known about *name*, or None for a user variable."""
        return self.__info__.get(name)

    def catalogue(self) -> list[VariableInfo]:
        """Every reserved name, seeded and registered, in name order.

        Read by `update-docs` to generate the table in `docs/syntax.md` §3: the set grows
        by import, so a hand-written list would be stale the first time a module declared
        one.
        """
        return sorted(self.__info__.values(), key=lambda entry: entry.name)

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


def variable(description: str) -> Callable[[_F], _F]:
    """Register the decorated zero-argument function as the shell variable of its own name.

    The counterpart of `@register` for values rather than verbs, and it keeps the same
    bargain: the function is returned unchanged, so it stays an ordinary Python callable
    that anything may call directly. *description* is what the completer shows beside the
    name and what the generated table in `docs/syntax.md` says it means; the declared
    return type is read from the annotation, so the documentation cannot drift from the code.

    Declare it beside the read it wraps, not here — a variable is a way of *naming* what
    some module already knows how to fetch::

        @variable('the open pull requests, newest first')
        def open_prs() -> list[PullRequest]:
            ...

    That one line then serves both surfaces: `loop {open_prs}:` iterates it, and
    `Ask(choices='open_prs')` offers it as a menu.

    A single **trailing underscore is stripped** from the name, which is what that
    convention is for: `{next}` and `{problems}` are the names the language wants, and
    neither is available to a function — one is a builtin, the other is already the
    problem set this module imported.
    """
    def decorate(compute: _F) -> _F:
        name = compute.__name__[:-1] if compute.__name__.endswith('_') else compute.__name__
        variables.define(name, compute, description)
        return compute
    return decorate


# ── the problem sets ────────────────────────────────────────────────────────────────────
# Registered rather than seeded, through the same door every other module uses: there is
# nothing about progress that the store itself should know.

@variable('every known problem')
def problems_() -> list[Problem]:
    return problems.problems_list


@variable('the solved problems')
def solved() -> list[Problem]:
    return problems.solved_problems


@variable('the unsolved problems')
def unsolved() -> list[Problem]:
    return problems.unsolved_problems


@variable('number of the last solved problem')
def last() -> int:
    return problems.last_solved_problem.number


@variable('number of the next unsolved problem')
def next_() -> int:
    return problems.next_unsolved_problem.number


@variable('number of a random unsolved problem')
def random() -> int:
    return problems.random_problem.number
