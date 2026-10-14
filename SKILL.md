---
name: cad-callout-pair-layout
description: Style CAD area, length and descriptive callouts with ordinary LEADER, associated MTEXT and a yellow dot; apply confirmed side/opening constraints and bounded pairwise placement. Use for annotation and avoidance, not engineering scope, quantities, frames or plotting.
---

# CAD Callout Pair Layout

Public preview v0.3.0-rc.1 preserves existing v0.3 MCP-first rules and an unchanged pure-geometry solver. [完整中文规则](SKILL.zh-CN.md). Read [transport](references/transport-contract.md) before CAD work, [input and acceptance](references/input-and-acceptance.md) for data, and [placement rules](references/placement-rules.md) for layout.

## Components and native execution

Foundation alone suffices for supported basic CAD. Add this Skill for this project's callout style/placement; distress/demolition additionally needs cad-distress-annotation. Ordinary callouts do not require that Skill. See [installation](docs/INSTALL.md) for actual availability. Foundation v1 provides partial primitives, not complete certified style/layout integration.

Discover actual tool schemas and uniquely identify process/session, drawing path and backend. Unknown identity prevents writes. Ordinary three-vertex LEADER with associated MTEXT is required; MLeader is not a substitute. A task-authorized fixed adapter belongs to the project/backend layer, must consume confirmed PID/fullpath, limit operations/types/handles, check old state and read back independently. This Skill carries no arbitrary native execution code. Never bypass a tool refusal/security setting or unknown-write fence. Query the original request after uncertain submission; do not switch provider or replay under a new ID.

## One callout

Read approved content, quantity, anchor and protected objects first. Treat A anchor, B bend, C tail and text as one unit; placement must not change engineering content or base geometry.

- One visual text line with spaces; preserve approved descriptive sentences. Obtain width/height from actual CAD formatting, not character counts.
- Ordinary LEADER plus MTEXT and an actually yellow anchor dot. Verify the dot's rendering source; leader color alone is insufficient.
- B→C parallel to approved frame horizontal; text aligned with tail and approved bottom gap. Angle at B strictly obtuse; leader may not cross its own text.
- Start short. Determine outward road side from the anchor and native centerline/edge constraints, not the old label position. Keep text outside the confirmed road annotation band.
- Frame-local coordinates determine left/right move priority; road centerline only determines side/outward constraints.

A historical metre-based reference uses _KCYD_DIM, gbenor.shx + gbcbig.shx, height 1.5, gap/arrow-size setting 0.375, HyDim, text ACI7 and leader/dot ACI2. These are example parameters, not universal defaults. Arrow-size is not automatically rendered dot diameter. Read an approved native sample for the task; do not transfer its engineering quantities. No fonts are distributed. Missing style/backend capability must be reported rather than silently approximated.

## Finite placement

Use at most three rounds, inheriting actual positions. Stage 1 uses fixed new-text conflict groups and common-y projection of parallel rays, not raw B.x. For right openings keep the rightmost unit, then its immediate left neighbor; mirror left openings. Stop as soon as a neighbor pair clears. Stage 2 processes actual leader/other-text pairs without merging all leader conflicts; candidates must clear the pair without adding new new-text overlap.

Extend 5 drawing units along the original anchor ray without changing angle. Each unit has five accepted extensions/25 total units across all rounds; never reset the budget. On failure try whole-unit horizontal offsets -2,+2,-4,+4,-6,+6 including anchor, which must remain in its confirmed target. Tail-only movement is not whole-unit translation. Rebuild groups next round; stop on clear/no-change/round limit, retaining last valid geometry and manual IDs. Mixed openings, nonparallel rays and tied projections are manual, not arbitrarily ordered.

The solver computes proposals only. Configurable values are not a hard enforcement of the Skill's three-round/five-extension policy; check input budgets. Reuse the algorithm rather than rewriting it. Native measurements, apply/readback and persistence come from verified tools. Other units/domains need adaptation and are unvalidated.

## Acceptance and continuation

Old groups become fixed obstacles; new groups retain their own budgets. Approved tiny-label hiding hides text and associated leader together while preserving boundary/fill; thresholds and quantities come from the engineering task.

Verify native objects, actual dimensions, associations, styles, positions and view appearance—not only JSON. Report text/text, leader/text, leader/leader and background candidates separately. Zero new-text overlap is not collision-free whole-drawing proof. Separate permitted colors from protected geometry. Save/reopen as required; do not expand to plotting/layout unless requested.

[Validation](docs/VALIDATION.md) separates generic solver tests from historical native work. Private fixtures and legacy COM/background helpers are omitted. This Skill supplies no CAD writer, MCP server or automatic installer.

Optional human tool: [BZYD](tools/autolisp/README.md). It moves an existing callout with a fixed anchor and can allow right angles; it does not automatically satisfy the Skill's strict-obtuse style, road-side or collision acceptance. It is not an Agent backend adapter or a way around unknown-write fences.
