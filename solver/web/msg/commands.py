#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `msg` shell command: read and write the message spool.

Registered at the **reader** floor — the terminal is the front door for every rung, and
a new invitee's first need is often to ask a question. The staff verbs (`queue`,
`notice`, `dismiss`) check the caller's profile against
:data:`~solver.web.msg.identity.STAFF_FLOOR` inside the command, the same shape
`users list` uses to self-scope for a non-admin: one command, one registration, and
the ladder enforced where the verb is.

**Two channels, one renderer.** Which plane answers — the web shell's direct
`msg.sock`, or the operator's `sudo` fallback — is :mod:`solver.web.msg.client`'s
problem, not this module's. Both come back as the same JSON, and everything below
renders it identically; a `None` from the client means neither plane answered, which
:func:`_unreachable` says once for every verb.

That client is shared: `user-authorize <thread-id>` reads and answers a key-request
thread through the same two planes (:mod:`solver.crypto.keys`), which is why the call
lives beside the spool rather than inside this command.
"""
from __future__ import annotations

__all__ = ['msg']

from typing import Annotated, Any, Literal

from rich.text import Text

from solver.auth.subject import rank
from solver.config import ExitCodes, config
from solver.core import osc
from solver.shell import console, register
from solver.shell.command import Context
from solver.shell import dialogue
from solver.shell.dialogue import SKIP, Abort, Action, Ask, Choice, walk
from solver.web.msg.client import call as _call
from solver.web.msg import KEY_ISSUE_SUBJECT
from solver.web.msg.identity import STAFF_FLOOR


#: What each verb means, for the menu `msg` shows when no verb was typed. The `Literal` stays
#: the source of what is *valid*; this only says what each option does.
_ACTIONS: dict[str, str] = {
    'list': 'your threads, newest first',
    'read': 'open one thread, and mark it read',
    'save': 'take a master key a maintainer issued you',
    'send': 'ask staff a question',
    'queue': 'STAFF: work the inbound queue',
    'notice': 'STAFF: send to named recipients, or everyone',
    'dismiss': 'STAFF: drop a worked message',
}

#: The verbs that carry a message *out*, and so need a subject and a body.
_OUTBOUND: tuple[str, ...] = ('send', 'notice')
#: The verbs that name an existing thread.
_ON_THREAD: tuple[str, ...] = ('read', 'save', 'dismiss')


def _threads(_: Context, bound: dict[str, Any]) -> list[Choice]:
    """This caller's threads as menu options — the same mailbox read `msg list` prints.

    Always the mailbox, for every thread verb. `dismiss` used to read the *staff queue*, which
    holds inbound questions only (`store.inbound` filters on `kind == 'inbound'`), so a notice
    could be listed by `msg list` and still leave `msg dismiss` saying "no messages". The
    mailbox is also the wider set for staff — `_visible_to` lets them see inbound threads too —
    and it is exactly what the service will accept: staff may dismiss anything, anyone else a
    thread they are a party to.

    `save` narrows to the threads that actually carry a key, which is otherwise something the
    user has to spot among a page of ids. An empty result names *why* it is empty, since that
    is more use than a menu with nothing in it.
    """
    action = str(bound.get('action') or '')
    result = _call('mailbox')
    if result is None or result[0] != 200 or not isinstance(result[1], dict):
        return []
    threads: list[dict[str, Any]] = result[1].get('threads') or []
    if action == 'save':
        threads = [thread for thread in threads if thread.get('subject') == KEY_ISSUE_SUBJECT]
        if not threads:
            raise Abort('no message carries a master key — ask a maintainer to issue one '
                        '(`user` files the request)', rc=ExitCodes.EXIT_ERROR)
    if not threads:
        raise Abort(f'no messages to {action or "act on"}', rc=ExitCodes.EXIT_ERROR)
    return [
        Choice(str(thread.get('id', '')), str(thread.get('subject', '')),
               f'{str(thread.get("author_name", ""))} · {_when(str(thread.get("updated", "")))}'
               + (' · unread' if thread.get('unread') else ''))
        for thread in threads
    ]


#: The wire form for "everyone", which the service resolves to every mapped identity.
_EVERYONE: str = '*'


def _recipients(_: Context, bound: dict[str, Any]) -> list[Choice]:
    """Who a notice can go to: everyone, plus the known accounts when they can be read.

    The roster is an admin-plane read, so a maintainer without sudo (or a web shell, which
    cannot sudo at all) gets only the `everyone` option — which is why the menu is not strict:
    identities can always be typed instead, comma-separated. Never raises; an unreadable
    roster is a shorter menu, not a failed notice.
    """
    options = [Choice(_EVERYONE, 'everyone', 'every mapped identity')]
    try:
        from solver.web.auth.commands import account_identities
        options.extend(Choice(identity) for identity in account_identities())
    except Exception:                                        # noqa: BLE001 — a menu, not a gate
        pass
    return options


def _needs_recipients(bound: dict[str, Any]) -> bool:
    """Whether a notice still needs telling who it goes to (`--all-users` already says so)."""
    return bound.get('action') == 'notice' and not bound.get('all_users')


def _needs_thread(bound: dict[str, Any]) -> bool:
    """Whether the chosen verb names a thread."""
    return bound.get('action') in _ON_THREAD


def _is_outbound(bound: dict[str, Any]) -> bool:
    """Whether the chosen verb carries a message out, and so needs something to say."""
    return bound.get('action') in _OUTBOUND


def _unreachable() -> int:
    """The one message for "no spool answered", on either plane."""
    console.print('[error]error:[/error] the message service is not reachable '
                  '(is euler-msg.service running?)')
    return 1


def _is_staff() -> bool:
    """Whether this shell's subject is at or above the staff floor."""
    return rank(config.subject.profile) >= rank(STAFF_FLOOR)


def _refuse_below_staff(verb: str) -> int:
    console.print(f'[error]error:[/error] msg {verb} requires {STAFF_FLOOR} '
                  f'(you are {config.subject.profile})')
    return 77


# ── rendering ───────────────────────────────────────────────────────────────────────

def _when(stamp: str) -> str:
    """An ISO-8601 timestamp trimmed to the minute — the row has to fit one line."""
    return stamp[:16].replace('T', ' ')


def _print_thread_line(thread: dict[str, Any], *, show_kind: bool = True) -> None:
    """One line per thread: unread marker, id, when, who, subject."""
    mark = '[accent]●[/accent]' if thread.get('unread') else ' '
    kind = f'{thread.get("kind", ""):7} ' if show_kind else ''
    replies = len(thread.get('replies') or [])
    tail = f' [muted](+{replies})[/muted]' if replies else ''
    console.print(f'  {mark} [accent]{thread.get("id", "")}[/accent] '
                  f'[muted]{_when(str(thread.get("updated", "")))}[/muted] {kind}'
                  f'{str(thread.get("author_name", ""))[:18]:18} {thread.get("subject", "")}{tail}')


def _print_thread(thread: dict[str, Any]) -> None:
    """One message in full — there is nothing else to it."""
    console.print(f'\n[accent]{thread.get("subject", "")}[/accent]  '
                  f'[muted]({thread.get("kind", "")} · {thread.get("id", "")})[/muted]')
    console.print(f'[muted]from[/muted] {thread.get("author_name", "")}  '
                  f'[muted]{_when(str(thread.get("created", "")))}[/muted]')
    for line in str(thread.get('body') or '').splitlines():
        console.print(f'  {line}')


# ── verbs ───────────────────────────────────────────────────────────────────────────

def _list() -> int:
    """Every message this caller may read, newest first."""
    result = _call('mailbox')
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    threads = data.get('threads') or []
    if not threads:
        console.print('[muted]no messages[/muted]')
        return 0
    unread = int(data.get('unread', 0))
    console.print(f'[accent]{len(threads)}[/accent] thread(s), '
                  f'[accent]{unread}[/accent] unread — read one with `msg read <id>`')
    for thread in threads:
        _print_thread_line(thread)
    return 0


def _read(thread_id: str) -> int:
    """Show one thread and mark it read."""
    result = _call('thread', thread_id=thread_id)
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    _print_thread(data)
    _call('read', thread_id=thread_id)      # attention, not activity — failure is harmless
    osc.messages_changed()                  # the unread count just dropped
    return 0


def _send(subject: str, body: str) -> int:
    """Ask staff something."""
    result = _call('send', body={'subject': subject, 'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 201 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    console.print(f'[success]sent[/success] [muted]({data.get("id")})[/muted] — '
                  'staff will see it in their queue')
    osc.messages_changed()
    return 0


def _queue() -> int:
    """Work the inbound queue one thread at a time (staff).

    The counterpart of `users process-requests` and `gh-merge merge`, on the same
    `dialogue.walk`: each waiting thread is shown in full, then **read** it (opening the body
    and marking it read), **grant** the key it asks for (`user-authorize`, for a key request),
    **merge** the pull request it announces (`gh-merge merge`, for a push notice),
    **dismiss** it as worked, or **skip** it for now. Quitting part-way is an abort, so a
    chain gated on the queue does not carry on as though it had been worked.

    The work verbs are offered on every row rather than chosen per subject — the queue's job
    is to put the acts in reach, and which one a thread wants is plain from what it says. The
    web chip does pick per row (`solver/web/user/msg_api.py`), because a button has to name
    one verb before anybody has read anything.
    """
    result = _call('queue')
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1

    queue: list[dict[str, Any]] = data.get('queue') or []
    if not dialogue.interactive():
        # `queue` is the staff *read* verb as well as the work list, so with nobody to ask it
        # prints the list — unlike `gh-merge merge`, where quietly doing nothing would hide
        # that the merge never happened.
        if not queue:
            console.print('[muted]the inbound queue is empty[/muted]')
            return 0
        console.print(f'[accent]{len(queue)}[/accent] inbound thread(s), oldest first — '
                      'work them interactively with `msg queue`')
        for thread in queue:
            _print_thread_line(thread, show_kind=False)
        return 0

    def render(thread: dict[str, Any]) -> Text:
        line = Text('  ')
        line.append(str(thread.get('subject', '')), style='accent')
        line.append(f'\n    from {thread.get("author_name", "")} · '
                    f'{_when(str(thread.get("updated", "")))} · {thread.get("id", "")}',
                    style='muted')
        for body_line in str(thread.get('body') or '').splitlines()[:4]:
            line.append(f'\n    {body_line}')
        return line

    def grant(thread: dict[str, Any]) -> int | None:
        """Answer a key request in place — the one action this queue exists for."""
        from solver.crypto.keys import user_authorize
        return user_authorize(str(thread.get('id', '')))

    def merge(_: dict[str, Any]) -> int | None:
        """Land the pull request a `git-push` announced — `gh-merge merge`'s own walk, here.

        It takes no thread: the announcement says one is waiting, and the queue it walks is
        GitHub's. Reached only from a staff queue, whose floor (:data:`STAFF_FLOOR`) is the
        one `gh-merge` requires, so calling the command function directly grants nothing the
        caller does not already hold.

        Nor does the row need dismissing after it: `gh-merge` closes each notice it lands,
        by the branch in its subject. Merging the request this row announced therefore takes
        the row with it — so `d` here is for a notice about something merged elsewhere, or
        one whose branch was abandoned.
        """
        from solver.core.git import gh_merge
        return gh_merge('merge')

    return walk(queue,
                {'r': Action('read', lambda thread: _read(str(thread.get('id', '')))),
                 'g': Action('grant', grant),
                 'm': Action('merge', merge),
                 'd': Action('dismiss', lambda thread: _dismiss(str(thread.get('id', '')))),
                 's': Action('skip', SKIP)},
                render=render, label='inbound thread').rc


def _notice(to: str, subject: str, body: str) -> int:
    """Send a notice to named recipients, or to everyone with `--all-users`."""
    parts = [part.strip() for part in to.split(',') if part.strip()]
    targets: str | list[str] = _EVERYONE if _EVERYONE in parts else parts
    if not targets:
        raise Abort('msg notice needs `to=<email[,email…]>` or `--all-users`',
                    rc=ExitCodes.EXIT_USAGE)
    result = _call('notice', body={'to': targets, 'subject': subject, 'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 201 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    count = data.get('recipients', 0)
    console.print(f'[success]notice sent[/success] to [accent]{count}[/accent] '
                  f'recipient(s) [muted]({data.get("id")})[/muted]')
    osc.messages_changed()
    return 0


def _save(thread_id: str) -> int:
    """Write the master key delivered in *thread_id* to this machine's enc-key file.

    The receiving half of key distribution. `user-authorize` (or `key-rekey`) wraps the master
    key to your public key and sends it; this takes it. Nothing else can write that file, and
    nothing writes it without proving the payload first:

    - the thread's **subject** must be the key-issue one, so no other message can be mined
      for something that looks like key material;
    - the payload must **unwrap with your private key** and its `verify` must decrypt to the
      known text. Only then does it replace what you have.

    The message is **dismissed** once the key is written: its whole content is now in your
    enc-key file, and a spool that keeps every taken key is storing key material for nobody.

    That order matters. The file it overwrites may be the only thing standing between this
    machine and the whole private tree, so a bad or mistargeted payload has to fail *before*
    the write, not be discovered after it.
    """
    from solver.crypto.keys import save_issued_key
    result = _call('thread', thread_id=thread_id)
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    # An issued key is always its own message: with no replies there is nowhere else for it
    # to be, and one subject to check.
    if not str(data.get('subject', '')).startswith(KEY_ISSUE_SUBJECT):
        console.print(f'[error]error:[/error] message [accent]{thread_id}[/accent] does not carry '
                      'a master key — `msg save` writes key material and nothing else')
        return 1
    if not save_issued_key(str(data.get('body', ''))):
        return 1
    # Worked, so gone. A message whose whole content is now in your enc-key file has nothing
    # left to say, and leaving it would mean a mailbox that fills with keys you have already
    # taken — each one a copy of key material sitting in the spool for no reason. Failure to
    # dismiss is not failure to save: the key is written either way.
    if _call('dismiss', thread_id=thread_id) is None:
        console.print(f'[muted]Saved, but could not dismiss [accent]{thread_id}[/accent] — '
                      '`msg dismiss` it yourself.[/muted]')
    osc.messages_changed()
    return 0


def _dismiss(thread_id: str) -> int:
    """Drop a worked thread from the spool (staff)."""
    result = _call('dismiss', thread_id=thread_id)
    if result is None:
        return _unreachable()
    status, data = result
    if status != 200:
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    console.print(f'[success]dismissed[/success] [muted]({thread_id})[/muted]')
    osc.messages_changed()
    return 0


@register(requires='reader', aliases=('messages',))
def msg(action: Annotated[Literal['list', 'read', 'save', 'send', 'queue', 'notice', 'dismiss'],
                          Ask('What would you like to do?', labels=_ACTIONS)] = 'list',
        thread: Annotated[str, Ask('Which message?', choices=_threads, when=_needs_thread,
                                   empty='no messages')] = '',
        subject: Annotated[str, Ask('Subject', when=_is_outbound)] = '',
        body: Annotated[str, Ask('Message', when=_is_outbound, multiline=True)] = '',
        to: Annotated[str, Ask('Who should receive it?', choices=_recipients,
                               when=_needs_recipients, strict=False)] = '',
        all_users: bool = False) -> int:
    """Read and send messages: your threads, questions to staff, staff notices.

    Every message has staff (`maintainer`+) at one end: you can ask them something,
    they can answer, and they can send notices. There is deliberately no user-to-user
    messaging. Delivery is asynchronous — the spool holds the thread until you read it.

    Typed bare, it walks you through the rest: pick a verb, then whatever that verb needs —
    a thread from your own list, or a subject and a message. Every answer can be given on the
    command line instead, and a non-interactive shell asks nothing.

    Args:
        action: [asked] What to do — `list` your threads, newest first; `read` one thread and
            mark it read; `save` the master key a maintainer issued you, writing it to your
            enc-key file; `send` staff a question; `queue` (STAFF) work the inbound list;
            `notice` (STAFF) to named recipients or everyone; `dismiss` (STAFF) a worked
            message. Defaults to `list`.
        thread: [asked] The message to act on, for `read` / `save` / `dismiss`. Offered as a
            menu of your own threads, so the id never has to be typed out.
        subject: [asked] The subject line, for `send` / `notice`.
        body: [asked] The message text, for `send` / `notice`.
        to: [asked] Who a `notice` goes to: `*` for everyone, or one or more identities,
            comma-separated. Offered as a menu of the known accounts where the roster can be
            read.
        all_users: Send the notice to every mapped identity. Defaults to False.
    """
    if action == 'list':
        return _list()

    if action == 'queue':
        return _queue() if _is_staff() else _refuse_below_staff('queue')

    if action in _ON_THREAD and not thread:
        # Reached only non-interactively: an interactive shell was offered the menu.
        raise Abort(f'msg {action} needs a message id (see `msg list`)', rc=ExitCodes.EXIT_USAGE)

    if action == 'read':
        return _read(thread)

    if action == 'save':
        return _save(thread)

    if action == 'dismiss':
        return _dismiss(thread) if _is_staff() else _refuse_below_staff('dismiss')

    if not subject or not body:
        raise Abort(f'msg {action} needs subject="…" and body="…"', rc=ExitCodes.EXIT_USAGE)

    if action == 'send':
        return _send(subject, body)

    # notice (staff): named recipients, or every mapped identity with --all-users.
    if not _is_staff():
        return _refuse_below_staff('notice')
    return _notice('*' if all_users else to, subject, body)
