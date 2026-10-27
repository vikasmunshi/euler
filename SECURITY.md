# Security

## Reporting a problem

Please report security issues **privately**, not in a public issue or pull request:

- on GitHub, [**Report a vulnerability**](https://github.com/vikasmunshi/euler/security/advisories/new)
  (the repository's Security tab) — preferred, since the report, the discussion and any fix stay
  together in one private advisory;
- or by e-mail to [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com), with "security" in
  the subject.

Helpful to include: what you found, where (a file and line, or a URL and request), how to
reproduce it, and what you think it allows. Reports are read by one person, so expect an
acknowledgement within a few days rather than hours; you will hear what is being done about it.

## Scope

In scope:

- the web front end at euler.vikasmunshi.com and its code under `packages/` — sign-in (SRP),
  sessions, the per-user services and their isolation, the message spool, the vault;
- the encryption of `solutions/private/` (the git filter and the master-key handling);
- the host setup under `scripts/setup/` — units, groups, the firewall and egress proxy.

Out of scope:

- volume: denial of service, load, or flooding the public forms;
- social engineering, and anything that needs access to someone else's device or account;
- the third-party services the project uses (GitHub, Let's Encrypt, the DNS and mail providers);
- what a collaborator can do by design with their own account — the accepted risks are listed in
  [`docs/web-server-guide.md` § 14](docs/web-server-guide.md#14--security-posture).

## Testing

The site is invite-only. Test only against an account you were invited to and data that is
yours; do not try to read or change another collaborator's files, keys or messages, and stop and
report as soon as you can show a problem exists.

## Acknowledgements

Thank you to those who have reported problems:

- **2026-10** — [Perch](https://github.com/lakeday-org/perch), the open-source code scanner, found
  that a sign-in begun before a password reset could still complete with the old password. Fixed
  in v4.11.2.

## How it is built

The design, the controls it relies on and the risks it accepts are documented in the open:

- [`docs/web-server-guide.md`](docs/web-server-guide.md) — the stack, § 14 the security posture and
  its regression guards;
- [`docs/srp-guide.md`](docs/srp-guide.md) — sign-in;
- [`docs/vault-guide.md`](docs/vault-guide.md) — the per-user vault;
- [`docs/secret-sharing-guide.md`](docs/secret-sharing-guide.md) and
  [`docs/gitfilter-guide.md`](docs/gitfilter-guide.md) — the master key and the encrypted solutions.
