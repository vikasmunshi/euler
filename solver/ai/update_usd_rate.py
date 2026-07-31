#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `update-usd-rate` command: refresh the USD→EUR reference rate.

The Claude API prices every model in US dollars; `costs` reports the accumulated spend in
euros. The conversion is a single managed setting, `ecb_usd_rate` in `solver/config.json`,
and currencies drift daily — so rather than hand-edit it, this command refreshes it from
the European Central Bank's euro reference rates (`eurofxref-daily.xml`): authoritative,
free, and needing no key. The feed quotes `1 EUR = N USD`, so `ecb_usd_rate` is `N`.

Nothing else is touched: the rate is written back through `config.dump_managed_config()`,
which round-trips only the settings named in `Config.managed`.

This used to be the second half of `update-models`. The two moved apart because they are
different jobs at different rungs — one regenerates package source from the model
catalogue, the other refreshes one number that only `costs` reads — and because a rate that
drifts daily made `update-models --check` report stale on almost every run.

Exposed as the `update-usd-rate` shell command: `solver "update-usd-rate"` to refresh,
`solver "update-usd-rate --check"` to verify (exit 1 if the rate has moved, writing nothing).
"""
from __future__ import annotations

__all__ = ['update_usd_rate']

import re

from solver.config import ExitCodes, config
from solver.core.download import download_file
from solver.core.git import commit_regenerated
from solver.shell import console, register
from solver.utils.quips import quips

#: The ECB euro foreign-exchange reference rates (daily, free, no API key) — the authoritative
#: source for EUR conversions. It quotes `1 EUR = N USD`, so `ecb_usd_rate` is `N`.
ECB_FX_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

#: Matches the USD reference rate in the ECB feed: `<Cube currency='USD' rate='1.1591'/>`.
_USD_RATE_RE = re.compile(r"""currency=['"]USD['"]\s+rate=['"]([\d.]+)['"]""")

#: Below this the two rates round to the same displayed figure — not worth a write.
_EPSILON = 5e-5


def _fetch_ecb_usd_rate() -> float | None:
    """Fetch the current USD→EUR rate (euros per dollar) from the ECB daily reference feed.

    The ECB quotes `1 EUR = N USD`
    Returns None if the feed is unreachable or carries no USD rate.
    """
    raw: bytes = download_file(ECB_FX_URL, refresh=True)
    if not (match := _USD_RATE_RE.search(raw.decode('utf-8'))):
        console.print(f'[error]error:[/error] no USD rate found in the ECB feed at {ECB_FX_URL}')
        return None
    return float(match.group(1))


# Maintainer: the rate is a *managed setting* — data in `solver/config.json`, the same file
# `manage-config` edits — and it shapes what `costs` reports about API spend. Curating that
# is maintainer's work. It writes no code, which is what separates it from `update-models`
# above it: this command's blast radius is one float that only a cost report reads.
#
# Unlike `update-models`, the write target is per-clone and per-user, so this completes
# wherever it is run. Egress: the ECB feed is allowlisted in scripts/setup/egress.sh.
@register(requires='maintainer', quietable=True)
def update_usd_rate(check: bool = False) -> int:
    """Refresh the USD→EUR rate used to report API costs.

    Fetches the euro reference rate from the European Central Bank's daily feed and writes it
    to `ecb_usd_rate` in `config.json`, the managed setting `costs` converts API spend with.
    A rate within a rounding step of the stored one is left alone. Nothing else is touched.

    A rate that moved is committed, staging that one file and nothing beside it.

    Args:
        check: Write nothing and fail if the stored rate is out of date. Defaults to False,
            which refreshes it in place. The rate drifts daily, so `--check` will usually
            report it as stale.
    """
    if (rate := _fetch_ecb_usd_rate()) is None:
        return ExitCodes.EXIT_ERROR
    if abs(rate - config.ecb_usd_rate) <= _EPSILON:
        if check:
            console.print('[success]USD→EUR rate is up to date[/success]')
            return ExitCodes.EXIT_OK
        console.print('[muted]USD→EUR rate already up to date[/muted]')
        # Still offered to the committer: an earlier run may have written the rate and failed
        # to commit it, and "up to date" must not mean "left dirty forever". Clean is a no-op.
        return commit_regenerated('update-usd-rate', quips['update-usd-rate'])
    if check:
        console.print(f'[error]USD→EUR rate out of date[/error] (run [accent]update-usd-rate[/accent]): '
                      f'[accent]{config.ecb_usd_rate} → {rate}[/accent]')
        return ExitCodes.EXIT_ERROR

    previous, config.ecb_usd_rate = config.ecb_usd_rate, rate
    config.dump_managed_config()
    console.print(f'[success]updated[/success] ecb_usd_rate in '
                  f'{config.managed_config_file.relative_to(config.root_dir)} '
                  f'([accent]{previous} → {rate}[/accent])')
    return commit_regenerated('update-usd-rate', quips['update-usd-rate'], [f'ecb_usd_rate: {previous} → {rate}'])
