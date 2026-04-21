# Notepad
<!-- Auto-managed by OMC. Manual edits preserved in MANUAL section. -->

## Priority Context
<!-- ALWAYS loaded. Keep under 500 chars. Critical discoveries only. -->
claude-adhd-harness: portable plugin catching drift in the 45sec between noticing and redirecting. Tap, not lecture. Patterns #1,4,6,8 aggressive; #2,5 cautious; #9,10 session-level. See memory/user_work_patterns.md.

Open followups (each a fresh session):
1. Semantic-match for nudge hook — word-overlap false-positives on-topic prompts (MIN_PROMPT_WORDS now 4).
2. Auto-anchor from first session prompt, claude.ai-title style — reduce need for manual /anchor.

## Working Memory
<!-- Session notes. Auto-pruned after 7 days. -->
### 2026-04-21 05:15
### 2026-04-21 05:27
### 2026-04-21 05:28
## Cross-repo pattern (after reading big-learns + basilect-engine + site-ops)

User has a CONSISTENT self-scaffolding pattern across all repos. Harness should parse this structure, not invent a new one.

**Universal sections (names vary, roles are the same):**
- Current work: `## Pipeline` | `## Current Focus` | `## Outstanding Items` | `## Phase N (next)`
- Explicit not-now: `## Deferred` | `## Backlog` | `## Known limitations` | subsections labeled "(low-priority)"
- Rules: `## Working Principles`

Site-ops even has typed priority in headings: "(low-priority backlog)", "(stabilized — backlog)", "(active — Phase 1 next)". Parser can extract priority annotations.

**Parser targets (first pass):**
1. `CLAUDE.md` in cwd or any ancestor
2. `todo.md`, `plans.md`, `maps/*.md` for big-learns-shaped repos
3. `.claude/plans/*.md` for phased-plan repos (site-ops)

**NEW detector: "principle-violation" (catches Claude-side drift too)**
- Parse ## Working Principles entries as rules
- PreToolUse hook: if next tool call appears to violate a rule, inject warning
- Example: site-ops "Don't read files speculatively" → flag speculative reads
- Two-sided harness: catches user drift AND claude drift, both compound

**Detector priority order (final for MVP):**
1. Deferred-item activation (user-drift, zero-FP, reads existing section)
2. Principle-violation (claude-drift, reads existing ## Working Principles)
3. #4 stacked-questions (regex)
4. #6 pre-execution reconsideration (regex + turn history)
5. #8 tool-eval loops (regex + tool dictionary)
6. #1 settings detour (topic divergence + customization vocab)

**Architectural implication:** the harness is 80% "parse existing CLAUDE.md conventions and surface them at the right hook" and 20% "pattern-specific linguistic detectors." Much smaller than initially scoped.


## 2026-04-21 05:15
### 2026-04-21 05:27
## MVP refinement — after reading user's existing projects

**Key insight:** user has already self-built most of the anchor infrastructure. big-learns has maps/logs/todo/plans. basilect-engine/CLAUDE.md has Pipeline/Deferred/Known-limitations sections. The harness should READ these, not duplicate them.

**Revised architecture:**

1. **Auto-anchor from CWD (SessionStart hook)** — walk up tree, parse CLAUDE.md for `## Pipeline` / `## Deferred` / `## Known limitations`; parse big-learns-shaped repos for maps/todo/plans. These sections ARE the anchor. No slash command needed for the common case.

2. **Mode detection from repo signal:**
   - big-learns/ or maps/ in cwd → learning mode (high drift tolerance, anchor = todo.md + maps/ topics)
   - CLAUDE.md with ## Pipeline → coding mode (low drift tolerance, anchor = pipeline steps)
   - neither → generic mode (needs manual /anchor)

3. **NEW high-leverage detector: "deferred-item activation"** — in a repo with `## Deferred`, if current prompt matches a deferred-item string, fire nudge. User literally wrote "not now" for these items. Near-zero false positive rate. Catches scope creep (#5) without ambiguity.

4. **Manual /anchor stays as override** for conceptual sessions not tied to a repo.

**Storage simplified:**
- Repo-scoped: read existing files in-place (no new state file)
- Un-anchored conceptual sessions: ~/.claude/anchors/<session-id>.json

**Detector priority order (revised):**
1. Deferred-item activation (near-zero FP, high signal) ← NEW, do first
2. #4 stacked-questions (regex, trivial)
3. #6 pre-execution reconsideration (regex + turn history)
4. #8 tool-eval loops (regex + tool dictionary)
5. #1 settings detour (topic divergence from anchor + customization vocab)

**Still deliberately excluded:** #2 drill-down, #9 magnetized compass direct detection, #10 completion gap (session-level, different mechanism).


## 2026-04-21 05:15
## MVP shape (working draft)

**Three pieces:**

1. **Anchor mechanism** — slash command or session-start prompt that captures "what are we actually trying to do here" into a file. Without an anchor, drift detection has nothing to drift *from*.

2. **UserPromptSubmit hook (detector)** — runs every turn. Reads anchor, applies pattern-specific linguistic detectors, injects a system-reminder nudge when thresholds trip. Deterministic, stateful, external to the model.

3. **Skill (policy)** — defines how Claude responds when the hook fires. Tone, format, branch-vs-refocus decision, how to phrase the "here's what you said you wanted" redirect.

**Why this split:** hooks run deterministically (fixes the magnetized-compass problem — external signal user can't produce internally). Skill defines *how* to react. Anchor gives the comparison target.

**Detectors per pattern (first pass):**
- #4 stacked questions: regex for "also"/"and also"/"another thing" + question-mark count > 1 → low-cost win
- #6 pre-execution reconsideration: "wait before" / "actually hold on" within N turns of "let's do X" → needs turn history
- #1 settings detour: keyword overlap against anchor drops below threshold AND prompt matches customization vocab ("X vs Y", "lighter", "what should I play with") → needs semantic-ish comparison
- #8 tool-eval loops: "difference between X and Y" / "which should I use" on tool-nouns → regex + tool dictionary

**Deliberately NOT in MVP:**
- Drill-down (#2) detection — too high false-positive rate, user values drilling
- Completion gap (#10) — session-level, different mechanism
- Magnetized compass (#9) — not directly detectable, only via proxies already covered by other patterns

**Open design questions:**
- Anchor granularity: one per session, or a stack (main goal + sub-goals)?
- Nudge frequency cap: max N nudges per session? Exponential backoff?
- Session-type modes: "learning/conceptual" vs "coding/execution" — different anchors, different detector weights?
- Storage: native CC memory vs a local file in the repo vs OMC notepad?


## MANUAL
<!-- User content. Never auto-pruned. -->

