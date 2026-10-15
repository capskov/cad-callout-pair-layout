---
name: cad-callout-pair-layout
description: Plan and style CAD callouts with ordinary LEADER, associated single-line MTEXT and a yellow dot. The Agent reads the inner frame, chooses regions and ordering, then uses bounded geometry checks and verified native tools. Use for new or adjusted callouts, not engineering quantities, frames or plotting.
---

# CAD Callout Style and Layout

Source preview v0.6 uses Agent-led planning. [完整中文规则](SKILL.zh-CN.md), [planning guide](references/agent-planning.md), [input/acceptance](references/input-and-acceptance.md), [transport contract](references/transport-contract.md). The unchanged v0.3 pairwise solver is an optional local repair tool; its fixed angle/extension limits do not constrain Agent planning. An unresolved ID returns to the Agent for judgment, not necessarily to the user.

1. **Read the usable inner frame first.** Query native extents of candidate frames, including proxies/blocks, and identify the correct continuous inner rectangle visually. A proxy bounding box need not equal an inner frame. If unavailable, derive a representative viewport or estimate from available evidence; record native, visual, viewport-derived or estimated evidence and units. About 1:400–1:500 and 175 metres per road sheet are project hints, not fixed dimensions. Prefer the inner frame; occasional overflow is a lower-priority fallback, while actual clipping must be resolved.
2. **Let the Agent choose regions and order.** Inspect the road, anchors, dense content and usable blank spaces before writing labels. Prefer readable areas outside the road. Confirmed gray residual background has very low avoidance weight and can be overlaid; do not lengthen leaders simply to avoid it. Protect current annotations and effective engineering information. Internal readable spaces may be used when necessary. Same-opening anchor order is an initial preference, not a crossing-free theorem on curved roads.
3. **Plan before placement.** The Agent may specify A/B/C directly, or ask a small tool to fit within selected regions/order/openings. Use native formatted text bounds, including superscripts, rather than character counts or MTEXT wrapping width. Keep point anchors fixed; other anchors must remain on their confirmed target. Do not seed a whole deliverable with arbitrary positions.
4. **Check, apply, read back and inspect.** scripts/review_layout.py checks explicit plans, supplied keepouts, soft frame limits and known clipping. It does not read CAD, choose regions, classify gray content or move labels. Apply via verified native tools and independently read associations, actual dimensions and positions. Fix isolated issues locally; widespread or recurring overlap requires revisiting regions/order. Gray-background permission does not make dense road hatch a preferred text area. Inspect complete labels against hatch edges, effective lines and viewport clipping. When printing is requested, inspect the actual requested-CTB PDF.

## Native callout and editing

Use ordinary three-vertex LEADER associated with MTEXT and an actually yellow anchor dot, not MLeader. Preserve approved content, quantities and base geometry. B–C follows frame horizontal, with approved text gap, a strictly obtuse B angle and no leader crossing its own text. Read actual task-approved style overrides; historical metre-based dimensions are examples, not universal defaults. Automatic scale selection/resizing remains unimplemented.

Verify native AnnotationOffset, Dimtad and regeneration, not just stored vertices. See [stable association/tail](references/transport-contract.md#关联尾端稳定性). Keep native objects editable and new layers unlocked; do not explode or rasterize them. On an initial field trial, edit one MTEXT in the native editor and restore it, then read back anchor/association/horizontal nonzero tail. Significant text-width changes need coordinated tail maintenance; arbitrary edits are not promised automatic equal-width tails.

## Execution and evidence

Discover actual runtime schemas and uniquely bind process/full path/backend before writes. Unknown writes are queried by their original request, never replayed under new IDs. Report native capability gaps; task-authorized alternatives do not bypass refusals or fences. This Skill ships no CAD writer, arbitrary-code adapter, fonts or engineering DWG. Foundation supplies reusable operations; the Agent/Skill supplies engineering presentation judgment.

The [accepted 35-callout field example](references/nanyi-field-example.md) displays the second-area PDF crop and its pm.ctb PDF. Annotation writes/readback/save used Foundation MCP; manual editing used CAD UI; explicitly authorized COM performed plotting. It is a local-case validation, not all-drawing or all-version certification. See [evidence](docs/VALIDATION.md). The optional [BZYD manual utility](tools/autolisp/README.md) remains separate and is not an Agent execution backend.
