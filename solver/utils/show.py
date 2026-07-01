#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Browser utilities for visualizing solutions."""
from __future__ import annotations

__all__ = ['show']

import threading
import time
import urllib.parse
import urllib.request
from functools import lru_cache
from subprocess import CalledProcessError, DEVNULL, run

from solver.config import ExitCodes, config
from solver.core.problems import Problem
from solver.shell import console, register
from solver.web.cli import ensure_running


# ---------------------------------------------------------------------------
# Browser
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def browser_is_available() -> bool:
    """Return "True" if the "browser" executable is present on "PATH".

    The result is cached after the first call.
    """
    try:
        run('command browser -h 1>/dev/null 2>&1', shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
        return True
    except CalledProcessError:
        return False


@register(help_text='Open problem documentation in a browser.', aliases=('open', 'view'), quietable=True)
def show(problem: Problem, check_for_errors: bool = False) -> int:
    """Open a problem's "problem.html" in the system browser.

    When *problem* is omitted, opens the current problem.

    Prints an error and returns early if:
    - the "browser" command is not available, or
    - the resolved "problem.html" file does not exist.

    Arguments:
        problem:            The `problem` to open; defaults to the current problem.
        check_for_errors:   Whether to check for rendering errors.
    """
    if not browser_is_available():
        console.print('[error]error:[/error] [muted]"browser" command not available; '
                      'use [accent]solver install chrome[/accent] to install Chrome[/muted]')
        return ExitCodes.EXIT_ERROR
    ensure_running()
    url: str = f'http://localhost:{config.server_port}/{problem.number:04d}/'
    if check_for_errors:
        return _check_for_rendering_errors(url)
    pipe = DEVNULL if console.quiet else None
    run(f'browser open {url}', shell=True, stdout=pipe, stderr=pipe)
    return ExitCodes.EXIT_OK


# Chrome's remote-debugging port and the seconds to let async rendering
# (MathJax typesetting, highlight.js) settle after load before reading the
# console. The port must match BROWSER_DEBUG_PORT in the `browser` script.
_BROWSER_DEBUG_PORT: int = 9222
_RENDER_SETTLE_SECONDS: float = 2.5

# MathJax renders a malformed expression as an in-DOM error node ("Math input
# error") rather than logging to the console, so the console listeners never see
# it. This snippet, run after the page settles, harvests those markers: MathJax
# v3 stamps the container with a data-mjx-error attribute and emits an mjx-merror
# (CHTML) / merror (MathML) node; .MathJax_Error covers the v2 fallback.
_MATHJAX_ERROR_SCAN_JS: str = '''(() => {
  const out = [], seen = new Set();
  const add = (m) => { m = (m || '').trim(); if (m && !seen.has(m)) { seen.add(m); out.push(m); } };
  document.querySelectorAll('[data-mjx-error]').forEach(el => add(el.getAttribute('data-mjx-error')));
  document.querySelectorAll('mjx-merror, .MathJax_Error, g[data-mml-node="merror"]')
    .forEach(el => add(el.getAttribute('data-mjx-error') || el.getAttribute('title') || el.textContent));
  return out;
})()'''


def _wait_for_devtools(deadline: float) -> bool:
    """Poll the DevTools /json/version endpoint until it answers or *deadline* passes."""
    version_url = f'http://localhost:{_BROWSER_DEBUG_PORT}/json/version'
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(version_url, timeout=1.0):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def _check_for_rendering_errors(url: str) -> int:
    """Open a problem's page in Chrome, collect console rendering errors, then close the tab.

    Drives the managed Chrome instance over the DevTools protocol (the same
    "--remote-debugging-port" the "browser" script launches) and captures the
    classes of failure that break these notes pages: uncaught JS exceptions,
    "console.error" calls (e.g. MathJax / highlight.js failures), and failed
    resource loads such as 404s on CSS/JS/images. The throwaway tab is always
    closed afterwards. Returns non-zero if any errors were seen.

    Arguments:
        url: The served page to load and inspect.
    """
    try:  # pychrome (the `show` group) drives the DevTools protocol; imported on demand
        import pychrome
    except ImportError as exc:
        console.print(f'[error]show-errors needs the [accent]show[/accent] dependency group '
                      f'({exc.name} is not installed) — run [accent]pip install -e ".\\[show]"[/accent].[/error]')
        return ExitCodes.EXIT_ERROR
    run('browser start', shell=True, stdout=DEVNULL, stderr=DEVNULL)
    if not _wait_for_devtools(time.monotonic() + 5.0):
        console.print('[error]error:[/error] [muted]Chrome DevTools endpoint '
                      f'(port {_BROWSER_DEBUG_PORT}) did not come up[/muted]')
        return ExitCodes.EXIT_ERROR

    errors: list[str] = []

    def record(message: str, *context: object) -> None:
        # Browser extensions inject content scripts that throw into the page's
        # console; those are not the page's own rendering errors, so drop any
        # event whose message or origin points at an extension / devtools URL.
        blob = ' '.join(str(part) for part in (message, *context))
        if 'chrome-extension://' in blob or 'devtools://' in blob:
            return
        errors.append(message)

    def on_exception(exceptionDetails: dict[str, object], **_: object) -> None:  # noqa: N803 (CDP param name)
        exception = exceptionDetails.get('exception')
        description = exception.get('description') if isinstance(exception, dict) else None
        text = description or exceptionDetails.get('text') or 'uncaught exception'
        record(f'JS exception: {text}', exceptionDetails.get('url'))

    def on_console(type: str, args: list[dict[str, object]], **kwargs: object) -> None:  # noqa: A002 (CDP param name)
        if type == 'error':
            message = ' '.join(str(arg.get('value', arg.get('description', ''))) for arg in args)
            record(f'console.error: {message}', kwargs.get('stackTrace'))

    def on_log_entry(entry: dict[str, object], **_: object) -> None:
        if entry.get('level') == 'error':
            record(f'{entry.get("source", "log")}: {entry.get("text", "")}', entry.get('url'))

    default_excepthook = threading.excepthook

    def _silence_recv_loop(args: threading.ExceptHookArgs) -> None:
        # pychrome's receiver thread raises JSONDecodeError on the empty frame
        # Chrome sends as the socket closes during teardown; that noise is harmless.
        thread = args.thread
        if thread is not None and '_recv_loop' in thread.name:
            return
        default_excepthook(args)

    chrome = pychrome.Browser(url=f'http://localhost:{_BROWSER_DEBUG_PORT}')
    tab = chrome.new_tab()
    threading.excepthook = _silence_recv_loop
    try:
        tab.set_listener('Runtime.exceptionThrown', on_exception)
        tab.set_listener('Runtime.consoleAPICalled', on_console)
        tab.set_listener('Log.entryAdded', on_log_entry)
        tab.start()
        tab.Runtime.enable()
        tab.Log.enable()
        tab.Page.enable()
        tab.Page.navigate(url=url, _timeout=10)
        tab.wait(_RENDER_SETTLE_SECONDS)
        scan = tab.Runtime.evaluate(expression=_MATHJAX_ERROR_SCAN_JS, returnByValue=True, _timeout=5)
        for message in (scan.get('result') or {}).get('value') or []:
            record(f'MathJax: {message}')
    finally:
        try:
            tab.stop()
        finally:
            chrome.close_tab(tab)
            threading.excepthook = default_excepthook

    if errors:
        console.print(f'[error]{len(errors)} rendering error(s)[/error] [muted]- {url}[/muted]')
        for error in errors:
            console.print(f'  [muted]{error}[/muted]')
        return ExitCodes.EXIT_ERROR
    console.print(f'[accent]no rendering errors[/accent] [muted]- {url}[/muted]')
    return ExitCodes.EXIT_OK
