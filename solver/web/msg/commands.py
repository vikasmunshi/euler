#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `msg` shell command: read and write the message spool.

**Five verbs, one per thing a person does with a message** — `list` what is waiting,
`read` one, `send` one, `dismiss` one, and `act` on one. There were seven, and the two
extra ones were the confusing part rather than the useful part: `queue` was `list` with a
staff-only filter over a mailbox that already shows staff the queue, and `notice` was
`send` with a different recipient. Both were labelled STAFF in the menu and both refused
*after* walking a `contributor` through subject, body and recipients — a menu that offers
what it will then refuse teaches the ladder in the worst possible place. Now the ladder is
in what a verb *asks*: `to` is only asked of staff, because for everyone else there is one
possible answer.

`act` is the other half of that: `save` was a verb for one message kind, which meant the
reader had to know which of seven verbs their message wanted. A message knows what it is
for — :func:`~solver.web.msg.verb_for` decides it from the subject — so `act` takes the id
and does the thing: take the key, grant the key, merge the pull request, or, for prose,
simply read it. The header chip labels its rows from that same function, so what the button
says and what the command does cannot drift.

Registered at the **reader** floor — the terminal is the front door for every rung, and a
new invitee's first need is often to ask a question. The two acts that are staff's alone
(`authorize`, `merge`) are reachable only through :func:`~solver.web.msg.verb_for`, which
hands them out at :data:`~solver.web.msg.identity.STAFF_FLOOR` and hands everyone else a
plain read. `dismiss` is not floored here at all: the service already answers that question
better — staff may drop anything, anyone else a message they are a party to, which is what
lets `act` clean up after the key it just took.

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

from solver.auth.subject import rank
from solver.config import ExitCodes, config
from solver.core import osc
from solver.shell import console, register
from solver.shell.command import Context
from solver.shell.dialogue import Abort, Ask, Choice
from solver.web.msg.client import call as _call
from solver.web.msg import KEY_ISSUE_SUBJECT, verb_for
from solver.web.msg.identity import STAFF_FLOOR


#: What each verb means, for the menu `msg` shows when no verb was typed. The `Literal` stays
#: the source of what is *valid*; this only says what each option does. No "STAFF:" markers:
#: every verb here is one every rung can run, and the one whose *reach* widens with the
#: ladder (`send`) says so by asking staff a question it does not ask anyone else.
_ACTIONS: dict[str, str] = {
    'list': 'everything waiting for you, newest first',
    'read': 'open one message, and mark it read',
    'send': 'write to staff — or, as staff, to users',
    'dismiss': 'drop a message you are done with',
    'act': 'do what a message asks: take a key, grant one, merge a pull request',
}

#: The verbs that name an existing message.
_ON_THREAD: tuple[str, ...] = ('read', 'dismiss', 'act')

#: The wire form for "everyone", which the service resolves to every mapped identity, and
#: the word the menu offers for it — nobody should have to know that `*` is the wire.
_EVERYONE: str = '*'
_EVERYONE_LABEL: str = 'everyone'
#: The default recipient, and the only one below the staff floor: a message to the
#: maintainers and admins, which is what the spool is for.
_STAFF_LABEL: str = 'staff'


def _threads(_: Context, bound: dict[str, Any]) -> list[Choice]:
    """This caller's messages as menu options — the same mailbox read `msg list` prints.

    Always the mailbox, for every thread verb. `dismiss` used to read the *staff queue*, which
    holds inbound questions only (`store.inbound` filters on `kind == 'inbound'`), so a notice
    could be listed by `msg list` and still leave `msg dismiss` saying "no messages". The
    mailbox is also the wider set for staff — `_visible_to` lets them see inbound threads too —
    and it is exactly what the service will accept: staff may dismiss anything, anyone else a
    thread they are a party to.

    For `act` each row also names **what acting on it would do**, from the same
    :func:`~solver.web.msg.verb_for` the header chip labels its rows with. Without it the menu
    would be a list of subjects and the reader would have to guess which one carries a key.
    Only when there is something to name: `read` on every other line is the noise the label
    exists to cut through, exactly as on the chip's rows.
    """
    action = str(bound.get('action') or '')
    result = _call('mailbox')
    if result is None or result[0] != 200 or not isinstance(result[1], dict):
        return []
    threads: list[dict[str, Any]] = result[1].get('threads') or []
    if not threads:
        raise Abort(f'no messages to {action or "act on"}', rc=ExitCodes.EXIT_ERROR)
    options: list[Choice] = []
    for thread in threads:
        note = f'{str(thread.get("author_name", ""))} · {_when(str(thread.get("updated", "")))}'
        if thread.get('unread'):
            note += ' · unread'
        if action == 'act' and (verb := _verb_of(thread)) != 'read':
            note += f' · {verb}'
        options.append(Choice(str(thread.get('id', '')), str(thread.get('subject', '')), note))
    return options


def _recipients(_: Context, bound: dict[str, Any]) -> list[Choice]:
    """Who a message can go to: staff, everyone, plus the known accounts when they can be read.

    Asked of staff only (:func:`_needs_recipients`), so `staff` leads but is not the whole
    menu. The roster is an admin-plane read, so a maintainer without sudo (or a web shell,
    which cannot sudo at all) gets the two words and nothing else — which is why the menu is
    not strict: identities can always be typed instead, comma-separated. Never raises; an
    unreadable roster is a shorter menu, not a failed message.
    """
    options = [Choice(_STAFF_LABEL, _STAFF_LABEL, 'the maintainers and admins'),
               Choice(_EVERYONE_LABEL, _EVERYONE_LABEL, 'every mapped identity')]
    try:
        from solver.web.auth.commands import account_identities
        options.extend(Choice(identity) for identity in account_identities())
    except Exception:                                        # noqa: BLE001 — a menu, not a gate
        pass
    return options


def _needs_recipients(bound: dict[str, Any]) -> bool:
    """Whether this `send` has a recipient worth asking about.

    Only staff are asked. Below that floor there is exactly one possible answer — staff —
    so the question would be a menu of one, and the two other options on it would be
    offers the service then refuses. A verb must not ask what it cannot honour.
    """
    return bound.get('action') == 'send' and not bound.get('to') and _is_staff()


def _needs_thread(bound: dict[str, Any]) -> bool:
    """Whether the chosen verb names a message."""
    return bound.get('action') in _ON_THREAD


def _is_send(bound: dict[str, Any]) -> bool:
    """Whether the chosen verb carries a message out, and so needs something to say."""
    return bound.get('action') == 'send'


def _unreachable() -> int:
    """The one message for "no spool answered", on either plane."""
    console.print('[error]error:[/error] the message service is not reachable '
                  '(is euler-msg.service running?)')
    return 1


def _is_staff() -> bool:
    """Whether this shell's subject is at or above the staff floor."""
    return rank(config.subject.profile) >= rank(STAFF_FLOOR)


def _verb_of(thread: dict[str, Any]) -> str:
    """What `act` would do to *thread*, for this caller — the menu's hint and the dispatch."""
    return verb_for(str(thread.get('subject', '')), is_staff=_is_staff(),
                    is_own=str(thread.get('author_name', '')) == config.subject.user)


# ── rendering ───────────────────────────────────────────────────────────────────────

def _when(stamp: str) -> str:
    """An ISO-8601 timestamp trimmed to the minute — the row has to fit one line."""
    return stamp[:16].replace('T', ' ')


def _print_thread_line(thread: dict[str, Any]) -> None:
    """One line per message: unread marker, id, when, who, subject."""
    mark = '[accent]●[/accent]' if thread.get('unread') else ' '
    verb = _verb_of(thread)
    tail = f' [muted]({verb})[/muted]' if verb != 'read' else ''
    console.print(f'  {mark} [accent]{thread.get("id", "")}[/accent] '
                  f'[muted]{_when(str(thread.get("updated", "")))}[/muted] '
                  f'{str(thread.get("kind", "")):7} '
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

def _fetch(thread_id: str) -> dict[str, Any] | None:
    """One message as this caller may see it, or None with the reason already printed.

    The single read behind both `read` and `act`: `act` has to know what a message *is*
    before it can do anything with it, and fetching twice to decide and then to print
    would let the two answers differ.
    """
    result = _call('thread', thread_id=thread_id)
    if result is None:
        _unreachable()
        return None
    status, data = result
    if status != 200 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return None
    return data


def _list() -> int:
    """Every message this caller may read, newest first.

    One list, for everybody. Staff see the inbound queue here as well — the store shows
    every inbound thread to any staff reader — so the separate `queue` verb was a second
    name for a subset of this, with its own ordering and its own emptiness message.
    """
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
    console.print(f'[accent]{len(threads)}[/accent] message(s), '
                  f'[accent]{unread}[/accent] unread — read one with `msg read <id>`, '
                  'or `msg act <id>` to do what it asks')
    for thread in threads:
        _print_thread_line(thread)
    return 0


def _read(thread_id: str) -> int:
    """Show one message and mark it read."""
    data = _fetch(thread_id)
    if data is None:
        return 1
    return _show(data)


def _show(data: dict[str, Any]) -> int:
    """Print an already-fetched message and mark it read — `read`, and `act`'s default."""
    _print_thread(data)
    _call('read', thread_id=str(data.get('id', '')))    # attention, not activity — failure is harmless
    osc.messages_changed()                              # the unread count just dropped
    return 0


def _act(thread_id: str) -> int:
    """Do what this message asks — and, for prose, that is to read it.

    The dispatch is :func:`~solver.web.msg.verb_for` on the subject, which is also what
    labels the header chip's rows, so the button and the command cannot disagree. The two
    staff acts are handed out by that function at :data:`STAFF_FLOOR` and never below it,
    which is what makes calling `user_authorize` / `gh_merge` as plain functions safe here:
    a caller who is not staff is never routed to them, and both commands hold their own
    floor for every other way in.

    Each act cleans up after itself, so there is nothing left to dismiss: taking a key
    dismisses the message that carried it, granting one dismisses the request, and a merge
    dismisses the notice that announced the pull request.
    """
    data = _fetch(thread_id)
    if data is None:
        return 1
    match _verb_of(data):
        case 'save':
            return _save(thread_id, data)
        case 'authorize':
            from solver.crypto.keys import user_authorize
            return user_authorize(thread_id)
        case 'merge':
            # No thread is passed: the notice says a pull request is waiting, and the queue
            # the verb walks is GitHub's. It dismisses this message itself, by the branch in
            # the subject (`solver.core.git._dismiss_pr_notice`).
            from solver.core.git import gh_merge
            return gh_merge('merge')
        case _:
            return _show(data)


def _send(subject: str, body: str, to: str) -> int:
    """Send one message: to staff, to everyone, or to named identities.

    One verb for what used to be two. `send` and `notice` differed only in *who receives*,
    which is an argument, not a verb — and making it a verb put the ladder in the menu,
    where a `contributor` was offered a staff-only option and refused after answering three
    questions.

    Below the staff floor `to` is never asked and defaults to `staff`, so nothing changes
    for the rung that has one possible answer. Above it, anything other than `staff` is a
    notice, which the service floors on its own; the check here only says so in the
    command's own words rather than as a bare 403.
    """
    parts = [part.strip() for part in to.split(',') if part.strip()] or [_STAFF_LABEL]
    if _STAFF_LABEL in parts:
        if len(parts) > 1:
            raise Abort(f'`to={_STAFF_LABEL}` is the whole audience — it cannot be combined '
                        'with named recipients', rc=ExitCodes.EXIT_USAGE)
        return _to_staff(subject, body)
    if not _is_staff():
        console.print(f'[error]error:[/error] only {STAFF_FLOOR}s may write to users '
                      f'(you are {config.subject.profile}) — `to={_STAFF_LABEL}` is yours')
        return 77
    targets: str | list[str] = (_EVERYONE if _EVERYONE in parts or _EVERYONE_LABEL in parts
                                else parts)
    return _notice(targets, subject, body)


def _to_staff(subject: str, body: str) -> int:
    """Ask staff something — the inbound half of `send`."""
    result = _call('send', body={'subject': subject, 'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 201 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    console.print(f'[success]sent[/success] [muted]({data.get("id")})[/muted] — '
                  'staff will see it in their messages')
    osc.messages_changed()
    return 0


def _notice(targets: str | list[str], subject: str, body: str) -> int:
    """Send to named recipients, or to everyone — the outbound half of `send` (staff)."""
    result = _call('notice', body={'to': targets, 'subject': subject, 'body': body})
    if result is None:
        return _unreachable()
    status, data = result
    if status != 201 or not isinstance(data, dict):
        console.print(f'[error]error:[/error] {status} {data}')
        return 1
    count = data.get('recipients', 0)
    console.print(f'[success]sent[/success] to [accent]{count}[/accent] '
                  f'recipient(s) [muted]({data.get("id")})[/muted]')
    osc.messages_changed()
    return 0


def _save(thread_id: str, data: dict[str, Any]) -> int:
    """Write the master key delivered in *thread_id* to this machine's enc-key file.

    The receiving half of key distribution, and what `msg act` does with a key message.
    `user-authorize` (or `key-rekey`) wraps the master key to your public key and sends it;
    this takes it. Nothing else can write that file, and nothing writes it without proving
    the payload first:

    - the message's **subject** must be the key-issue one, so no other message can be mined
      for something that looks like key material. That is how `act` chose this branch, and
      it is checked again here rather than trusted — the dispatch is a routing decision,
      the check is the gate;
    - the payload must **unwrap with your private key** and its `verify` must decrypt to the
      known text. Only then does it replace what you have.

    The message is **dismissed** once the key is written: its whole content is now in your
    enc-key file, and a spool that keeps every taken key is storing key material for nobody.

    That order matters. The file it overwrites may be the only thing standing between this
    machine and the whole private tree, so a bad or mistargeted payload has to fail *before*
    the write, not be discovered after it.
    """
    from solver.crypto.keys import save_issued_key
    # An issued key is always its own message: with no replies there is nowhere else for it
    # to be, and one subject to check.
    if not str(data.get('subject', '')).startswith(KEY_ISSUE_SUBJECT):
        console.print(f'[error]error:[/error] message [accent]{thread_id}[/accent] does not carry '
                      'a master key — taking one writes key material and nothing else')
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
    """Drop a worked message from the spool.

    Not floored in the command: the service decides, and it decides better — staff may drop
    anything, anyone else a message they are a party to. A `reader` clearing a notice they
    have finished with is the case the floor used to get wrong.
    """
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
def msg(action: Annotated[Literal['list', 'read', 'send', 'dismiss', 'act'],
                          Ask('What would you like to do?', labels=_ACTIONS)] = 'list',
        thread: Annotated[str, Ask('Which message?', choices=_threads, when=_needs_thread,
                                   empty='no messages')] = '',
        subject: Annotated[str, Ask('Subject', when=_is_send)] = '',
        body: Annotated[str, Ask('Message', when=_is_send, multiline=True)] = '',
        to: Annotated[str, Ask('Who should receive it?', choices=_recipients,
                               when=_needs_recipients, strict=False)] = '') -> int:
    """Read and send messages: what is waiting for you, and what it asks you to do.

    Every message has staff (`maintainer`+) at one end: you can ask them something,
    they can answer, and they can send notices. There is deliberately no user-to-user
    messaging. Delivery is asynchronous — the spool holds the message until you read it.

    Five verbs, and each is one thing a person does with a message. `act` is the one worth
    knowing: a message *knows* what it is for, so acting on one takes the key it carries,
    grants the key it asks for, or merges the pull request it announces — and on anything
    else it simply reads it. The header's message chip labels its rows from the same rule.

    Typed bare, it walks you through the rest: pick a verb, then whatever that verb needs —
    a message from your own list, or a subject and a body. Every answer can be given on the
    command line instead, and a non-interactive shell asks nothing.

    Args:
        action: [asked] What to do — `list` everything waiting for you, newest first; `read`
            one message and mark it read; `send` a message; `dismiss` one you are done with;
            `act` on one, doing what it asks. Defaults to `list`.
        thread: [asked] The message to act on, for `read` / `dismiss` / `act`. Offered as a
            menu of your own messages, so the id never has to be typed out.
        subject: [asked] The subject line, for `send`.
        body: [asked] The message text, for `send`.
        to: [asked] Who a `send` goes to: `staff` (the default, and the only audience below
            the `maintainer` floor), `everyone`, or one or more identities, comma-separated.
            Staff are offered the known accounts as a menu where the roster can be read.
    """
    if action == 'list':
        return _list()

    if action in _ON_THREAD:
        if not thread:
            # Reached only non-interactively: an interactive shell was offered the menu.
            raise Abort(f'msg {action} needs a message id (see `msg list`)',
                        rc=ExitCodes.EXIT_USAGE)
        if action == 'read':
            return _read(thread)
        if action == 'dismiss':
            return _dismiss(thread)
        return _act(thread)

    if not subject or not body:
        raise Abort('msg send needs subject="…" and body="…"', rc=ExitCodes.EXIT_USAGE)
    return _send(subject, body, to)
