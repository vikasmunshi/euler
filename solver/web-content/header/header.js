// Content pages run inside the workspace shell's content iframe; the shell's command
// bar is their header. This script reports the page's context to that bar — the
// current problem / file / section — so it can build the breadcrumb, label the crumb,
// and show the Eval action, and it bounces to /login if the session has ended. There
// is no in-page header any more.
(function () {
    'use strict';

    // Drop a leading `edit` segment (the /edit/<n>/<file> editor route) so the problem
    // number and filename resolve the same as on the read-only /<n>/<file>.
    const RAW = window.location.pathname.split('/').filter(Boolean);
    const SEGMENTS = RAW[0] === 'edit' ? RAW.slice(1) : RAW;
    const PROBLEM_NUMBER = /^\d+$/.test(SEGMENTS[0] || '') ? parseInt(SEGMENTS[0], 10) : 0;
    // A trailing file segment (/<n>/<file>) means this is a code/viewer page.
    const FILENAME = SEGMENTS.length > 1 ? SEGMENTS[SEGMENTS.length - 1] : '';

    // Report this page's context to the shell's command bar (breadcrumb + crumb labels
    // + Eval visibility). `label` names the section for the pages that carry no problem
    // number in their URL.
    function postContext() {
        const path = window.location.pathname;
        const label = path === '/summary' ? 'problems'
            : path === '/edit/progress' ? 'progress'
                : path === '/index' ? 'guides'
                    : path.startsWith('/docs/') ? decodeURIComponent(path.slice(6))
                        : '';
        try {
            window.parent.postMessage({
                type: 'solver:ctx',
                path,
                problem: PROBLEM_NUMBER,
                filename: FILENAME,
                label,
            }, window.location.origin);
        } catch { /* not embedded / cross-origin: nothing to report */ }
    }

    async function init() {
        // Verify we're still signed in before rendering a (possibly cached) app page —
        // an uncached probe, so a signed-out user is bounced to /login even from cache.
        const auth = await fetch('/whoami', { cache: 'no-store', headers: { Accept: 'application/json' } });
        if (!auth.ok) {
            window.top.location.replace('/login');
            return;
        }
        postContext();
    }

    init();
}());
