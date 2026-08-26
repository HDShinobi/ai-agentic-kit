# Contributing to AI Agentic Kit

Thanks for your interest in improving **AI Agentic Kit** — a Claude Code plugin
marketplace of à-la-carte domain plugins (prefix `aak-`). Contributions of every
size are welcome: new skills, bug fixes, documentation, and especially corpus and
example data for the language plugins.

- Repo: https://github.com/HDShinobi/ai-agentic-kit
- License: MIT (see `LICENSE`). Vendored plugins keep their upstream license —
  see the root `NOTICE` file. By contributing you agree your contribution is
  licensed under the same terms as the component it touches.

## How to contribute

1. **Open an issue first** for anything non-trivial, so we can agree on scope.
2. Fork, branch off `main`, and keep changes focused on one plugin where possible.
3. Follow the conventions in `CLAUDE.md` and each plugin's structure.
4. **Validate before opening a PR** — every changed plugin and the marketplace
   manifest must pass:
   ```bash
   claude plugin validate .                 # marketplace
   claude plugin validate plugins/<name>    # each changed plugin
   ```
5. Use conventional commit messages (e.g. `feat(aak-marketing): …`,
   `fix(aak-vietnamese): …`, `docs(readme): …`).

## Contributing example / corpus pairs (language plugins)

Several `aak-vietnamese` skills ship curated **source → improved** copy pairs used
as few-shot references (see each skill's `references/examples.md`). To add pairs:

1. Open a PR editing the relevant `references/examples.md`, keeping the existing
   two-column format and updating the pair count in the heading.
2. Every added pair must pass the advertising-law linter:
   ```bash
   python3 plugins/aak-vietnamese/shared/scripts/validate_copy.py <file>
   ```
   A pair that would ship non-compliant copy is worse than no pair at all —
   fix or drop it rather than weaken the check.
3. Keep text in NFC-normalized Vietnamese (vi-VN) and preserve register/tone.

## Vendored plugins

`aak-ads` and `aak-vietnamese` are **vendored verbatim** from upstream projects.
Substantive changes to their skill logic should generally go upstream first; only
mechanical wiring (frontmatter, command namespacing, link targets) is adjusted
here, and any such change is recorded in `NOTICE`.

## Questions

Open a GitHub issue at https://github.com/HDShinobi/ai-agentic-kit/issues.
