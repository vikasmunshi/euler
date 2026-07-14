# Real multi-tenant web access — design of record

> **Status: design, in progress.** This supersedes the web tier's per-*profile*
> shared-uid model ([secure-web-server.md](secure-web-server.md) DD-13) with a
> per-*user* one, and **replaces the dropped Phase 7 brokers** (DD-15): instead of
> brokering secrets away from a shared RCE uid, we *invert* the problem — each user
> brings their own keys and runs in their own uid, so a user's secrets are exposed
> only to that user's own code. This is the JupyterHub / multi-tenant dev-environment
> shape, built on the crypto and auth primitives the project already has.
>
> Sections marked **DECIDED** capture choices already made; **OPEN** flags a decision
> we still need to resolve. Nothing here is built yet.

## 1 · Why — the pivot

The delivered web front end (Phases 1–6) runs each web *rung* as one shared uid
(`euler-ws-reader/contributor/maintainer`). Two consequences drove the whole of the
now-dropped Phase 7:

- **No secret can rest on a shared RCE uid.** A key readable by `euler-ws-maintainer`
  is readable by *every* maintainer's shell — so the operator's Anthropic key and the
  crypto master key had to be kept off the web tier and reached only through brokers
  (`euler-ai`, `euler-git`), with identity and authorship reduced to *claim-based*
  headers because `/proc/<pid>/environ` is same-uid-readable (the DD-9 reality).
- **The git story was contorted:** one shared working tree, a broker doing
  temporary-index commits to `web/*` branches, because per-user worktrees would have
  needed the master key on the web tier.

The brokers are the *symptom*. The *cause* is the shared uid. Give each collaborator
their **own uid**, and the secret problem inverts: a user's own key, in their own
home, readable only by their uid, exposed only to their own shell — which is not a
leak, because they own it. Kernel identity (`SO_PEERCRED`, real uids) replaces
claim-based headers. Per-user worktrees on per-user branches make git trivial.

This is a **real collaborative tool** for an invited set of *trusted, named*
collaborators — not an anonymous showcase. That framing is what makes the trade-offs
below acceptable (see [§7 Threat model](#7--threat-model)).

## 2 · The shape (target)

```
  browser ──TLS──▶ Caddy (edge) ──forward_auth──▶ auth service ─▶ (email → user slug)
                     │  routes /ws and content BY USER (X-User-Slug)
                     ▼
        per-user instance, born as euler-user-<slug> (systemd, no setuid)
          ├─ home:     /var/lib/euler-users/<slug>            (0700, uid-private)
          │    ├─ .euler/id        the user's X25519 private key (their upload / generated)
          │    ├─ .euler/env       the user's own ANTHROPIC_API_KEY (their vault)
          │    └─ .state/…         their shell history / last problem / session
          ├─ worktree: a per-user checkout of the repo on branch  user/<slug>
          │    └─ solutions/private/**  PLAINTEXT — smudged with the master key the
          │         user unwraps via THEIR private key (enc-key.json, user-authorize)
          └─ shell:    python -m solver, identity = this user (real uid, real key)
```

Everything a user touches is theirs: their uid, home, keys, worktree, branch. Their
Anthropic key is their own billing. Their commits are authored and pushed as
themselves. Revocation is `key-rekey` (drops their master-key access) + disabling the
account (stops their instance).

## 3 · The secrets inversion — DECIDED

**Each user brings their own keys; nothing is brokered.** The mechanism already
exists in `solver.crypto`:

- **The crypto master key** is wrapped, per authorized X25519 public key, in
  `keys/enc-key.json` (proof-of-possession: hold the matching private key → unwrap the
  master key → decrypt/smudge). `user-authorize <pubkey>` adds an entry; `key-rekey`
  rotates the master key and re-wraps only to still-authorized keys (**revocation**);
  `user --regen` rotates a user's own keypair carrying access forward.
- **Per user:** the user generates *or uploads* an X25519 keypair. The **private key**
  lands in their per-user home (`~/.euler/id`, `0600`, their uid only). Their **public
  key** is enrolled with `user-authorize` — an **operator/admin trust action** (it
  grants decryption of the whole private corpus, so it can never be self-service; it is
  the same trust gate as the invite). Now their uid, and only their uid, can smudge the
  private solutions in their own worktree.
- **The Anthropic key** is likewise *theirs*: uploaded via the web **vault** into their
  per-user env, read only by their uid. `claude-api` / `euler-solve` in their shell use
  it directly — no broker, no operator budget, no shared key.

Because a user's private key sits in their uid-private home and is never
same-uid-shared with anyone else, uploading it to the vault is **not** the
DD-15-rejected vault: that objection was "a secret on a *shared* uid is readable by
every tenant of that uid." Here every tenant is a uid of one.

**Consequence for AR-2 / the master key.** Today the web tier never holds the master
key. Under this model, *every authorized user's uid can unwrap it* (that is the point —
they smudge their own worktree). This is a deliberate escalation of the
[AR-2](security-notes.md) posture and must be recorded as a new accepted risk: an
authorized collaborator can decrypt the full encrypted corpus and forge ciphertext (the
SEC-01 class). It is acceptable **only** because authorization is an explicit,
per-person, revocable trust decision over a *named invite list* — exactly the trust the
operator already extends by inviting them. **OPEN:** do we want a tier that gets a web
account but is **not** key-authorized (public-solutions-only worktree, no private
plaintext)? That would preserve AR-2 for the untrusted-newcomer case and reserve key
access for graduated trust. (Leaning: yes — it maps the old `reader` vs `contributor`
line onto *key-authorized or not*, see §5.)

## 4 · Per-user provisioning without setuid — OPEN (leaning stated)

The delivered design's backbone is **no service runs as root, no process changes uid**
(DD-2/DD-4): each instance is *born* as the right uid via a systemd `User=`. Preserving
that per-user means **one systemd template instance per user**, and provisioning the
uid + home + worktree when the account is created.

- **Instances:** `euler-ws@<slug>.service`, `User=euler-user-<slug>`, socket
  `/run/euler/ws-<slug>.sock`. **Leaning: socket-activated** (`euler-ws@<slug>.socket`)
  so idle users cost nothing and systemd starts the instance on first attach — no
  always-on process per invitee.
- **Provisioning (at `users add`, sudo-gated, DD-6):** create the system user
  `euler-user-<slug>`, its home, its `.euler/` (empty until the user uploads keys), and
  its **worktree** — `git worktree add /…/<slug> user/<slug>` off master, sharing the
  object store. **OPEN:** shared worktree vs. per-user clone-with-alternates. A worktree
  shares one `.git` (multi-writer ref races, and `.git` write-access spreads across
  uids); a clone with read-only shared **alternates** gives each user their own `.git`
  for refs/commits over a shared read-only object store — cleaner isolation, slightly
  more setup. (Leaning: **clone + alternates**.)
- **De-provisioning (at `users remove` / `disable`):** stop the instance, `key-rekey`
  to drop the user's master-key access, archive or drop their worktree/home.

**Alternative considered — a privileged spawner (JupyterHub model):** one small root
(or `CAP_SETUID`) supervisor that forks each shell setuid'd to the user. Fewer moving
units, but it reintroduces a privileged component the delivered design spent real effort
to avoid. **Leaning: per-user systemd instances, no spawner** — keep the no-setuid
property; the invite list is small enough that N instances is fine.

## 5 · Identity, profiles & routing — OPEN

- **Terminal is always the local OS user** (DECIDED). Unchanged from today's
  `resolve_subject`: the checkout owner → the operator; a real non-owner OS login → that
  user. Multi-tenancy is a *web* concern; the box's terminal is whoever logged into it.
- **Web identity = the authenticated account → its own uid.** `forward_auth` resolves
  the email to a **user slug**; Caddy routes `/ws` and the content service to that
  user's per-user socket (by `X-User-Slug`, the per-*user* analogue of today's
  `X-Profile`). **OPEN:** Caddy dynamic-upstream-from-header needs verifying (a computed
  `unix//run/euler/ws-{header}.sock`, or forward_auth returns the socket path outright).
- **What happens to the reader/contributor/maintainer ladder?** Two coherent options,
  **OPEN**:
  1. **Profiles collapse into per-user isolation.** Every web account is a full tenant
     in its own sandbox — it can do anything to *its own* worktree/branch, and isolation
     (not a capability gate) is the boundary. The RBAC kernel (DD-12) still gates the
     *infra* commands (`git-publish` to master, `key-*`, `users`) to the local admin, but
     the reader/contributor/maintainer distinction largely disappears.
  2. **Profiles survive as a trust dial**, re-expressed per-user: *key-authorized*
     (can see/edit private plaintext) vs. *not* (public-only worktree), plus whether the
     account may push, run AI, etc. This keeps the graduated-trust story (§3's OPEN) and
     the newcomer-can't-decrypt-everything guard.
  - (Leaning: **option 2** — per-user uid for *isolation*, a small capability/trust
    dial for *what a newcomer may reach*, so trust still graduates.)

## 6 · What carries over vs. changes

| Delivered (Phases 1–6) | Multi-tenant |
|---|---|
| TLS edge, egress firewall, SRP auth, forward_auth | **kept** — the edge and auth service are unchanged in shape |
| `authorizations.json` RBAC kernel (DD-12) | **kept**, re-scoped: gates infra/admin; per-user isolation replaces per-profile capability rungs (§5) |
| Per-profile shared uids `euler-ws-<profile>` (DD-13) | **replaced** by per-user `euler-user-<slug>` instances (§4) |
| One shared working tree, no master key on web tier | **replaced** by per-user worktrees, master key unwrapped per-user via their own key (§3) |
| Shell ticket carries `(email, profile)` (DD-9) | carries the user identity → the per-user uid; kernel `SO_PEERCRED` now authoritative, claim-based headers gone |
| DD-15 brokers (`euler-ai`, `euler-git`) | **dropped** — users bring their own keys; git is per-user native |
| `euler-solve` / `claude-api` need a broker over the web | run natively in the user's shell with the user's own key + CLI |

## 7 · Threat model

The trust boundary is the **invite list** — a small set of *named, trusted*
collaborators, as today ([security-notes.md](security-notes.md)). What changes:

- **Gained:** kernel-authoritative per-user identity (no same-uid masquerade *between
  users*); per-user blast radius (a compromised user's shell reaches only *their* home,
  keys, worktree — not other users'); no operator secret on the web tier at all.
- **Accepted (new AR):** an authorized user's uid can unwrap the master key (§3) — the
  SEC-01 class, accepted for *key-authorized* collaborators as an explicit, revocable,
  per-person trust decision. Mitigated by the §5-option-2 tier for un-graduated accounts.
- **Unchanged:** a collaborator's login is still host code execution *as their own uid*
  (the AR-1 posture, now better contained — their own sandbox, their own egress).

## 8 · Open decisions (to resolve before building)

1. **Graduated trust (§3/§5):** is there a web tier that is *not* key-authorized
   (public-only, no private plaintext)? — leaning **yes**.
2. **Worktree vs. clone-with-alternates (§4):** how each user's checkout shares the
   object store — leaning **clone + read-only alternates**.
3. **Provisioning trigger & lifecycle (§4):** socket-activated per-user instances;
   what exactly `users add`/`remove`/`disable` provision and tear down.
4. **Caddy per-user routing (§5):** dynamic upstream from an `X-User-Slug` header, or
   forward_auth returns the socket path.
5. **Key upload UX (§3):** generate-in-browser vs. upload-existing for the X25519
   keypair; how the public key reaches `user-authorize` (admin action) and how the
   Anthropic key is stored in the per-user vault.
6. **Disk & scale (§4):** object-store sharing keeps this bounded for an invite list;
   confirm the ceiling we design for.

## 9 · Build-plan sketch (subject to §8)

1. **Per-user identity in `solver/auth`:** email → user slug → per-user uid/home; the
   web plane of `resolve_subject` resolves a *user*, not a profile.
2. **Provisioning kit** (`users add` extension, sudo-gated): create the uid, home,
   `.euler/`, and worktree/clone; enroll the uploaded public key (`user-authorize`);
   the socket-activated `euler-ws@<slug>` unit.
3. **The vault** (web): upload/rotate the X25519 keypair and the Anthropic key into the
   per-user home; surface the public key for the admin's `user-authorize` step.
4. **Caddy per-user routing** + the ws/content services made per-user (drop the
   per-profile instances).
5. **Per-user git**: native `git-commit`/`git-push` on `user/<slug>`; the operator
   merges to master locally (the review gate the delivered design already keeps).
6. **Migration & teardown**: retire the DD-13 per-profile instances and the (unbuilt)
   broker scaffolding; new AR in security-notes; docs.
