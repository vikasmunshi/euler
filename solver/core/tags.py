#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tag/topic glue: the `topics`, `topic` and `update-tags` commands.

The tag system is a double-entry graph. Each problem's ``solution_dir/tags.json``
(Layer 2) lists the tags it carries; the central ``topics/tags.json`` (Layer 1)
lists, per tag, the problems/solutions that carry it (its ``refs`` leg). The two
legs hold the same information at the same granularity — ``pNNNN`` for problem-level
facets (domain, takeaway) and ``pNNNN_sN`` for per-solution techniques.

``update-tags`` is the reconciler that keeps them consistent and feeds the topic
articles under ``topics/``.
"""
from __future__ import annotations

__all__ = ['topics', 'topic', 'update_tags', 'format_vocabulary']

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from solver.config import ExitCodes, config
from solver.core.problems import Problem, solution_dir
from solver.shell import console, register

TAGS_FILENAME = 'tags.json'
FACETS = ('domain', 'technique', 'takeaway')
#: reference-source URLs that are pedagogical framing, not a tag (mirrors the vocabulary build).
_STOPLIST = ('Big_O_notation', 'Time_complexity', 'Computational_complexity', 'Space_complexity',
             'Analysis_of_algorithms', 'Best,_worst_and_average_case', 'Order_of_magnitude')
_TAGS_RE = re.compile(r'<!--\s*tags:\s*\[(.*?)\]\s*-->', re.DOTALL)
_GEN_RE = re.compile(r'(<!--\s*BEGIN problems.*?-->)(.*?)(<!--\s*END problems\s*-->)', re.DOTALL)


# ── paths ─────────────────────────────────────────────────────────────────────────────

def _topics_dir() -> Path:
    return config.root_dir / 'topics'


def _central_path() -> Path:
    return _topics_dir() / TAGS_FILENAME


# ── compact JSON (scalar lists inline, object lists multi-line) ─────────────────────────

def dumps_compact(obj: Any, level: int = 0) -> str:
    """json.dumps-alike: a list of scalars renders on one line; dicts and lists of
    objects stay multi-line at 2-space indent. Keeps big ``refs`` legs to one line."""
    pad, pad2 = '  ' * level, '  ' * (level + 1)
    if isinstance(obj, dict):
        if not obj:
            return '{}'
        body = ',\n'.join(f'{pad2}{json.dumps(k)}: {dumps_compact(v, level + 1)}' for k, v in obj.items())
        return f'{{\n{body}\n{pad}}}'
    if isinstance(obj, list):
        if all(not isinstance(x, (dict, list)) for x in obj):
            return json.dumps(obj)
        if not obj:
            return '[]'
        body = ',\n'.join(f'{pad2}{dumps_compact(x, level + 1)}' for x in obj)
        return f'[\n{body}\n{pad}]'
    return json.dumps(obj)


def _write_central(obj: Any) -> None:
    """The central vocabulary: compact (scalar lists inline) so big refs legs stay one line."""
    _central_path().write_text(dumps_compact(obj) + '\n')


def _write_problem_tags(path: Path, obj: Any) -> None:
    """A per-problem tags.json: plain, human-diffable json.dumps(indent=2)."""
    path.write_text(json.dumps(obj, indent=2) + '\n')


# ── central vocabulary ──────────────────────────────────────────────────────────────────

def _load_central() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(_central_path().read_text())
    return data


def _url_index(central: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Map every reference/additional-reference URL to its (slug, facet)."""
    index: dict[str, tuple[str, str]] = {}
    for tag in central['tags']:
        for url in filter(None, [tag.get('reference'), *tag.get('additional-references', [])]):
            index[url] = (tag['slug'], tag['facet'])
    return index


def _facet_of(central: dict[str, Any]) -> dict[str, str]:
    return {tag['slug']: tag['facet'] for tag in central['tags']}


def format_vocabulary() -> str:
    """The current tag vocabulary as compact markdown, grouped by facet, for a generation prompt.
    Lists each tag as ``- slug — name`` (takeaways append the summary)."""
    tags = _load_central()['tags']
    lines: list[str] = []
    for facet in FACETS:
        entries = sorted((t for t in tags if t['facet'] == facet), key=lambda t: t['slug'])
        lines.append(f'\n### {facet} ({len(entries)})')
        for t in entries:
            extra = f": {t['summary']}" if facet == 'takeaway' and t.get('summary') else ''
            lines.append(f"- {t['slug']} — {t['name']}{extra}")
    return '\n'.join(lines)


def _ref_key(ref: str) -> tuple[int, int]:
    """Natural sort for pNNNN / pNNNN_sN (problem-level sorts before its solutions)."""
    m = re.fullmatch(r'p(\d+)(?:_s(\d+))?', ref)
    if not m:
        return (0, 0)
    return (int(m.group(1)), int(m.group(2)) if m.group(2) is not None else -1)


# ── per-problem tags.json (Layer 2) ─────────────────────────────────────────────────────

def _problem_tags_path(num: int) -> Path:
    return solution_dir(num) / TAGS_FILENAME


def _load_problem_tags(num: int) -> dict[str, Any] | None:
    path = _problem_tags_path(num)
    return json.loads(path.read_text()) if path.exists() else None


def _solution_indices(num: int) -> list[int]:
    """Solution indices present on disk for a problem (from pNNNN_sK.py/.c)."""
    d = solution_dir(num)
    idx = {int(m.group(1)) for f in d.glob(f'p{num:04d}_s*.py')
           if (m := re.fullmatch(rf'p{num:04d}_s(\d+)\.py', f.name))}
    idx |= {int(m.group(1)) for f in d.glob(f'p{num:04d}_s*.c')
            if (m := re.fullmatch(rf'p{num:04d}_s(\d+)\.c', f.name))}
    return sorted(idx)


def _all_problem_numbers() -> list[int]:
    """Every problem that has a notes.html (public + private)."""
    nums: list[int] = []
    for pattern in (f'public/p*/{config.notes_filename}', f'private/p*/p*/{config.notes_filename}'):
        for f in config.solutions_dir.glob(pattern):
            if m := re.search(r'p(\d+)', f.parent.name):
                nums.append(int(m.group(1)))
    return sorted(nums)


def _harvest(num: int, url_index: dict[str, tuple[str, str]]) -> tuple[list[str], list[str]]:
    """Read a problem's notes.html and return (domain slugs, technique slugs) via the
    central URL index. Takeaways are not harvestable (no canonical URL)."""
    notes = solution_dir(num) / config.notes_filename
    domain: set[str] = set()
    technique: set[str] = set()
    if not notes.exists():
        return [], []
    soup = BeautifulSoup(notes.read_text(), 'html.parser')
    for a in soup.find_all('a'):
        if 'reference-source' not in (a.get('class') or []):
            continue
        url = a.get('href')
        if not isinstance(url, str) or not url or any(s in url for s in _STOPLIST):
            continue
        hit = url_index.get(url)
        if hit is None:
            continue
        slug, facet = hit
        (domain if facet == 'domain' else technique).add(slug)
    return sorted(domain), sorted(technique)


def _bootstrap_problem(num: int, url_index: dict[str, tuple[str, str]]) -> dict[str, Any]:
    """Create a per-problem tags.json from the notes: domain, and techniques expanded to
    every solution index on disk (approximate; narrowed later per index). Takeaways empty."""
    domain, technique = _harvest(num, url_index)
    indices = _solution_indices(num)
    techniques = {f's{k}': list(technique) for k in indices} if indices else {}
    return {'domain': domain, 'takeaways': [], 'techniques': techniques, 'new-tags': []}


# ── topic articles ──────────────────────────────────────────────────────────────────────

def _iter_articles() -> list[Path]:
    return sorted(p for p in _topics_dir().rglob('*.md'))


def _article_tags(text: str) -> list[str]:
    m = _TAGS_RE.search(text)
    if not m:
        return []
    return [s.strip() for s in m.group(1).split(',') if s.strip()]


def _find_article(name: str) -> Path | None:
    name = name.removesuffix('.md')
    for path in _iter_articles():
        rel = path.relative_to(_topics_dir()).with_suffix('')
        if str(rel) == name or path.stem == name:
            return path
    return None


# ══ commands ════════════════════════════════════════════════════════════════════════════

@register(requires='reader', help_text='Show the tags on a problem and the topics that cover them.')
def topics(problem: Problem) -> int:
    """List a problem's tags (grouped by facet) and the topic articles that cover any of them."""
    data = _load_problem_tags(problem.number)
    if data is None:
        console.print(f'[error]error:[/error] no {TAGS_FILENAME} for problem {problem.number} '
                      f'(run [accent]update-tags[/accent])')
        return ExitCodes.EXIT_ERROR
    console.print(f'[accent]Problem {problem.number}[/accent] — {problem.title}')
    own: set[str] = set(data.get('domain', [])) | set(data.get('takeaways', []))
    if data.get('domain'):
        console.print(f'  [muted]domain   [/muted] {", ".join(data["domain"])}')
    for sidx, slugs in sorted(data.get('techniques', {}).items()):
        if slugs:
            own |= set(slugs)
            console.print(f'  [muted]technique[/muted] [accent.dim]{sidx}[/accent.dim] {", ".join(slugs)}')
    if data.get('takeaways'):
        console.print(f'  [muted]takeaway [/muted] {", ".join(data["takeaways"])}')
    covering = [str(p.relative_to(_topics_dir()).with_suffix(''))
                for p in _iter_articles() if own & set(_article_tags(p.read_text()))]
    console.print(f'  [muted]topics   [/muted] {", ".join(covering) if covering else "(none)"}')
    return ExitCodes.EXIT_OK


@register(requires='reader', help_text='Show a topic article\'s tags and the problems/solutions they map to.')
def topic(name: str) -> int:
    """List a topic article's declared tags and, per tag, the problems/solutions on its central leg."""
    path = _find_article(name)
    if path is None:
        console.print(f'[error]error:[/error] no topic article {name!r} under topics/')
        return ExitCodes.EXIT_ERROR
    tags = _article_tags(path.read_text())
    if not tags:
        console.print(f'[warning]{path.name}[/warning] declares no tags (add a <!-- tags: [...] --> comment)')
        return ExitCodes.EXIT_OK
    central = {t['slug']: t for t in _load_central()['tags']}
    console.print(f'[accent]{path.relative_to(_topics_dir()).with_suffix("")}[/accent] — tags: {", ".join(tags)}')
    seen: set[str] = set()
    for slug in tags:
        tag = central.get(slug)
        if tag is None:
            console.print(f'  [error]{slug}[/error] — not in vocabulary')
            continue
        refs = tag.get('refs', [])
        seen.update(refs)
        console.print(f'  [muted]{tag["facet"]:9}[/muted] [accent.dim]{slug}[/accent.dim] '
                      f'({len(refs)}) {", ".join(refs) if refs else "(unmapped)"}')
    problems = sorted({r.split('_')[0] for r in seen}, key=_ref_key)
    console.print(f'  [muted]→ {len(problems)} problem(s):[/muted] {", ".join(problems)}')
    return ExitCodes.EXIT_OK


# ── the reconciler ──────────────────────────────────────────────────────────────────────

def _head_central() -> dict[str, Any] | None:
    """The committed ``topics/tags.json`` at HEAD, for the maintainer-intent diff."""
    try:
        proc = subprocess.run(['git', '-C', str(config.root_dir), 'show', f'HEAD:topics/{TAGS_FILENAME}'],
                              capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return json.loads(proc.stdout) if proc.returncode == 0 and proc.stdout.strip() else None


def _apply_membership(ptags: dict[int, dict[str, Any]], slug: str, facet: str, ref: str, present: bool) -> None:
    """Add or remove a tag from the per-problem file implied by *ref* (pNNNN / pNNNN_sN)."""
    m = re.fullmatch(r'p(\d+)(?:_s(\d+))?', ref)
    if not m:
        return
    num = int(m.group(1))
    data = ptags.setdefault(num, {'domain': [], 'takeaways': [], 'techniques': {}, 'new-tags': []})
    if facet == 'technique':
        idx = f's{m.group(2)}' if m.group(2) is not None else (f's{_solution_indices(num)[0]}'
                                                               if _solution_indices(num) else 's0')
        bucket = data['techniques'].setdefault(idx, [])
    else:
        bucket = data['domain'] if facet == 'domain' else data['takeaways']
    if present and slug not in bucket:
        bucket.append(slug)
    elif not present and slug in bucket:
        bucket.remove(slug)


def _maintainer_diff(current: dict[str, Any], ptags: dict[int, dict[str, Any]]) -> int:
    """Apply maintainer edits to the central refs (vs HEAD) into the per-problem files first,
    so the maintainer wins over solver/contributor on the subsequent reconcile."""
    head = _head_central()
    if head is None:
        return 0
    facet = _facet_of(current)
    head_refs = {t['slug']: set(t.get('refs', [])) for t in head['tags']}
    changes = 0
    for tag in current['tags']:
        slug, cur = tag['slug'], set(tag.get('refs', []))
        was = head_refs.get(slug)
        if was is None:
            continue  # brand-new tag in central; its refs will be built from per-problem files
        for ref in cur - was:
            _apply_membership(ptags, slug, facet[slug], ref, present=True)
            changes += 1
        for ref in was - cur:
            _apply_membership(ptags, slug, facet[slug], ref, present=False)
            changes += 1
    return changes


def _promote_new_tags(central: dict[str, Any], ptags: dict[int, dict[str, Any]]) -> tuple[int, list[str]]:
    """Move each per-problem `new-tags` proposal into the central vocabulary (bookmark rule),
    then into the file's proper facet bucket. Returns (count, warnings)."""
    known = {t['slug'] for t in central['tags']}
    known_refs = {t['reference'] for t in central['tags'] if t['reference']}
    warnings: list[str] = []
    added = 0
    for num, data in ptags.items():
        for prop in list(data.get('new-tags', [])):
            slug, facet = prop.get('slug'), prop.get('facet')
            if not slug or facet not in FACETS:
                warnings.append(f'p{num:04d}: malformed new-tag {prop!r}')
                continue
            if slug not in known:
                # Bookmark rule: strip the #anchor for the reference, unless the base URL is
                # already another tag's reference (the anchor is load-bearing identity — keep it).
                ref = prop.get('reference') or ''
                if '#' in ref and ref.split('#', 1)[0] not in known_refs:
                    reference, extra = ref.split('#', 1)[0], [ref]
                elif '#' in ref:
                    reference, extra = ref, []
                else:
                    reference, extra = (ref or None), []
                central['tags'].append({'slug': slug, 'facet': facet, 'name': prop.get('name', slug),
                                        'reference': reference, 'additional-references': extra,
                                        'summary': prop.get('summary', ''), 'refs': []})
                known.add(slug)
                if reference:
                    known_refs.add(reference)
                added += 1
            # file the promoted slug into the correct bucket
            if facet == 'technique':
                for idx in prop.get('applies-to') or [f's{k}' for k in _solution_indices(num)] or ['s0']:
                    data['techniques'].setdefault(idx, [])
                    if slug not in data['techniques'][idx]:
                        data['techniques'][idx].append(slug)
            else:
                bucket = data['domain'] if facet == 'domain' else data['takeaways']
                if slug not in bucket:
                    bucket.append(slug)
        data['new-tags'] = []
    return added, warnings


def _rebuild_refs(central: dict[str, Any], ptags: dict[int, dict[str, Any]]) -> None:
    """Rebuild every tag's central `refs` leg from the per-problem files."""
    refs: dict[str, set[str]] = defaultdict(set)
    for num, data in ptags.items():
        for slug in data.get('domain', []):
            refs[slug].add(f'p{num:04d}')
        for slug in data.get('takeaways', []):
            refs[slug].add(f'p{num:04d}')
        for idx, slugs in data.get('techniques', {}).items():
            for slug in slugs:
                refs[slug].add(f'p{num:04d}_{idx}')
    for tag in central['tags']:
        tag['refs'] = sorted(refs.get(tag['slug'], set()), key=_ref_key)


def _validate(central: dict[str, Any], ptags: dict[int, dict[str, Any]]) -> list[str]:
    """Unknown slugs, facet violations, and unpromoted new-tags across the per-problem files."""
    facet = _facet_of(central)
    problems: list[str] = []
    for num, data in ptags.items():
        tag = f'p{num:04d}'
        for slug in data.get('domain', []):
            if slug not in facet:
                problems.append(f'{tag}: unknown domain tag {slug!r}')
            elif facet[slug] != 'domain':
                problems.append(f'{tag}: {slug!r} is {facet[slug]}, filed under domain')
        for slug in data.get('takeaways', []):
            if slug not in facet:
                problems.append(f'{tag}: unknown takeaway tag {slug!r}')
            elif facet[slug] != 'takeaway':
                problems.append(f'{tag}: {slug!r} is {facet[slug]}, filed under takeaways')
        for idx, slugs in data.get('techniques', {}).items():
            for slug in slugs:
                if slug not in facet:
                    problems.append(f'{tag}: unknown technique tag {slug!r} ({idx})')
                elif facet[slug] != 'technique':
                    problems.append(f'{tag}: {slug!r} is {facet[slug]}, filed under techniques')
        if data.get('new-tags'):
            problems.append(f'{tag}: {len(data["new-tags"])} unpromoted new-tag(s)')
    return problems


def _regen_articles(central: dict[str, Any], write: bool) -> list[str]:
    """Refill each article's generated problem list from its declared tags. Returns issues."""
    by_slug = {t['slug']: t for t in central['tags']}
    issues: list[str] = []
    for path in _iter_articles():
        text = path.read_text()
        tags = _article_tags(text)
        for slug in tags:
            if slug not in by_slug:
                issues.append(f'{path.name}: declares unknown tag {slug!r}')
        # An article's reading list is distinct problems (collapse pNNNN_sN -> pNNNN).
        problems = sorted({r.split('_')[0] for slug in tags
                           for r in by_slug.get(slug, {}).get('refs', [])}, key=_ref_key)
        block = '\n'.join(problems)
        new_text = _GEN_RE.sub(lambda m: f'{m.group(1)}\n{block}\n{m.group(3)}', text)
        if write and new_text != text and _GEN_RE.search(text):
            path.write_text(new_text)
    return issues


@register(requires='maintainer',
          help_text='Reconcile the tag graph: per-problem tags.json <-> central topics/tags.json -> articles.')
def update_tags(check: bool = False) -> int:
    """The glue for the double-entry tag graph.

    Order (maintainer beats solver/contributor): apply maintainer edits to the central
    ``refs`` (vs HEAD) into the per-problem files first; bootstrap a ``tags.json`` for any
    problem missing one (harvested from notes); promote ``new-tags`` proposals into the
    vocabulary; rebuild every central ``refs`` leg from the per-problem files; regenerate the
    topic articles' problem lists.

    With ``--check`` nothing is written: report unknown slugs, facet violations and unpromoted
    proposals, and exit non-zero if the graph is inconsistent.
    """
    central = _load_central()
    url_index = _url_index(central)
    nums = _all_problem_numbers()

    # Load every per-problem file; note which need bootstrapping.
    ptags: dict[int, dict[str, Any]] = {}
    missing: list[int] = []
    for num in nums:
        data = _load_problem_tags(num)
        if data is None:
            missing.append(num)
        else:
            data.setdefault('domain', [])
            data.setdefault('takeaways', [])
            data.setdefault('techniques', {})
            data.setdefault('new-tags', [])
            ptags[num] = data

    if check:
        issues = _validate(central, ptags)
        issues += _regen_articles(central, write=False)
        if missing:
            issues.append(f'{len(missing)} problem(s) have no {TAGS_FILENAME} (run update-tags)')
        for msg in issues:
            console.print(f'  [error]•[/error] {msg}')
        console.print(f'[{"error" if issues else "accent"}]update-tags --check: '
                      f'{len(issues) or "no"} issue(s)[/]')
        return ExitCodes.EXIT_ERROR if issues else ExitCodes.EXIT_OK

    diff_changes = _maintainer_diff(central, ptags)
    for num in missing:
        ptags[num] = _bootstrap_problem(num, url_index)
    promoted, warnings = _promote_new_tags(central, ptags)
    _rebuild_refs(central, ptags)
    art_issues = _regen_articles(central, write=True)

    # Re-sort vocabulary (domain, technique, takeaway; by slug) and persist everything.
    order = {'domain': 0, 'technique': 1, 'takeaway': 2}
    central['tags'].sort(key=lambda t: (order.get(t['facet'], 9), t['slug']))
    _write_central(central)
    for num, data in ptags.items():
        _write_problem_tags(_problem_tags_path(num), data)

    for msg in warnings + art_issues:
        console.print(f'  [warning]•[/warning] {msg}')
    console.print(f'[accent]update-tags:[/accent] {len(ptags)} problem file(s), '
                  f'{len(missing)} bootstrapped, {promoted} tag(s) promoted, '
                  f'{diff_changes} maintainer edit(s) applied')
    return ExitCodes.EXIT_OK
