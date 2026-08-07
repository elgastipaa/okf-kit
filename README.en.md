# okf-kit — so the AI stops forgetting your project

> **Note on language.** The kit's full documentation is in **Spanish** (`GUIDE.md`,
> `OKF-SPEC.md`, `reference/`, `templates/`). This page is the English entry point and
> covers everything you need to decide and to install. Point any coding agent at `GUIDE.md`
> and it will follow the procedure regardless of the prose language.

**The problem.** You've been building with an AI for months. Every session starts by
explaining the project again; the decisions you made together — why that database, why that
weird hack must not be touched — live in chats that are long gone. And the day the agent
breaks something, there's nowhere to look up why it was that way.

**What this kit does.** It leaves the context the AI needs in your repo, in markdown and
git: the **why** behind decisions (`decisions/`), a map of the present you can walk in
seconds, and the work in flight. No apps, no services, no `pip install`. Any AI reads it, on
any machine, without you explaining it.

**What you won't find elsewhere: the kit measures itself.** It ships a harness
([`templates/eval/`](templates/eval/)) that runs real questions against your repo, with and
without the context layer, and tells you in turns and tokens whether it's actually helping.
This matters: the [largest study on context files](https://arxiv.org/abs/2602.11988)
(SRI Lab, ETH Zürich, 2026) measured that in general they **don't improve accuracy and cost
>20% more** — and that the only thing that did pay off (+4%) is what a human knows and the
code cannot say: decisions, constraints you can't see by reading, non-obvious test
configuration. That's exactly what this kit helps you write, and the harness is there so you
don't have to take my word for it.

**We publish the measurement even when it's bad — and it mostly is.** Installing this kit does
**not** make your AI faster at figuring out how your code works; plain grepping does just as
well. The best number this kit used to quote turned out to be the merit of the **human** who
wrote that layer, not of the format. What it does do, measured, is **preserve the whys** that
today live in deleted chats and **produce the questions only you can answer**, instead of
inventing a plausible answer for them. All of it — including the bugs we found in our own
instrument — is in **[`MEASUREMENT.md`](MEASUREMENT.md)**. A kit that only publishes its wins
isn't measuring — it's advertising.

> **Self-contained**: markdown + git, no service, SDK or cloud. If you can `cat` a file you
> can read it; if you can `git clone`, you can take it with you.

**No external apps.** No Obsidian, Notion, MkDocs or graph viewer: it's markdown + git. A
human reads it on GitHub; an agent reads it as files. **There's nothing to adopt in order to
*use* the bundle.** The kit also ships optional tooling so the context doesn't rot on its own
— a linter, a drift ranker, a fresh-context reviewer — but that's plumbing: it's not the
reason this works, and it works without them.

---

## Install

**As a Claude Code plugin** (the fast path):

```
/plugin marketplace add elgastipaa/okf-kit
/plugin install okf@okf-kit
```

That gives you two paths, and **the one you probably need is the second**:

- **`/okf:okf-migrate`** — *"my `AGENTS.md` is a mess"*, *"I have docs everywhere and I don't
  know which ones are still true"*. **This is the normal case**: a repo that's been built
  with an AI and accumulated scattered context. It consolidates what you already have —
  separating what's still true from what the code left behind — instead of piling one more
  layer on top.
- **`/okf:okf-init`** — a repo with **no** prior context. The less common case.

Plugin commands carry the plugin's prefix. You don't have to type them, though: describing
the symptom in your own words is enough to trigger the right skill. Then just say:

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

Everything the installer writes is Python-stdlib-only, and it never overwrites your own work:
it aborts on a hand-written `AGENTS.md`/`CLAUDE.md` (that repo is what `okf-migrate` is for)
and never touches someone else's `pre-commit`.

To undo it: what it writes is **new and untracked**, so `git checkout` won't remove it — use
`git clean -nd` to preview and `git clean -fd` to do it — and the hook, which git doesn't
version, goes with `rm .git/hooks/pre-commit`. Run the `-n` first: `git clean` also removes
other untracked files of yours.

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

- **Never lost** → it's in git: versioned, diffable, with the history git already gives you.
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
| `OKF-SPEC.md` | The format spec, for anyone implementing it or writing tooling. **As a user you don't need it**: what you get is a folder of markdown with frontmatter. |
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
