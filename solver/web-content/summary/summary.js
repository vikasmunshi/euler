(function () {
  'use strict';

  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function parseDate(s) {
    var d = new Date(s + ' GMT');
    return isNaN(d.getTime()) ? null : d;
  }

  function localDate(d) {
    if (!(d instanceof Date) || isNaN(d.getTime())) return '';
    var pad = function (n) { return String(n).padStart(2, '0'); };
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
      ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }

  function pathFor(num) {
    return String(num).padStart(4, '0') + '/';
  }

  // Clicking a problem runs `show <n>` in the shell (via /cmd) rather than navigating
  // the content pane directly, so the console's current problem stays in sync with the
  // view — the shell's `show` sets variables.problem and emits the OSC that moves the
  // pane. The href stays as an open-in-new-tab fallback.
  function showInShell(num) {
    fetch('/cmd', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'show ' + num }),
    }).catch(function () { /* the shell is the source of truth */ });
  }

  function hasLevel(info) {
    return info.level !== '' && info.level !== null && info.level !== undefined;
  }

  function createCell(num, info) {
    var solved = info.solved === true;
    var td = document.createElement('td');
    var classes = ['tooltip', solved ? 'problem_solved' : 'problem_unsolved'];
    if (hasLevel(info)) classes.push('t_' + info.level);
    td.className = classes.join(' ');
    td.setAttribute('data-num', String(num));

    var a = document.createElement('a');
    a.href = pathFor(num);
    a.textContent = String(num);
    td.appendChild(a);

    var span = document.createElement('span');
    span.className = 'tooltiptext_narrow';
    var html = '<div class="tt-title">Problem ' + num + '</div>';
    if (hasLevel(info)) {
      html += '<div class="tt-diff">Difficulty: Level ' + info.level + ' [' + info.pct + '%]</div>';
    }
    if (solved && info.date) {
      html += '<div class="tt-date">Completed on ' + escHtml(localDate(parseDate(info.date)) || info.date) + '</div>';
    }
    if (info.title) {
      html += '<div class="tt-name">&ldquo;' + escHtml(info.title) + '&rdquo;</div>';
    }
    span.innerHTML = html;
    td.appendChild(span);
    return td;
  }

  function createProgressBar(solved, total) {
    var pct = total ? (solved / total * 100) : 0;
    var wrap = document.createElement('div');
    wrap.className = 'grid-progress-wrap';
    wrap.innerHTML =
      '<div class="progress_bar"><div class="progress_bar_block" style="width:' +
        pct.toFixed(1) + '%"></div></div>' +
      '<span class="grid-caption">Solved ' + solved + '&thinsp;/&thinsp;' + total + '</span>';
    return wrap;
  }

  function buildTable(entries, cellsPerRow, fillTo) {
    // entries: array of [num, info]; fillTo: pad to this count with empty cells
    var table = document.createElement('table');
    table.className = 'grid problems_solved_table';
    var total = (fillTo != null) ? fillTo : entries.length;
    for (var i = 0; i < total; i += cellsPerRow) {
      var tr = document.createElement('tr');
      for (var j = 0; j < cellsPerRow; j++) {
        var idx = i + j;
        if (idx < entries.length) {
          tr.appendChild(createCell(entries[idx][0], entries[idx][1]));
        } else if (idx < total) {
          var empty = document.createElement('td');
          empty.className = 'empty-cell';
          tr.appendChild(empty);
        }
      }
      table.appendChild(tr);
    }
    return table;
  }

  function countSolved(entries) {
    var n = 0;
    for (var i = 0; i < entries.length; i++) if (entries[i][1].solved) n++;
    return n;
  }

  function buildById(problems) {
    var container = document.getElementById('by-id');
    var rowsLayout = document.createElement('div');
    rowsLayout.className = 'grids-row-layout';

    var maxNum = 0;
    for (var k in problems) {
      var n = parseInt(k, 10);
      if (n > maxNum) maxNum = n;
    }
    var nGrids = Math.floor((maxNum - 1) / 100) + 1;

    for (var g = 0; g < nGrids; g++) {
      var start = g * 100 + 1;
      var entries = [];
      for (var num = start; num < start + 100; num++) {
        if (problems[num]) entries.push([num, problems[num]]);
      }
      var grid = document.createElement('div');
      grid.className = 'problems_solved_grid';
      grid.id = 'grid_' + g;
      grid.appendChild(buildTable(entries, 10, 100));
      grid.appendChild(createProgressBar(countSolved(entries), entries.length));
      rowsLayout.appendChild(grid);
    }
    container.appendChild(rowsLayout);
  }

  function updateTracker(problems, mtime) {
    var solved = 0;
    var total = 0;
    Object.keys(problems).forEach(function (k) {
      total++;
      if (problems[k].solved) solved++;
    });
    var strong = document.getElementById('tracker-strong');
    var percentage = total > 0 ? (solved / total * 100).toFixed(1) : '0.0';
    if (strong) strong.textContent = 'Solved ' + solved + ' of ' + total + ' problems (' + percentage + '%)';
    var gen = document.getElementById('generated-at');
    if (gen && mtime) gen.textContent = 'Updated: ' + localDate(mtime);
  }

  function initTooltips(root) {
    root.addEventListener('mouseenter', function (e) {
      var td = e.target.closest('.tooltip');
      if (!td) return;
      var tip = td.querySelector('.tooltiptext_narrow');
      if (!tip) return;
      var rect = td.getBoundingClientRect();
      var tw = 210;
      var gap = 4;
      var top = rect.bottom + gap;
      var left = rect.left + rect.width / 2 - tw / 2;
      if (left < 8) left = 8;
      if (left + tw > window.innerWidth - 8) left = window.innerWidth - 8 - tw;
      if (top + tip.offsetHeight > window.innerHeight - 8) top = rect.top - gap - tip.offsetHeight;
      tip.style.top = top + 'px';
      tip.style.left = left + 'px';
      tip.style.visibility = 'visible';
      tip.style.opacity = '1';
    }, true);
    root.addEventListener('mouseleave', function (e) {
      var td = e.target.closest('.tooltip');
      if (!td) return;
      var tip = td.querySelector('.tooltiptext_narrow');
      if (!tip) return;
      tip.style.visibility = 'hidden';
      tip.style.opacity = '0';
    }, true);
  }

  function render(problems, mtime) {
    updateTracker(problems, mtime);
    buildById(problems);
    initTooltips(document.body);
    // Route a problem click through the shell (show <n>) instead of an iframe navigation.
    document.getElementById('by-id').addEventListener('click', function (e) {
      var td = e.target.closest('td[data-num]');
      if (!td || !e.target.closest('a')) return;
      e.preventDefault();
      showInShell(td.getAttribute('data-num'));
    });
  }

  function init() {
    fetch('problems.json', { cache: 'no-cache' })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        var lm = r.headers.get('Last-Modified');
        var mtime = lm ? new Date(lm) : null;
        if (mtime && isNaN(mtime.getTime())) mtime = null;
        return r.json().then(function (problems) {
          return { problems: problems, mtime: mtime };
        });
      })
      .then(function (data) { render(data.problems, data.mtime); })
      .catch(function (e) {
        var strong = document.getElementById('tracker-strong');
        if (strong) strong.textContent = 'Failed to load problems.json: ' + e.message;
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
