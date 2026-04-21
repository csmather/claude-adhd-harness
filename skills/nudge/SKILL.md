---
name: nudge
description: Policy for responding when the claude-adhd-harness drift-notice hook injects a nudge tag.
---

# Drift nudge policy

When you see an `<adhd-harness-nudge>` tag in your context, surface the anchor to the user in ONE short sentence before answering their actual prompt.

## Rules

- One sentence. Neutral tone. No "I notice..." / "It looks like..." / "Just checking..." — state the anchor and the choice.
- Offer three options: **branch** (save as a follow-up, return to anchor), **refocus** (drop the tangent, return to anchor), **update** (anchor is stale — replace it).
- Wait for the user's pick before addressing the drifted prompt.
- Do not moralize, do not explain the drift pattern, do not apologize. The user already knows.
- After the user responds, act on their choice. Don't re-nudge on the next turn.

## Phrasing template

> Anchor check: "{anchor_text}" (set {age}). Branch, refocus, or update?

That's it. Nothing else above or below.
