#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for `env.conf` and the five web-service configurations it feeds.

Two things are pinned here, and the first matters more than it looks.

**Reading the table must not construct a `Config`.** `euler-auth`, `euler-msg` and
`euler-ws` run from `/opt/euler` with no working tree and no `EULER_REPO_ROOT`, so
`repo_root()` raises for them by design. If importing `solver.config.env` built the
singleton, euler-auth would die at import, never signal readiness under `Type=notify`, and
take the site down with it — Caddy authenticates every request through it. That has
happened once already, for a different reason, and is written up in web-server-guide §11.
The probe below asks a fresh interpreter, from `/`, with no tree in sight.

**The table and the classes must agree.** Each `NamedTuple` declares the shape; `env.conf`
says which variable carries each field and what it is without one. A field added to a class
and forgotten in the table would fall back to a Python default nobody wrote down; a row left
in the table for a field that no longer exists is a variable operators may still be setting
to no effect. Both are caught here rather than in a deployment.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, NamedTuple, get_type_hints
from unittest import mock

from solver.config.env import COMMON_SECTION, ENV_FILE, MissingSetting, load_spec
from solver.config.paths import repo_root
from solver.web.auth.config import AuthConfig
from solver.web.msg.config import MsgConfig
from solver.web.site.config import SiteConfig
from solver.web.user.config import UserConfig
from solver.web.ws.config import WsConfig

_ROOT: Path = repo_root()

#: Fields whose class default deliberately differs from the table's, and why.
#:
#: `user_socket_dir` is the only one: the class defaults to empty, which *disables* the
#: push to a per-user socket, so a config built directly — a test, a deploy with no web
#: tier — never tries to reach a service that is not there. `from_env` supplies the real
#: directory, which is the point: the running service does have one.
_DELIBERATELY_DIFFER: frozenset[str] = frozenset({'user_socket_dir'})

#: Every service, its section, and the fields that are deliberately **not** the table's to
#: give — each computed rather than configured, and each documented at its `from_env`.
_SERVICES: tuple[tuple[str, type[NamedTuple], frozenset[str]], ...] = (
    ('auth', AuthConfig, frozenset()),
    ('msg', MsgConfig, frozenset()),
    ('site', SiteConfig, frozenset({'repo_root'})),
    ('user', UserConfig, frozenset({'repo_root', 'shell_argv'})),
    ('ws', WsConfig, frozenset({'shell_argv'})),
)


class ImportPurityTests(unittest.TestCase):
    def test_reading_the_table_constructs_no_config(self) -> None:
        """The property the three tree-less services live on."""
        result = subprocess.run(
            [sys.executable, '-c',
             'import sys\n'
             'from solver.config.env import load_spec\n'
             "spec = load_spec('auth')\n"
             "print(spec.entries['socket_path'].env_var,\n"
             "      'config' in vars(sys.modules['solver.config']))"],
            capture_output=True, text=True, cwd='/',
            env={k: v for k, v in os.environ.items() if k != 'EULER_REPO_ROOT'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'EULER_AUTH_SOCKET False')


class TableAgreesWithClassesTests(unittest.TestCase):
    def test_every_configured_field_is_in_the_table(self) -> None:
        for service, cls, computed in _SERVICES:
            spec = load_spec(service)
            declared = set(get_type_hints(cls)) - computed
            with self.subTest(service=service):
                self.assertEqual(declared - set(spec.entries), set(),
                                 f'[{service}] in env.conf names no variable for these fields')

    def test_no_row_is_left_behind(self) -> None:
        """A row for a field no class declares is a variable set to no effect."""
        claimed: set[str] = set()
        for _, cls, _computed in _SERVICES:
            claimed |= set(get_type_hints(cls))
        for service, _cls, _computed in _SERVICES:
            with self.subTest(service=service):
                self.assertEqual(set(load_spec(service).entries) - claimed, set())

    def test_a_class_default_states_the_same_value_as_the_table(self) -> None:
        """The two defaults are a safety net and a catalogue of the same fact.

        A class default is what a *direct* construction gets — `SiteConfig(...)` in a test,
        `site_config()` inside `UserConfig` — while the table's is what `from_env` falls
        back to. They drifted once, in this very change: emptying the class defaults for
        `github_url` silently dropped the GitHub link from every directly-built config.
        """
        for service, cls, _computed in _SERVICES:
            spec = load_spec(service)
            for field, default in cls._field_defaults.items():
                entry = spec.entries.get(field)
                if entry is None or entry.required or not entry.default or field in _DELIBERATELY_DIFFER:
                    continue
                with self.subTest(service=service, setting=field):
                    self.assertEqual(str(default), entry.default,
                                     f'{cls.__name__}.{field} and [{service}] in env.conf '
                                     f'disagree about the default')

    def test_the_common_section_is_shared_by_more_than_one_service(self) -> None:
        """`[common]` earns its place only where a default would otherwise be repeated."""
        users: dict[str, int] = {}
        for service, cls, _computed in _SERVICES:
            for field in set(load_spec(COMMON_SECTION, ENV_FILE).entries) & set(get_type_hints(cls)):
                users[field] = users.get(field, 0) + 1
        self.assertTrue(users, 'nothing reads [common]')
        singles = {field for field, count in users.items() if count < 2}
        self.assertEqual(singles, set(), 'these belong in their own service section')


class ResolutionTests(unittest.TestCase):
    """What a variable, or its absence, resolves to."""

    def test_the_environment_wins_over_the_default(self) -> None:
        with mock.patch.dict(os.environ, {'EULER_SMTP_RELAY': '10.0.0.1:2525'}):
            self.assertEqual(load_spec('auth').raw('smtp_relay'), '10.0.0.1:2525')

    def test_the_default_stands_when_unset(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('EULER_SMTP_RELAY', None)
            self.assertEqual(load_spec('auth').raw('smtp_relay'), '127.0.0.1:8025')

    def test_a_service_entry_overrides_the_common_one(self) -> None:
        """`[auth] socket_path` and `[common] auth_socket` are different sockets."""
        spec = load_spec('auth')
        self.assertEqual(spec.entries['socket_path'].env_var, 'EULER_AUTH_SOCKET')
        self.assertEqual(load_spec('msg').entries['socket_path'].env_var, 'EULER_MSG_SOCKET')

    def test_a_required_setting_exits_naming_its_variable(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('EULER_ADMIN_TOKEN', None)
            with self.assertRaises(MissingSetting) as caught:
                load_spec('auth').raw('admin_token')
        self.assertIn('EULER_ADMIN_TOKEN', str(caught.exception))

    def test_an_uncoercible_value_exits_naming_its_variable(self) -> None:
        with mock.patch.dict(os.environ, {'EULER_WS_DETACHED_TTL': 'soon'}):
            with self.assertRaises(MissingSetting) as caught:
                load_spec('ws').get('detached_ttl', int)
        self.assertIn('EULER_WS_DETACHED_TTL', str(caught.exception))

    def test_an_empty_path_is_omitted_but_an_empty_string_is_a_value(self) -> None:
        """`Path('')` is the current directory, which is never what an unset variable meant."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('EULER_CONTENT_STATIC_DIR', None)
            os.environ.pop('EULER_PROFILE', None)
            values = load_spec('site').read({'static_dir': Path, 'profile': str, 'serve_static': bool})
        self.assertNotIn('static_dir', values)
        self.assertEqual(values['profile'], '')
        self.assertIs(values['serve_static'], False)

    def test_an_unknown_service_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            load_spec('nosuchservice')


class ServiceConfigTests(unittest.TestCase):
    """Each class still resolves to what it resolved to before the table existed."""

    def setUp(self) -> None:
        self._env = mock.patch.dict(os.environ, {'EULER_ADMIN_TOKEN': 'tok',
                                                 'EULER_MSG_ADMIN_TOKEN': 'tok',
                                                 'EULER_BASE_URL': 'https://euler.example/'})
        self._env.start()
        self.addCleanup(self._env.stop)

    def test_auth(self) -> None:
        config = AuthConfig.from_env()
        self.assertEqual(config.state_dir, Path('/var/lib/euler-auth'))
        self.assertEqual(config.socket_group, 'euler-web')
        self.assertEqual(config.admin_socket_group, '')
        self.assertEqual(config.base_url, 'https://euler.example', 'the trailing slash is stripped')
        self.assertEqual(config.smtp_relay, '127.0.0.1:8025')

    def test_msg(self) -> None:
        config = MsgConfig.from_env()
        self.assertEqual(config.socket_path, Path('/run/euler/msg.sock'))
        self.assertEqual(config.admin_socket_path, Path('/run/euler-msg/admin.sock'))
        self.assertEqual(config.user_socket_dir, '/run/euler')

    def test_site(self) -> None:
        config = SiteConfig.from_env()
        self.assertEqual(config.repo_root, _ROOT)
        self.assertEqual(config.static_dir, _ROOT / 'solver/web/content')
        self.assertEqual(config.github_url, 'https://github.com/vikasmunshi/euler')
        self.assertIs(config.serve_static, False)

    def test_ws(self) -> None:
        config = WsConfig.from_env()
        self.assertEqual(config.socket_path, Path('/run/euler/ws.sock'))
        self.assertEqual(config.auth_socket, '/run/euler/auth.sock')
        self.assertEqual(config.detached_ttl, 86400)
        self.assertEqual(config.shell_argv, (sys.executable, '-m', 'solver'))

    def test_user_names_its_socket_for_its_slug(self) -> None:
        with mock.patch.dict(os.environ, {'EULER_USER_SLUG': 'u0a68e0'}):
            config = UserConfig.from_env()
        self.assertEqual(config.slug, 'u0a68e0')
        self.assertEqual(config.socket_path, Path('/run/euler/user-u0a68e0.sock'))

    def test_user_without_a_slug_falls_back_to_the_bare_socket(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('EULER_USER_SLUG', None)
            os.environ.pop('EULER_USER_SOCKET', None)
            self.assertEqual(UserConfig.from_env().socket_path, Path('/run/euler/user.sock'))

    def test_the_site_view_of_a_user_config_carries_no_profile(self) -> None:
        config: Any = UserConfig.from_env().site_config()
        self.assertEqual(config.profile, '')
        self.assertEqual(config.repo_root, _ROOT)


if __name__ == '__main__':
    unittest.main()
