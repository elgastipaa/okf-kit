# OKF kit — durable context engineering for any repo

> **Note on language.** The full documentation of this kit is in **Spanish**
> (`README.md`, `GUIDE.md`, `OKF-SPEC.md`, `reference/`, `templates/`). This page is the
> English entry point: what the kit is, how to install it, and where to look next. Any
> coding agent can translate the rest on demand — and if you point one at `GUIDE.md`, it
> will follow the procedure regardless of the prose language.

**The problem.** You build a project by talking to AI. The reasoning lives in a chat that
expires. Next session — new machine, new tool, new model — you explain everything again.

**The kit.** A **guide + template library + tooling** that installs a durable context
system into *any* repo, using the **Open Knowledge Format (OKF)**: plain markdown with YAML
frontmatter, versioned in git. No external service, no SDK, no cloud, no `pip install`.
If you can `cat` a file you can read it; if you can `git clone`, you can take it with you.

Works for **code**, **data/analytics** and **wiki/knowledge-base** repos. What changes
between domains is the folder layout and the `type:` vocabulary — picked with a *profile*.

---

## Install

**As a Claude Code plugin** (the fast path):

```
/plugin marketplace add elgastipaa/okf-kit
/plugin install okf@okf-kit
```

That gives you `/okf-init` (bootstrap a clean repo) and `/okf-migrate` (consolidate a repo
that already has scattered docs, ADRs and `AGENTS.md` files). Then just say:

```
Set up OKF context in this repo.
```

**Without a plugin, or with any other AI** — clone it and run the installer, or point the
agent at `GUIDE.md`:

```bash
git clone https://github.com/elgastipaa/okf-kit
python3 okf-kit/scripts/okf_install.py /path/to/your-repo --profile codigo --name "Your Project"
```

The installer does everything mechanical (bundle skeleton, the `AGENTS.md` contract trimmed
to your install level, procedures, linter, CI, git hook) and then tells you what's left —
which is the part that needs judgment: **seeding the concepts**, i.e. the *why* your code
doesn't state. Let an agent do that part with you. Add `--minimal` to skip the future-work
layer, `--no-claude` to put the procedures in `docs/okf/` instead of `.claude/skills/`,
`--dry-run` to see the plan without writing. Already have OKF installed? `--upgrade`
replaces the kit's machinery without touching your bundle.

Everything the installer writes is Python-stdlib-only and reversible with `git checkout`.

---

## What you get: three layers

| Layer | Lives in | Answers | Read by |
|---|---|---|---|
| **Entrypoint** | `AGENTS.md` (repo root) | "Who am I, what rules do I follow, where is everything?" | Every agent, every session |
| **Knowledge** | `knowledge/` (the OKF bundle) | "What is this, and **why**?" | The agent, on demand, via `index.md` |
| **Procedures** | `.claude/skills/` — or vendor-neutral markdown any AI can follow | "**How** do I do task X?" | The agent, when the task matches |

All three are cross-vendor: `AGENTS.md` is the de-facto standard every tool reads, the
bundle is markdown, and the procedures are markdown that work as Claude Code skills *or*
get followed directly. See `reference/install-per-tool.md` for Cursor/Copilot/Gemini/etc.

There is a fourth layer that is a trap: **the tool's private memory** (e.g. `~/.claude/…`).
Useful, but not portable and not in the repo. The source of truth must be the bundle in git.

## Why this design holds up

- **Never lost** → it's in git: versioned, diffable, with a `log.md` history.
- **Any time** → it's state on disk, with no backend or session behind it.
- **Any AI** → markdown + `AGENTS.md` is as close to a cross-vendor standard as exists.
- **Anywhere** → `git clone` and the whole context follows you.
- **Without blowing the context window** → `index.md` files give progressive disclosure:
  the agent reads the map and descends only into what it needs.
- **Without losing direction** → the context covers the past (`decisions/`, log), the
  present (the concepts) **and the future**: current direction in `roadmap.md`, and each
  non-trivial change specced in `_changes/` before it's coded, then harvested into the
  bundle when it closes.

## Where to look next (Spanish)

| File | What for |
|---|---|
| **`GUIDE.md`** | The executable procedure an agent follows to install OKF in a repo. |
| **`OKF-SPEC.md`** | The format specification (normative rules), condensed and self-contained. |
| `reference/profiles.md` | Folder layout and `type:` per domain — the core of the universality. |
| `reference/verification.md` | How to **test** a bundle: conformance, quality, the cold-behavior test, and the compliance audit. |
| `reference/upgrading.md` | Moving a repo that already has OKF to the current kit revision. |
| `reference/install-per-tool.md` | Wiring OKF to any AI (Claude/Cursor/Copilot/Gemini…), no lock-in. |
| `reference/spec-driven-interop.md` | How OKF differs from spec-driven tools (OpenSpec, Spec Kit, Kiro) and how to run both. |
| `knowledge/` | The kit documenting **itself** in its own format — a live proof of what an install produces. |
| `DEVELOPING.md` | Working on the kit itself: the release gate. |

## License and credit

Apache-2.0 (see `LICENSE` and `NOTICE`).

OKF (Open Knowledge Format) is an open format published by Google Cloud in
[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(`okf/SPEC.md`), also Apache-2.0. There it targets data catalogs; here it is generalized to
**project context of any domain — code, data or wikis**, which the format explicitly allows
(`type` is not registered anywhere and the hierarchy is domain-independent).
