# Test package for the solver project (unittest discovery root).
#
# `silence()` quiets the three things the suite emits but never asserts on: the shared
# rich console (commands' own stdout — the suite drives their error/progress paths),
# failure-path logging, and aiohttp's plain-str request-key warning. It is a FUNCTION,
# not import-time side effects, because `python -m unittest discover -s tests` (the
# pre-push hook, scripts/setup/hooks/pre-push.template) imports test modules top-level
# and never runs this __init__ — so each noisy module calls `silence()` itself, which
# imports this package (cwd is on the path under `python -m`) under either discovery
# style. Idempotent.
#
# The one deliberate import-time effect is `_pin_subject()`, below: the suite runs as a
# fixed identity, never the host's. Commands register at import against `config.subject`
# (`@register` drops one the subject may not run), so the identity current when the first
# command module is imported decides the whole registry. Left to resolve itself it reads
# /etc/euler/authorizations.json, and a terminal without the `euler-authz` group sees that
# policy with no names in it — the operator becomes a reader, every contributor+ command
# goes missing, and a suite that passes in one terminal fails in the next. The pin must
# precede every test module, so the suite runs with `-t .` (`make test`, the pre-push
# hook), which imports this package first; `test_config` fails loudly when it did not.
import logging
import warnings

from aiohttp.web import NotAppKeyWarning

from solver.auth.identity import os_login, subject_for
from solver.config import config
from solver.shell.command import registry

_aiohttp_patched = False

#: How the pinned subject authenticated — the mark `test_config` checks for.
PINNED_AUTH = 'test-pinned'

#: Whether the pin came before any command registered (or was withheld) — False means some
#: test module imported commands under the host's identity first.
pinned_first = False


def _pin_subject() -> None:
    """Fix the suite's identity: the checkout owner with no deployed policy (`admin`).

    That is the identity a fresh clone resolves to, and the one that registers the whole
    catalogue. The login is kept, so per-user state (`.state/<slug>`) lands where it did.
    """
    global pinned_first
    pinned_first = not registry.all() and not registry.withheld
    config.subject = subject_for(os_login(), owner=True, policy=None)._replace(auth_method=PINNED_AUTH)


_pin_subject()


def _filter_request_key_warning() -> None:
    """Drop aiohttp's NotAppKeyWarning (one write lives inside aiohttp_jinja2, so it
    cannot be fully fixed at our source)."""
    warnings.filterwarnings('ignore', category=NotAppKeyWarning)


def _patch_aiohttp_test_case() -> None:
    """Re-apply the warning filter from inside every AioHTTPTestCase.setUp.

    unittest's runner resets warnings to `default` for the whole run (main.py sets it
    before discovery, so an import-time filter is always shadowed). A filter re-added
    *during* the run wins, and every web tier's requests trip the warning — so wrap the
    one setUp they all inherit rather than touch each get_application. Installed once.
    """
    global _aiohttp_patched
    if _aiohttp_patched:
        return
    from aiohttp.test_utils import AioHTTPTestCase
    original = AioHTTPTestCase.setUp

    def setUp(self: AioHTTPTestCase) -> None:
        _filter_request_key_warning()
        original(self)

    AioHTTPTestCase.setUp = setUp       # type: ignore[method-assign, assignment]
    _aiohttp_patched = True


def silence() -> None:
    """Suppress the suite's incidental console/log/warning output. Idempotent."""
    _filter_request_key_warning()
    logging.disable(logging.CRITICAL)
    # `quiet` also makes the solver pass DEVNULL to any subprocess it shells out to.
    from solver.shell.tty import console
    console.quiet = True
    _patch_aiohttp_test_case()
