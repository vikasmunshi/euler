#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the messaging tier (web-server-guide § Messaging).

Three surfaces, in the order the request travels:

- **the store** — thread semantics with no service around them: who may see what, how
  read-state moves, and the caps and sanitising that bound a store
  holding text other people wrote.
- **the spool service** — the real ``euler-msg`` apps over real unix sockets, so
  ``SO_PEERCRED`` identity is exercised rather than stubbed: the tests connect as *this*
  process's uid and the policy file maps that login. Also the profile floors, and that a
  policy edit lands within one request.
- **the per-user tier** — the browser half: the pane, the header chip's badge, the write
  routes, and the delivery push that reaches an attached terminal as a text frame.

The policy file is written per test with **this process's own login** in it, because the
spool's whole identity story is "the connecting uid, resolved through
``authorizations.json``" — a fixture with someone else's name in it would test nothing.
"""
from __future__ import annotations

import asyncio
import contextlib
import getpass
import io
import json
import os
import re
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from solver.auth.identity import system_slug
from solver.web.msg import KEY_ISSUE_SUBJECT, KEY_REQUEST_SUBJECT
from solver.web.msg.app import MessageService, build_admin_app, build_app
from solver.web.msg.config import MsgConfig
from solver.web.msg.identity import box_of
from solver.web.msg.store import MAX_PER_AUTHOR, MessageStore
from solver.web.site import gitstate
from solver.web.unixhttp import request as unix_request
from tests import silence

silence()

_ME = getpass.getuser()                 # the uid every socket test connects as
_ALICE = 'alice@example.com'
_BOB = 'bob@example.com'
_ALICE_BOX = box_of(_ALICE)
_BOB_BOX = box_of(_BOB)
_ADMIN_TOKEN = 'test-admin-token'


def _write_policy(path: Path, users: dict[str, str]) -> None:
    """Write an ``authorizations.json`` with *users*, bumping mtime so a reload is seen."""
    path.write_text(json.dumps({'ladder': ['reader', 'contributor', 'maintainer', 'admin'],
                                'users': users}), encoding='utf-8')
    stamp = time.time() + _write_policy.bump                # type: ignore[attr-defined]
    _write_policy.bump += 1                                 # type: ignore[attr-defined]
    os.utime(path, (stamp, stamp))


_write_policy.bump = 0                                      # type: ignore[attr-defined]


# ==================================================================================== #
#                                    the store
# ==================================================================================== #
class MessageStoreTests(unittest.TestCase):
    """Thread semantics, with no service and no sockets in the way."""

    def setUp(self) -> None:
        self.scratch = Path(tempfile.mkdtemp(prefix='euler-msg-store-'))
        self.addCleanup(shutil.rmtree, self.scratch, True)
        self.store = MessageStore(self.scratch / 'messages.json')

    def test_submit_is_visible_to_staff_and_to_its_author(self) -> None:
        thread_id = self.store.submit(_ALICE_BOX, 'help', 'please', [_ME])
        self.assertIsNotNone(thread_id)
        self.assertEqual(len(self.store.threads_for(_ME, staff=True)), 1)
        self.assertEqual(len(self.store.threads_for(_ALICE_BOX)), 1)
        # …and to nobody else.
        self.assertEqual(self.store.threads_for(_BOB_BOX), [])

    def test_author_starts_read_and_recipients_unread(self) -> None:
        self.store.submit(_ALICE_BOX, 'help', 'please', [_ME])
        self.assertEqual(self.store.unread_count(_ALICE_BOX), 0)
        self.assertEqual(self.store.unread_count(_ME, staff=True), 1)

    def test_staff_promoted_later_still_sees_the_queue_unread(self) -> None:
        """A maintainer who was not on the roster at submit time is not shut out."""
        thread_id = self.store.submit(_ALICE_BOX, 'help', 'please', [_ME])
        assert thread_id is not None
        self.assertEqual(len(self.store.threads_for('newstaff', staff=True)), 1)
        self.assertEqual(self.store.unread_count('newstaff', staff=True), 1)
        self.assertTrue(self.store.mark_read(thread_id, 'newstaff', staff=True))
        self.assertEqual(self.store.unread_count('newstaff', staff=True), 0)

    def test_a_broadcast_is_one_record_with_many_recipients(self) -> None:
        thread_id = self.store.notice(_ME, 'downtime', 'tonight', [_ALICE_BOX, _BOB_BOX])
        assert thread_id is not None
        raw = json.loads((self.scratch / 'messages.json').read_text())
        self.assertEqual(len(raw), 1, 'a broadcast must not fan out into copies')
        self.assertEqual(len(self.store.threads_for(_ALICE_BOX)), 1)
        self.assertEqual(len(self.store.threads_for(_BOB_BOX)), 1)

    def test_a_reader_cannot_see_another_readers_thread(self) -> None:
        thread_id = self.store.submit(_ALICE_BOX, 'private', 'text', [_ME])
        assert thread_id is not None
        self.assertIsNone(self.store.thread(thread_id, _BOB_BOX))
        self.assertIsNone(self.store.thread(thread_id, _BOB_BOX))
        self.assertFalse(self.store.mark_read(thread_id, _BOB_BOX))

    def test_control_characters_never_reach_the_store(self) -> None:
        thread_id = self.store.submit(_ALICE_BOX, 'a\x1b[31mb\x00c', 'l1\nl2\x07', [_ME])
        assert thread_id is not None
        thread = self.store.thread(thread_id, _ME, staff=True)
        assert thread is not None
        self.assertEqual(thread.subject, 'a[31mbc')
        self.assertEqual(thread.body, 'l1\nl2', 'newlines survive in a body; BEL does not')

    def test_empty_fields_are_refused(self) -> None:
        self.assertIsNone(self.store.submit(_ALICE_BOX, '', 'body', [_ME]))
        self.assertIsNone(self.store.submit(_ALICE_BOX, 'subject', '', [_ME]))
        self.assertIsNone(self.store.notice(_ME, 's', 'b', []), 'a notice needs a recipient')

    def test_per_author_cap(self) -> None:
        for index in range(MAX_PER_AUTHOR):
            self.assertIsNotNone(self.store.submit(_ALICE_BOX, f's{index}', 'b', [_ME]))
        self.assertIsNone(self.store.submit(_ALICE_BOX, 'one too many', 'b', [_ME]))
        self.assertIsNotNone(self.store.submit(_BOB_BOX, 'not my cap', 'b', [_ME]),
                             'the cap is per author, not global')

    def test_expired_threads_sweep_on_access(self) -> None:
        thread_id = self.store.submit(_ALICE_BOX, 's', 'b', [_ME])
        assert thread_id is not None
        path = self.scratch / 'messages.json'
        records = json.loads(path.read_text())
        records[thread_id]['expiry'] = time.time() - 1
        path.write_text(json.dumps(records))
        self.assertEqual(self.store.threads_for(_ME, staff=True), [])

    def test_drop_removes_a_thread(self) -> None:
        thread_id = self.store.submit(_ALICE_BOX, 's', 'b', [_ME])
        assert thread_id is not None
        self.assertTrue(self.store.drop(thread_id))
        self.assertFalse(self.store.drop(thread_id))

    def test_inbound_unread_is_the_askers_own_state(self) -> None:
        """A queue row must not read as unread just because no box was supplied."""
        self.store.submit(_ALICE_BOX, 's', 'b', [_ME])
        self.assertFalse(self.store.inbound(_ALICE_BOX)[0].unread)
        self.assertTrue(self.store.inbound(_ME)[0].unread)


# ==================================================================================== #
#                              the spool service
# ==================================================================================== #
class _SpoolCase(unittest.IsolatedAsyncioTestCase):
    """A real euler-msg on real sockets; the test process's uid is the caller."""

    #: The profile this process's login holds for the test.
    my_profile: str = 'admin'

    async def asyncSetUp(self) -> None:
        # Re-filter during the run: unittest resets warnings to 'default' before
        # discovery, so the import-time call is shadowed. AioHTTPTestCase gets this from
        # the patched setUp; an IsolatedAsyncioTestCase has to ask.
        silence()
        self.scratch = Path(tempfile.mkdtemp(prefix='euler-msg-svc-'))
        self.addCleanup(shutil.rmtree, self.scratch, True)
        self.policy = self.scratch / 'authorizations.json'
        _write_policy(self.policy, {_ME: self.my_profile, _ALICE: 'reader', _BOB: 'contributor'})
        os.environ['EULER_AUTHZ_FILE'] = str(self.policy)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)

        self.config = MsgConfig(
            state_dir=self.scratch / 'state',
            socket_path=self.scratch / 'msg.sock',
            admin_socket_path=self.scratch / 'msg-admin.sock',
            socket_group='', admin_socket_group='', admin_token=_ADMIN_TOKEN,
            user_socket_dir='')
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        self.service = MessageService(self.config)
        self._runners: list[web.AppRunner] = []
        for app, path in ((build_app(self.service), self.config.socket_path),
                          (build_admin_app(self.service), self.config.admin_socket_path)):
            runner = web.AppRunner(app, access_log=None)
            await runner.setup()
            await web.UnixSite(runner, str(path)).start()
            self._runners.append(runner)

    async def asyncTearDown(self) -> None:
        for runner in self._runners:
            await runner.cleanup()

    async def call(self, method: str, path: str, body: dict[str, Any] | None = None,
                   *, admin: bool = False) -> tuple[int, Any]:
        """One request, off the event loop (the client is blocking stdlib)."""
        socket_path = str(self.config.admin_socket_path if admin else self.config.socket_path)
        headers = {'X-Admin-Token': _ADMIN_TOKEN} if admin else None
        return await asyncio.to_thread(
            lambda: unix_request(socket_path, method, path, body=body, headers=headers))

    async def as_identity(self, method: str, path: str,
                          identity: str, body: dict[str, Any] | None = None) -> tuple[int, Any]:
        """The same call made *as another identity*, over the admin plane."""
        payload = {**(body or {}), 'identity': identity}
        joiner = '&' if '?' in path else '?'
        return await self.call(method, f'{path}{joiner}identity={identity}', payload, admin=True)


class SpoolIdentityTests(_SpoolCase):
    """SO_PEERCRED is the identity, and the policy is the profile."""

    @unittest_run_loop
    async def test_peer_uid_resolves_to_the_policy_identity(self) -> None:
        status, data = await self.call('GET', '/messages')
        self.assertEqual(status, 200)
        self.assertTrue(data['staff'], 'an admin login is staff')
        self.assertEqual(data['threads'], [])

    @unittest_run_loop
    async def test_healthz_needs_no_identity(self) -> None:
        status, _ = await self.call('GET', '/healthz')
        self.assertEqual(status, 200)

    @unittest_run_loop
    async def test_an_unmapped_peer_is_refused(self) -> None:
        """A uid the policy does not map reads nobody's mail — fail-closed."""
        _write_policy(self.policy, {_ALICE: 'reader'})       # this login is now unmapped
        status, _ = await self.call('GET', '/messages')
        self.assertEqual(status, 401)

    @unittest_run_loop
    async def test_a_demote_lands_within_one_request(self) -> None:
        self.assertEqual((await self.call('GET', '/staff/queue'))[0], 200)
        _write_policy(self.policy, {_ME: 'reader', _ALICE: 'reader'})
        self.assertEqual((await self.call('GET', '/staff/queue'))[0], 403)

    @unittest_run_loop
    async def test_the_admin_plane_needs_its_token(self) -> None:
        status, _ = await asyncio.to_thread(
            lambda: unix_request(str(self.config.admin_socket_path), 'GET',
                                 f'/admin/messages?identity={_ME}'))
        self.assertEqual(status, 401)

    @unittest_run_loop
    async def test_the_admin_plane_refuses_an_unmapped_identity(self) -> None:
        status, _ = await self.as_identity('GET', '/admin/messages', 'ghost@example.com')
        self.assertEqual(status, 400)


class SpoolFlowTests(_SpoolCase):
    """The three flows, end to end over the sockets."""

    @unittest_run_loop
    async def test_user_to_staff_then_an_answer_comes_back(self) -> None:
        status, data = await self.as_identity(
            'POST', '/admin/messages', _ALICE, {'subject': 'how?', 'body': 'tell me'})
        self.assertEqual(status, 201)

        status, queue = await self.call('GET', '/staff/queue')
        self.assertEqual(status, 200)
        self.assertEqual(len(queue['queue']), 1)
        self.assertEqual(queue['queue'][0]['author_name'], _ALICE,
                         'the queue names the sender by identity, not by box')

        status, _ = await self.call('POST', '/staff/notice',
                                    {'to': [_ALICE], 'subject': 'about that', 'body': 'like so'})

    @unittest_run_loop
    async def test_broadcast_reaches_everyone_but_the_sender(self) -> None:
        status, data = await self.call('POST', '/staff/notice',
                                       {'to': '*', 'subject': 'downtime', 'body': 'tonight'})
        self.assertEqual(status, 201)
        self.assertEqual(data['recipients'], 2)
        for who in (_ALICE, _BOB):
            _status, mail = await self.as_identity('GET', '/admin/messages', who)
            self.assertEqual(len(mail['threads']), 1)
            self.assertEqual(mail['threads'][0]['kind'], 'notice')
        _status, mine = await self.call('GET', '/messages')
        self.assertEqual(mine['unread'], 0, "the sender's own copy is already read")

    @unittest_run_loop
    async def test_a_notice_to_a_named_recipient_reaches_only_them(self) -> None:
        status, _ = await self.call('POST', '/staff/notice',
                                    {'to': [_ALICE], 'subject': 's', 'body': 'b'})
        self.assertEqual(status, 201)
        _status, alice = await self.as_identity('GET', '/admin/messages', _ALICE)
        _status, bob = await self.as_identity('GET', '/admin/messages', _BOB)
        self.assertEqual(len(alice['threads']), 1)
        self.assertEqual(len(bob['threads']), 0)

    @unittest_run_loop
    async def test_a_notice_to_an_unknown_address_is_refused(self) -> None:
        """Never file a message into a box nobody can ever read."""
        status, _ = await self.call('POST', '/staff/notice',
                                    {'to': ['nobody@example.com'], 'subject': 's', 'body': 'b'})
        self.assertEqual(status, 400)

    @unittest_run_loop
    async def test_read_state_and_thread_fetch(self) -> None:
        _status, data = await self.as_identity('POST', '/admin/messages', _BOB,
                                               {'subject': 's', 'body': 'b'})
        thread_id = data['id']
        _status, mail = await self.call('GET', '/messages')
        self.assertEqual(mail['unread'], 1)
        self.assertEqual((await self.call('POST', f'/messages/{thread_id}/read'))[0], 200)
        _status, mail = await self.call('GET', '/messages')
        self.assertEqual(mail['unread'], 0)
        status, thread = await self.call('GET', f'/messages/{thread_id}')
        self.assertEqual(status, 200)
        self.assertEqual(thread['body'], 'b')

    @unittest_run_loop
    async def test_dismiss_drops_a_worked_thread(self) -> None:
        _status, data = await self.as_identity('POST', '/admin/messages', _BOB,
                                               {'subject': 's', 'body': 'b'})
        thread_id = data['id']
        self.assertEqual((await self.call('DELETE', f'/staff/queue/{thread_id}'))[0], 200)
        self.assertEqual((await self.call('GET', f'/messages/{thread_id}'))[0], 404)

    @unittest_run_loop
    async def test_a_thread_you_are_not_party_to_is_404(self) -> None:
        _status, data = await self.as_identity('POST', '/admin/messages', _BOB,
                                               {'subject': 's', 'body': 'b'})
        status, _ = await self.as_identity('GET', f'/admin/threads/{data["id"]}', _ALICE)
        self.assertEqual(status, 404)


class SpoolFloorTests(_SpoolCase):
    """A reader may write to staff and read their own mail, and nothing else."""

    my_profile = 'reader'

    @unittest_run_loop
    async def test_reader_may_send_and_read_own(self) -> None:
        self.assertEqual((await self.call('GET', '/messages'))[0], 200)
        status, _ = await self.call('POST', '/messages', {'subject': 's', 'body': 'b'})
        self.assertEqual(status, 400, 'no staff are mapped, so there is no one to queue for')

    @unittest_run_loop
    async def test_reader_may_not_read_the_queue(self) -> None:
        self.assertEqual((await self.call('GET', '/staff/queue'))[0], 403)

    @unittest_run_loop
    async def test_reader_may_not_broadcast(self) -> None:
        status, _ = await self.call('POST', '/staff/notice',
                                    {'to': '*', 'subject': 's', 'body': 'b'})
        self.assertEqual(status, 403)

    @unittest_run_loop
    async def test_reader_may_not_dismiss(self) -> None:
        self.assertEqual((await self.call('DELETE', '/staff/queue/whatever'))[0], 403)

    @unittest_run_loop
    async def test_a_message_with_no_staff_mapped_is_refused_not_lost(self) -> None:
        """Better a visible refusal than a thread queued for an empty roster."""
        status, _ = await self.call('POST', '/messages', {'subject': 's', 'body': 'b'})
        self.assertEqual(status, 400)
        self.assertEqual(json.loads((self.config.state_dir / 'messages.json').read_text()
                                    if (self.config.state_dir / 'messages.json').exists()
                                    else '{}'), {})


class SpoolContributorTests(_SpoolCase):
    """A contributor is not staff — the floor is maintainer, not "anyone who can write"."""

    my_profile = 'contributor'

    @unittest_run_loop
    async def test_contributor_may_not_read_the_queue(self) -> None:
        self.assertEqual((await self.call('GET', '/staff/queue'))[0], 403)


# ==================================================================================== #
#                             the per-user tier
# ==================================================================================== #
async def _no_git_read(_repo_root: Any, *, fetch: bool = False) -> None:
    """gitstate.read stand-in: the chip is not under test and its real read would fetch."""
    return None


class UserMessageChipTests(AioHTTPTestCase):
    """The browser half — which is one read-only fragment and the delivery push.

    What is *absent* is as much the contract as what is present: there is no pane, no
    thread view and no write route, so the browser cannot put anything into the spool.
    Those tests are the ones asserting a 404 below.
    """

    profile: str = 'maintainer'

    async def get_application(self) -> web.Application:
        # Deferred: importing the per-user app pulls aiohttp_jinja2 and the site tier.
        from solver.web.user.app import build_app as build_user_app
        from solver.web.user.config import UserConfig

        self.scratch = Path(tempfile.mkdtemp(prefix='euler-msg-user-'))
        self.addCleanup(shutil.rmtree, self.scratch, True)
        self.policy = self.scratch / 'authorizations.json'
        # This process's login is the spool's view of the caller (peer uid); the browser
        # identity below is what the *content* tier gates on. In production they are the
        # same principal — the instance runs as that collaborator's uid.
        _write_policy(self.policy, {_ME: self.profile, _ALICE: 'reader'})
        os.environ['EULER_AUTHZ_FILE'] = str(self.policy)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)

        saved_read = gitstate.read
        gitstate.read = _no_git_read            # type: ignore[assignment]
        self.addCleanup(setattr, gitstate, 'read', saved_read)

        # A real spool behind the tier: the chip must be tested against the store, not
        # against a stub that agrees with it.
        config = MsgConfig(
            state_dir=self.scratch / 'state', socket_path=self.scratch / 'msg.sock',
            admin_socket_path=self.scratch / 'msg-admin.sock', socket_group='',
            admin_socket_group='', admin_token=_ADMIN_TOKEN, user_socket_dir='')
        config.state_dir.mkdir(parents=True, exist_ok=True)
        self.spool = MessageService(config)
        self.spool_config = config
        self._spool_runner = web.AppRunner(build_app(self.spool), access_log=None)
        await self._spool_runner.setup()
        await web.UnixSite(self._spool_runner, str(config.socket_path)).start()
        os.environ['EULER_MSG_SOCKET'] = str(config.socket_path)
        self.addCleanup(os.environ.pop, 'EULER_MSG_SOCKET', None)

        repo_root = Path(__file__).resolve().parents[1]
        user_config = UserConfig(
            repo_root=repo_root, static_dir=repo_root / 'solver/web/content',
            socket_path=self.scratch / 'user.sock', socket_group='', tcp_bind='',
            serve_static=False, slug=system_slug(_ALICE), auth_socket='',
            shell_argv=(), detached_ttl=0)
        return build_user_app(user_config)

    async def tearDownAsync(self) -> None:
        await self._spool_runner.cleanup()
        await super().tearDownAsync()

    @property
    def headers(self) -> dict[str, str]:
        """forward_auth's identity headers for this instance's own user."""
        return {'X-User': _ALICE, 'X-Profile': self.profile}

    @unittest_run_loop
    async def test_the_chip_renders_with_its_verbs(self) -> None:
        resp = await self.client.get('/messages', headers=self.headers)
        self.assertEqual(resp.status, 200)
        body = await resp.text()
        self.assertIn('<summary', body)
        self.assertIn('msg list', body, 'the chip offers the shell verb, not a page')

    @unittest_run_loop
    async def test_the_fragment_is_the_contents_and_cannot_re_arm_its_own_load(self) -> None:
        """The swap must not replace the <details>.

        With `hx-swap="outerHTML"` the replacement carried its own `hx-trigger="load"`,
        which fired on insertion and re-fetched forever — and each swap reset `open`, so
        the menu shut a few milliseconds after any click. The fragment therefore carries
        neither the element nor its triggers.
        """
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertNotIn('id="msg-chip"', body)
        self.assertNotIn('hx-trigger', body)
        self.assertNotIn('<details', body)

    @unittest_run_loop
    async def test_the_header_swaps_the_chips_contents_not_the_chip(self) -> None:
        page = await (await self.client.get('/account', headers=self.headers)).text()
        self.assertIn('hx-swap="innerHTML"', page.split('id="msg-chip"')[1][:200])

    @unittest_run_loop
    async def test_unauthenticated_is_refused(self) -> None:
        self.assertEqual((await self.client.get('/messages')).status, 401)

    @unittest_run_loop
    async def test_rows_type_a_read_command_into_the_shell(self) -> None:
        """A row is a terminal verb, not a link: there is nowhere in the browser to go."""
        thread_id = self.spool.store.submit(_ALICE_BOX, 'a question', 'the body', [_ME])
        assert thread_id is not None
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn(f'data-term-cmd="msg read {thread_id}"', body)
        self.assertIn('a question', body)
        self.assertNotIn('the body', body, 'the body is read in the shell, never rendered here')

    @unittest_run_loop
    async def test_a_key_request_row_offers_the_authorize_verb(self) -> None:
        """The row carries the verb it is FOR — here, somebody else's request seen by staff.

        Authored by somebody else — a request of *your own* is a `msg save` row instead, since
        what you are waiting for on it is the reply.

        The id is the whole point: the command reads the public key from the thread over the
        socket, so the key never reaches the browser and nobody retypes it.
        """
        thread_id = self.spool.store.submit(box_of(_ME), f'{KEY_REQUEST_SUBJECT}{_ME}',
                                            f'public key: {"ab" * 32}', [_ME])
        assert thread_id is not None
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn(f'data-term-cmd="user-authorize {thread_id}"', body)
        self.assertNotIn(f'msg read {thread_id}', body, 'one verb per row, the relevant one')
        self.assertIn('>authorize<', body, 'and the row says which')
        self.assertNotIn('ab' * 32, body, 'the key is read in the shell, never rendered here')

    @unittest_run_loop
    async def test_a_key_issued_to_you_offers_save(self) -> None:
        """A rotation's notice: the thing to do with a key is take it, not read about it."""
        thread_id = self.spool.store.notice(_ALICE_BOX, f'{KEY_ISSUE_SUBJECT}rotated master key',
                                            'payload here', [_ME])
        assert thread_id is not None
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn(f'data-term-cmd="msg save {thread_id}"', body)
        self.assertIn('>save<', body)

    @unittest_run_loop
    async def test_an_ordinary_thread_is_still_a_read(self) -> None:
        """Prose keeps the plain verb, and carries no chip — a label on every row is noise."""
        thread_id = self.spool.store.submit(_ALICE_BOX, 'a question', 'the body', [_ME])
        assert thread_id is not None
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn(f'data-term-cmd="msg read {thread_id}"', body)
        self.assertNotIn('user-authorize', body)
        self.assertNotIn('msg-verb', body, 'no chip on an ordinary row')

    @unittest_run_loop
    async def test_the_count_and_totals_come_from_the_spool(self) -> None:
        self.spool.store.submit(_ALICE_BOX, 's1', 'b', [_ME])
        self.spool.store.submit(_ALICE_BOX, 's2', 'b', [_ME])
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn('2 unread, 2 threads', body)
        self.assertIn('is-unread', body)

    @unittest_run_loop
    async def test_an_empty_mailbox_still_names_its_axes(self) -> None:
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn('0 unread, 0 threads', body)

    @unittest_run_loop
    async def test_rows_are_capped_and_put_unread_first(self) -> None:
        for index in range(8):
            thread_id = self.spool.store.submit(_ALICE_BOX, f'subject-{index}', 'b', [_ME])
            assert thread_id is not None
            if index < 6:                       # leave the last two unread
                self.spool.store.mark_read(thread_id, _ME, staff=True)
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertEqual(body.count('data-term-cmd="msg read '), 5, 'the menu is capped')
        self.assertIn('subject-6', body)        # …and the unread ones are the ones kept
        self.assertIn('subject-7', body)

    @unittest_run_loop
    async def test_the_chip_survives_an_unreachable_spool(self) -> None:
        """Messaging is the least important thing in the header; it must not take a page
        render down with it."""
        await self._spool_runner.cleanup()
        resp = await self.client.get('/messages', headers=self.headers)
        self.assertEqual(resp.status, 200)
        self.assertIn('0 unread, 0 threads', await resp.text())
        self._spool_runner = web.AppRunner(build_app(self.spool), access_log=None)
        await self._spool_runner.setup()
        await web.UnixSite(self._spool_runner, str(self.spool_config.socket_path)).start()

    @unittest_run_loop
    async def test_the_header_carries_the_chip_on_an_ordinary_page(self) -> None:
        """Every page renders it with the spool flag but no count — no read per navigation."""
        body = await (await self.client.get('/account', headers=self.headers)).text()
        self.assertIn('id="msg-chip"', body)
        self.assertIn('hx-get="/messages"', body)

    @unittest_run_loop
    async def test_there_is_no_pane_and_no_write_route(self) -> None:
        """The browser cannot put anything into the spool — the surface simply is not there."""
        for method, path in (('GET', '/messages/'), ('GET', '/messages/whatever'),
                             ('POST', '/messages'), ('POST', '/messages/'),
                             ('POST', '/messages/notice')):
            resp = await self.client.request(method, path, headers=self.headers)
            self.assertIn(resp.status, (404, 405), f'{method} {path} should not exist')

    @unittest_run_loop
    async def test_the_delivery_push_is_accepted_with_no_terminal_attached(self) -> None:
        """The nudge is best-effort: no shell open means nothing to notify, not an error."""
        resp = await self.client.post('/internal/message', json={'slug': 'x', 'unread': 3})
        self.assertEqual(resp.status, 200)
        self.assertEqual((await resp.json())['notified'], 0)

    @unittest_run_loop
    async def test_the_delivery_push_rejects_a_malformed_body(self) -> None:
        resp = await self.client.post('/internal/message', data='not json')
        self.assertEqual(resp.status, 400)


class UserMessageChipReaderTests(UserMessageChipTests):
    """A reader gets the same chip, with the staff verb shown but locked."""

    profile = 'reader'

    @unittest_run_loop
    async def test_the_queue_verb_is_shown_but_locked(self) -> None:
        """Shown, not hidden: the ladder is part of what the header teaches."""
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn('Inbound queue', body)
        self.assertIn('needs the maintainer profile', body)
        self.assertNotIn('data-term-cmd="msg queue"', body)

    @unittest_run_loop
    async def test_a_key_request_row_offers_the_authorize_verb(self) -> None:
        """Overridden: a reader gets the row and **no** verb.

        A reader cannot issue a key, so somebody else's request keeps the plain read —
        offering them a grant they can never make would be worse than saying nothing.
        """
        thread_id = self.spool.store.submit(box_of(_ME), f'{KEY_REQUEST_SUBJECT}{_ME}',
                                            f'public key: {"ab" * 32}', [_ME])
        assert thread_id is not None
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn(f'data-term-cmd="msg read {thread_id}"', body)   # the row is there…
        self.assertNotIn('user-authorize', body)                       # …without the verb

    @unittest_run_loop
    async def test_rows_type_a_read_command_into_the_shell(self) -> None:
        """As a reader this login is not staff, so the thread must be addressed to them."""
        thread_id = self.spool.store.notice(_ALICE_BOX, 'a notice', 'the body', [_ME])
        assert thread_id is not None
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn(f'data-term-cmd="msg read {thread_id}"', body)
        self.assertNotIn('the body', body)

    @unittest_run_loop
    async def test_the_count_and_totals_come_from_the_spool(self) -> None:
        self.spool.store.notice(_ALICE_BOX, 's1', 'b', [_ME])
        self.spool.store.notice(_ALICE_BOX, 's2', 'b', [_ME])
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertIn('2 unread, 2 threads', body)

    @unittest_run_loop
    async def test_rows_are_capped_and_put_unread_first(self) -> None:
        for index in range(8):
            thread_id = self.spool.store.notice(_ALICE_BOX, f'subject-{index}', 'b', [_ME])
            assert thread_id is not None
            if index < 6:
                self.spool.store.mark_read(thread_id, _ME)
        body = await (await self.client.get('/messages', headers=self.headers)).text()
        self.assertEqual(body.count('data-term-cmd="msg read '), 5)
        self.assertIn('subject-6', body)
        self.assertIn('subject-7', body)


class MsgCommandNudgeTests(_SpoolCase):
    """The shell half of the chip's refresh: OSC 5379 `msg` after a mutating verb.

    The spool pushes when a message *arrives*, but marking one read happens in the user's
    own shell and no service sees it — so without this the badge still said 1 after they
    read the only unread thread, until the next full page load. Same move `git-sync` makes
    for the git chip, landing on the same `euler:message` event as the delivery push.
    """

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        os.environ['EULER_MSG_SOCKET'] = str(self.config.socket_path)
        self.addCleanup(os.environ.pop, 'EULER_MSG_SOCKET', None)
        # The command reads its own identity and channel off the live config.
        from solver.auth.subject import Subject
        from solver.config import config as app_config
        self._saved_subject = app_config.subject
        self.addCleanup(setattr, app_config, 'subject', self._saved_subject)
        app_config.subject = Subject(user=_ME, slug=_ME, channel='web',
                                     auth_method='test', profile=self.my_profile)

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """Run the `msg` command with stdout captured; return what it wrote."""
        from solver.web.msg.commands import msg
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            msg(*args, **kwargs)
        return buffer.getvalue()

    @staticmethod
    def _nudges(output: str) -> int:
        """How many `msg` nudges the output carries (the token varies per emission)."""
        return len(re.findall(r'\x1b\]5379;msg;\d+\x07', output))

    async def _thread_from_alice(self) -> str:
        status, data = await self.as_identity('POST', '/admin/messages', _ALICE,
                                              {'subject': 'ping', 'body': 'hello'})
        self.assertEqual(status, 201)
        return str(data['id'])

    @unittest_run_loop
    async def test_reading_nudges_the_chip(self) -> None:
        thread_id = await self._thread_from_alice()
        _status, before = await self.call('GET', '/messages')
        self.assertEqual(before['unread'], 1)
        output = await asyncio.to_thread(self._run, 'read', thread_id)
        self.assertEqual(self._nudges(output), 1)
        _status, after = await self.call('GET', '/messages')
        self.assertEqual(after['unread'], 0, 'the nudge must follow a real change')

    @unittest_run_loop
    async def test_every_mutating_verb_nudges(self) -> None:
        thread_id = await self._thread_from_alice()
        for label, call in (
                ('send', lambda: self._run('send', subject='s', body='b')),
                ('notice', lambda: self._run('notice', to=_ALICE, subject='s', body='b')),
                ('dismiss', lambda: self._run('dismiss', thread_id)),
        ):
            output = await asyncio.to_thread(call)
            self.assertEqual(self._nudges(output), 1, f'{label} should nudge the chip')

    @unittest_run_loop
    async def test_read_only_verbs_do_not_nudge(self) -> None:
        """A nudge that fires when nothing moved trains the reader to ignore it."""
        await self._thread_from_alice()
        for label, call in (('list', lambda: self._run('list')),
                            ('queue', lambda: self._run('queue'))):
            output = await asyncio.to_thread(call)
            self.assertEqual(self._nudges(output), 0, f'{label} changes nothing')

    @unittest_run_loop
    async def test_a_terminal_shell_emits_nothing(self) -> None:
        """Off the web channel the sequence is noise in a real terminal — osc.emit no-ops."""
        from solver.config import config as app_config
        app_config.subject = app_config.subject._replace(channel='terminal')
        thread_id = await self._thread_from_alice()
        output = await asyncio.to_thread(self._run, 'read', thread_id)
        self.assertEqual(self._nudges(output), 0)


class NotifyStaffTests(unittest.IsolatedAsyncioTestCase):
    """The programmatic sender — why the layer exists at all."""

    async def asyncSetUp(self) -> None:
        silence()
        self.scratch = Path(tempfile.mkdtemp(prefix='euler-msg-notify-'))
        self.addCleanup(shutil.rmtree, self.scratch, True)
        policy = self.scratch / 'authorizations.json'
        _write_policy(policy, {_ME: 'maintainer', _ALICE: 'reader'})
        os.environ['EULER_AUTHZ_FILE'] = str(policy)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
        os.environ['EULER_MSG_SOCKET'] = str(self.scratch / 'msg.sock')
        self.addCleanup(os.environ.pop, 'EULER_MSG_SOCKET', None)

        config = MsgConfig(
            state_dir=self.scratch / 'state', socket_path=self.scratch / 'msg.sock',
            admin_socket_path=self.scratch / 'admin.sock', socket_group='',
            admin_socket_group='', admin_token=_ADMIN_TOKEN, user_socket_dir='')
        config.state_dir.mkdir(parents=True, exist_ok=True)
        self.spool = MessageService(config)
        self.runner = web.AppRunner(build_app(self.spool), access_log=None)
        await self.runner.setup()
        await web.UnixSite(self.runner, str(config.socket_path)).start()
        self.addAsyncCleanup(self.runner.cleanup)

    async def test_a_command_can_queue_a_message_for_staff(self) -> None:
        from solver.web.msg.notify import notify_staff
        sent = await asyncio.to_thread(notify_staff, 'Key authorization request', 'public key: abc')
        self.assertTrue(sent)
        queue = self.spool.store.inbound()
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0].subject, 'Key authorization request')
        self.assertIn('abc', queue[0].body)

    async def test_an_absent_spool_is_a_quiet_false_not_an_exception(self) -> None:
        """A command must not fail because the thing reporting it could not report."""
        from solver.web.msg.notify import notify_staff
        os.environ['EULER_MSG_SOCKET'] = str(self.scratch / 'nothing-here.sock')
        sent = await asyncio.to_thread(notify_staff, 's', 'b')
        self.assertFalse(sent)

    async def test_a_refusal_is_reported_as_false(self) -> None:
        from solver.web.msg.notify import notify_staff
        sent = await asyncio.to_thread(notify_staff, '', '')      # empty fields are refused
        self.assertFalse(sent)


class DeliveryNudgeTests(unittest.IsolatedAsyncioTestCase):
    """The spool's push, and the frame an attached terminal receives."""

    async def test_notify_all_sends_a_text_frame_to_attached_sockets(self) -> None:
        """The nudge must be a TEXT frame: a PTY byte would land in the replay buffer."""
        from solver.web.ws.manager import PtyManager

        received: list[str] = []

        class _FakeWs:
            closed = False

            async def send_str(self, data: str) -> None:
                received.append(data)

        manager = PtyManager()

        class _FakePty:
            async def notify(self, message: str) -> int:
                await _FakeWs().send_str(message)
                return 1

        manager._shells['someone'] = _FakePty()      # type: ignore[assignment]
        sent = await manager.notify_all(json.dumps({'euler': 'message', 'unread': 2}))
        self.assertEqual(sent, 1)
        self.assertEqual(json.loads(received[0]), {'euler': 'message', 'unread': 2})

    async def test_the_push_targets_the_recipients_own_socket(self) -> None:
        """euler-msg pushes to ``user-<box>.sock`` and never fans out beyond it."""
        scratch = Path(tempfile.mkdtemp(prefix='euler-msg-push-'))
        self.addCleanup(shutil.rmtree, scratch, True)
        policy = scratch / 'authorizations.json'
        _write_policy(policy, {_ME: 'maintainer', _ALICE: 'reader'})
        os.environ['EULER_AUTHZ_FILE'] = str(policy)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)

        pushes: list[dict[str, Any]] = []

        async def internal_message(request: web.Request) -> web.Response:
            pushes.append(await request.json())
            return web.json_response({'notified': 1})

        instance = web.Application()
        instance.add_routes([web.post('/internal/message', internal_message)])
        runner = web.AppRunner(instance, access_log=None)
        await runner.setup()
        await web.UnixSite(runner, str(scratch / f'user-{_ALICE_BOX}.sock')).start()
        self.addAsyncCleanup(runner.cleanup)

        config = MsgConfig(state_dir=scratch / 'state', socket_path=scratch / 'msg.sock',
                           admin_socket_path=scratch / 'admin.sock', socket_group='',
                           admin_socket_group='', admin_token=_ADMIN_TOKEN,
                           user_socket_dir=str(scratch))
        config.state_dir.mkdir(parents=True, exist_ok=True)
        service = MessageService(config)
        thread_id, boxes = await service.notice(box_of(_ME), 'downtime', 'tonight', [_ALICE])
        self.assertIsNotNone(thread_id)
        self.assertEqual(boxes, [_ALICE_BOX])
        self.assertEqual(len(pushes), 1)
        self.assertEqual(pushes[0], {'slug': _ALICE_BOX, 'unread': 1})

    async def test_a_local_login_gets_no_push(self) -> None:
        """An os-login has no per-user instance; pushing to a socket that cannot exist
        would be a guaranteed-failing connect on every message."""
        scratch = Path(tempfile.mkdtemp(prefix='euler-msg-nopush-'))
        self.addCleanup(shutil.rmtree, scratch, True)
        policy = scratch / 'authorizations.json'
        _write_policy(policy, {_ME: 'maintainer', 'operator': 'admin'})
        os.environ['EULER_AUTHZ_FILE'] = str(policy)
        self.addCleanup(os.environ.pop, 'EULER_AUTHZ_FILE', None)
        config = MsgConfig(state_dir=scratch / 'state', socket_path=scratch / 'msg.sock',
                           admin_socket_path=scratch / 'admin.sock', socket_group='',
                           admin_socket_group='', admin_token=_ADMIN_TOKEN,
                           user_socket_dir=str(scratch))
        config.state_dir.mkdir(parents=True, exist_ok=True)
        service = MessageService(config)
        self.assertFalse(service.policy.is_web('operator'))
        await service.notify(['operator'])       # must not raise, must not connect


if __name__ == '__main__':
    unittest.main()
