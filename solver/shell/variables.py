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

from solver.config import Singleton, config
from solver.core.lock import descendant_pids, lock_state, proc_is_solver
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
            'config': config,
            'loop': None,
            'problem': None,
            'rcode': 0,
            'next': lambda: next(
                (p for p in problems.problems_list if p not in problems.solved_problems),
                problems.problems_list[-1]
            ).number,
            'random': lambda: random.choice(
                [p for p in problems.problems_list if p not in problems.solved_problems] or problems.problems_list
            ).number,
            'problems': lambda: problems.problems_list,
            'solved': lambda: problems.solved_problems,
            'unsolved': lambda: problems.not_solved_problems,
            'stale': lambda: problems.stale_problems,
            'reserved': [],
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
        problems.clear_cache()


# ---------------------------------------------------------------------------
# Cross-process workspace-var refresh
#
# The lock owner (lock_state.acquired) holds the workspace flock for its whole
# lifetime; every shell it spawns (the web server and the PTY shells it forks,
# claude-skill) inherits that lock (lock_state.inherited) and carries the owner's
# PID in lock_state. The owner is therefore an ancestor of every sibling shell.
#
# A workspace change is propagated through the owner as a hub:
#   * the owner mutates  → it fans the nudge straight out to its descendants;
#   * a descendant mutates → it signals the owner (the single well-known PID),
#     whose handler re-syncs and then fans out to *all* descendants (the sender
#     included — a redundant but idempotent re-read), so every sibling re-syncs.
# Only the owner ever fans out (descendants merely re-sync in their handler), so
# the relay cannot loop.
#
# The SIGUSR1 handler is installed once, at Variables construction (import time),
# in every process: this replaces SIGUSR1's default "terminate" before any peer
# can send the nudge, and avoids depending on lock state that is not yet known at
# import. A handler sitting idle in a process that is neither owner nor descendant
# is harmless.
# ---------------------------------------------------------------------------
_parent_trigger_installed: bool = False


def _on_workspace_changed(signum: int, frame: FrameType | None) -> None:
    """SIGUSR1 handler: re-sync vars after a workspace change, then relay if we own the lock."""
    variables.refresh_workspace_vars()
    _broadcast_to_descendants()


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


def _broadcast_to_descendants() -> None:
    """If this process owns the workspace lock, nudge every descendant shell to re-sync.

    A no-op in any non-owner process (self-guarded on `lock_state.acquired`), so descendants
    never re-fan and the relay terminates after one hop. Only `solver` shells are signalled: a
    non-solver descendant (e.g. the `claude` child spawned by `claude-skill`, or its `sh -c`
    wrapper) has no SIGUSR1 handler, so the nudge would terminate it (`claude exited -10`).
    """
    if not lock_state().acquired:
        return
    for pid in descendant_pids(os.getpid()):
        if not proc_is_solver(pid):
            continue  # not a sibling shell — no handler installed, so the nudge would kill it
        try:
            os.kill(pid, signal.SIGUSR1)
        except OSError:
            pass  # that descendant has gone; nothing to refresh there


def _notify_peers() -> None:
    """Propagate a local workspace change to the other shells sharing the lock.

    The owner fans out to its descendants directly; a descendant routes the nudge through the
    owner, whose handler then reaches every sibling.
    """
    _lock_state = lock_state()
    if _lock_state.acquired:
        _broadcast_to_descendants()
    elif _lock_state.inherited and _lock_state.pid_of_holder:
        try:
            os.kill(_lock_state.pid_of_holder, signal.SIGUSR1)
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
            _notify_peers()

    wrapper.__refresh_workspace_vars__ = True  # type: ignore[attr-defined]
    return wrapper
