// Shared site header: injected into #page-header on every page. The problem
// number comes from the URL (/<n>/ or /<n>/<file>); the summary and progress
// pages have none (number 0).
//
// Exposes window.SolverHeader = {ready, problemNumber, filename}, where `ready`
// resolves once the header DOM is injected and wired — code.js awaits it before
// touching the Eval/Save/Del buttons it owns.
(function () {
    'use strict';

    const SEGMENTS = window.location.pathname.split('/').filter(Boolean);
    const PROBLEM_NUMBER = /^\d+$/.test(SEGMENTS[0] || '') ? parseInt(SEGMENTS[0], 10) : 0;
    // A trailing file segment (/<n>/<file>) means this is a code/viewer page.
    const FILENAME = SEGMENTS.length > 1 ? SEGMENTS[SEGMENTS.length - 1] : '';

    const pad4 = n => String(n).padStart(4, '0');

    // Make an anchor a live link, or an inert .nav-dummy when there is no target.
    function setLink(el, href, external) {
        if (!el) return;
        if (href) {
            el.setAttribute('href', href);
            el.classList.remove('nav-dummy');
            if (external) {
                el.target = '_blank';
                el.rel = 'noopener noreferrer';
            }
        } else {
            el.removeAttribute('href');
            el.classList.add('nav-dummy');
        }
    }

    // Problem links (prev / this problem / next) are derived from the current
    // problem number, and are dummies off a problem (number 0); Euler and GitHub
    // fall back to their site roots off a problem.
    function wireNav() {
        const num = PROBLEM_NUMBER || null;
        const byId = id => document.getElementById(id);
        const problemUrl = n => `/${pad4(n)}/`;

        setLink(byId('nav-prev'), num && num > 1 ? problemUrl(num - 1) : null);
        setLink(byId('nav-problem'), num ? problemUrl(num) : null);
        setLink(byId('nav-next'), num ? problemUrl(num + 1) : null);

        setLink(byId('nav-euler'),
            num ? `https://projecteuler.net/problem=${num}` : 'https://projecteuler.net/progress', true);
        setLink(byId('nav-github'),
            num ? `https://github.com/vikasmunshi/euler/blob/master/solutions/${pad4(num).split('').join('/')}/`
                : 'https://github.com/vikasmunshi/euler', true);

        setLink(byId('nav-summary'), '/summary');
        setLink(byId('nav-progress'), '/progress');
    }

    // The filename + language badge only appear on code pages, which set
    // <body data-language="…">; other pages leave the elements empty/hidden.
    const LANG_ICONS = {
        python: 'devicon-python-original.svg',
        c: 'devicon-c-original.svg',
        json: 'devicon-json-original.svg',
    };

    function fillCodeMeta() {
        const language = document.body.dataset.language;
        if (!language) return;
        const filenameEl = document.getElementById('filename');
        if (filenameEl) filenameEl.textContent = FILENAME;
        const badge = document.getElementById('lang-badge');
        if (!badge) return;
        badge.hidden = false;
        badge.title = language;
        const icon = LANG_ICONS[language];
        if (icon) {
            const img = document.createElement('img');
            img.src = `/vendor/${icon}`;
            img.alt = language;
            badge.appendChild(img);
        } else {
            badge.textContent = language;  // unknown language: fall back to text
        }
    }

    // The account menu (user icon → change password / log out): toggle on click,
    // close on an outside click.
    function wireUserMenu() {
        const button = document.getElementById('user-btn');
        const dropdown = document.getElementById('user-dropdown');
        if (!button || !dropdown) return;
        button.addEventListener('click', (event) => {
            event.stopPropagation();
            const opening = dropdown.hidden;
            dropdown.hidden = !opening;
            button.setAttribute('aria-expanded', String(opening));
        });
        document.addEventListener('click', () => {
            if (!dropdown.hidden) {
                dropdown.hidden = true;
                button.setAttribute('aria-expanded', 'false');
            }
        });
    }

    async function init() {
        const host = document.getElementById('page-header');
        if (!host) return;
        host.innerHTML = await fetch('/header.html').then(r => r.text());
        wireNav();
        fillCodeMeta();
        wireUserMenu();
        document.dispatchEvent(new CustomEvent('header:ready'));
    }

    const domReady = document.readyState === 'loading'
        ? new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve))
        : Promise.resolve();

    window.SolverHeader = {
        ready: domReady.then(init),
        problemNumber: PROBLEM_NUMBER,
        filename: FILENAME,
    };
}());