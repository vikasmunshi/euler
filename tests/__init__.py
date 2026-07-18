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
import logging
import warnings

from aiohttp.web import NotAppKeyWarning

_aiohttp_patched = False


def _filter_request_key_warning() -> None:
    """Drop aiohttp's NotAppKeyWarning (one write lives inside aiohttp_jinja2, so it
    cannot be fully fixed at our source)."""
    warnings.filterwarnings('ignore', category=NotAppKeyWarning)


def _patch_aiohttp_test_case() -> None:
    """Re-apply the warning filter from inside every AioHTTPTestCase.setUp.

    unittest's runner resets warnings to ``default`` for the whole run (main.py sets it
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

    AioHTTPTestCase.setUp = setUp       # type: ignore[method-assign]
    _aiohttp_patched = True


def silence() -> None:
    """Suppress the suite's incidental console/log/warning output. Idempotent."""
    _filter_request_key_warning()
    logging.disable(logging.CRITICAL)
    # `quiet` also makes the solver pass DEVNULL to any subprocess it shells out to.
    from solver.shell.tty import console
    console.quiet = True
    _patch_aiohttp_test_case()
