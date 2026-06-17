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

    loop     → Any             current loop value (read-only; driven by
                               :meth:`loop_through_iterable`; None outside a loop)
    problem  → Problem | None  the workspace problem, as an object   (shell-settable)
    rcode    → int             exit code of the most recent evaluation (shell-settable)
    reserved → list[str]       sorted list of every reserved name     (read-only)
    problems → list[Problem]   every known problem                    (read-only)
    next     → int             number of the next unsolved problem    (computed)
    random   → int             number of a random unsolved problem    (computed)
    solved   → list[Problem]   the solved problems                    (computed)
    unsolved → list[Problem]   the unsolved problems                  (computed)
    stale    → list[Problem]   the stale problems                     (computed)

The *computed* specials are callables, invoked by the interpreter at each `{…}`
reference, so their value reflects current progress on every use.
"""
from __future__ import annotations

__all__ = ['Variables', 'refresh_workspace_vars', 'variables']

import functools
import os
import random
import signal
from types import FrameType
from typing import Any, Callable, Generator, Iterable, cast

from solver.config import Singleton
from solver.core.problems import Problem, problems
from solver.shell.tty import console


class Variables(metaclass=Singleton):
    """The interpreter's name store (a singleton; use the `variables` instance).

    The instance `__dict__` *is* the backing store, so reserved names live
    alongside user names in a single mapping the interpreter resolves by item
    access. Protection is layered on top: the item-access dunders guard the
    *assign* channel, while the statically defined per-name properties guard
    the *set* channel.
    """

    __slots__ = ('__dict__', '__reserved__')

    def __init__(self) -> None:
        self.__dict__: dict[str, Any] = {
            'loop': None,
            'problem': None,
            'rcode': 0,
            'reserved': [],
            'next': lambda: next(
                (p for p in problems.problems_list if p not in problems.solved_problems),
                problems.problems_list[-1]
            ).number,
            'random': lambda: random.choice(
                [p for p in problems.problems_list if p not in problems.solved_problems] or problems.problems_list
            ).number,
            'problems': problems.problems_list,
            'solved': lambda: problems.solved_problems,
            'unsolved': lambda: problems.not_solved_problems,
            'stale': lambda: problems.stale_problems,
        }
        self.__reserved__: set[str] = set(self.__dict__.keys())
        self.__dict__['reserved'] = sorted(self.__reserved__)
        _install_parent_trigger()

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
    def problem(self) -> Problem | None:
        """The current problem, exposed as `problem`."""
        return cast(Problem | None, self.__dict__['problem'])

    @problem.setter
    def problem(self, value: Problem | None) -> None:
        """The current problem, exposed as `problem`."""
        self.__dict__['problem'] = value

    @property
    def rcode(self) -> int:
        """The return code, exposed as `rcode`."""
        return cast(int, self.__dict__['rcode'])

    @rcode.setter
    def rcode(self, value: int) -> None:
        """The return code, exposed as `rcode`."""
        assert isinstance(value, int), f'rcode must be an int, not {value!r}'
        self.__dict__['rcode'] = value

    def refresh_workspace_vars(self) -> None:
        """Sync the `problem` special from the current workspace problem."""
        self.problem = Problem.from_workspace()


# ---------------------------------------------------------------------------
# Cross-process workspace-var refresh
#
# The interactive shell owns the workspace flock (lock_state.acquired) for its
# whole session; the children it spawns (the web server, claude-skill) inherit
# that lock (lock_state.inherited) and carry the owner's PID in lock_state. When
# a child mutates the workspace it re-syncs its own vars, then signals the owner
# so the otherwise-idle parent shell re-runs refresh_workspace_vars() too.
#
# The SIGUSR1 handler is installed once, at Variables construction (import time),
# in every process: this replaces SIGUSR1's default "terminate" before any child
# can send the nudge, and avoids depending on lock state that is not yet known at
# import. Only the lock owner is ever signalled (see _notify_parent), so a handler
# sitting idle in a non-owner process is harmless.
# ---------------------------------------------------------------------------
_parent_trigger_installed: bool = False


def _on_workspace_changed(signum: int, frame: FrameType | None) -> None:
    """SIGUSR1 handler: re-sync vars after a child changed the workspace."""
    variables.refresh_workspace_vars()


def _install_parent_trigger() -> None:
    """Install the SIGUSR1 handler once (called from Variables.__init__)."""
    global _parent_trigger_installed
    if _parent_trigger_installed:
        return
    try:
        signal.signal(signal.SIGUSR1, _on_workspace_changed)
    except ValueError:
        return  # not the main thread — a signal handler cannot be installed here
    _parent_trigger_installed = True


def _notify_parent() -> None:
    """From a child holding an inherited lock, nudge the owner shell to re-sync its vars."""
    from solver.core.lock import lock_state  # local import to avoid circular import
    if lock_state.inherited and lock_state.pid_of_holder:
        try:
            os.kill(lock_state.pid_of_holder, signal.SIGUSR1)
        except OSError:
            pass  # owner already gone; nothing left to refresh


variables = Variables()


def refresh_workspace_vars[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        finally:
            variables.refresh_workspace_vars()
            console.print(f'[primary]Workspace '
                          f'{'is empty' if variables.problem is None else f'has {variables.problem.as_title()}'}'
                          f'[/primary]')
            _notify_parent()

    wrapper.__refresh_workspace_vars__ = True  # type: ignore[attr-defined]
    return wrapper
