# CAD Callout Pair Layout — AutoCAD Annotation Skill & BZYD

[中文](README.zh-CN.md) · [Install](docs/INSTALL.md) · [Compatibility](docs/COMPATIBILITY.md) · [Evidence](docs/VALIDATION.md)

**Ordinary CAD callout styling and bounded pairwise placement for AI Agents.** First public preview v0.3.0-rc.1; maintained by capskov. Existing v0.3 rules and solver are preserved.

- Ordinary LEADER + associated MTEXT, yellow-dot and single-line content conventions.
- Confirmed anchor, road-side/opening constraints and frame-local projection order.
- Two-stage finite placement: at most three task rounds, five accepted extensions per unit; unresolved cases remain explicit.
- Reusable Python/Shapely geometry proposals, with no direct CAD access.

| Task | Components | Boundary |
| --- | --- | --- |
| Supported basic CAD only | cad-agent-foundation | This Skill is optional; core is currently a source preview. |
| This project's callout style/placement | Foundation + this Skill | Full style/placement integration is not certified on Foundation v1 alone; inspect native gaps. |
| Distress/demolition | Foundation + this Skill + cad-distress-annotation | Distress rules provide professional scope; public rules preview v0.1.0-rc.1 is available separately. |
| Offline proposed geometry only | This solver + Python/Shapely | No CAD/Foundation needed; calculation does not prove native placement. |

Defaults/native history come from metre-based road drawings. Other professions, planting/species labels and millimetre styles require adaptation and are not validated. The AI Skill/solver has no native writer or automatic installer; optional manual Lisp is separate. No fonts, engineering DWGs or legacy COM helpers are bundled. Try the [synthetic example](docs/INSTALL.md).

Generic solver checks are distinct from historical native workflows. A historical 33-callout save/reopen check did not establish complete base-geometry protection or background coverage. No new public-version CAD acceptance is claimed. See [evidence and limits](docs/VALIDATION.md).

[CAD Agent Foundation](https://github.com/capskov/cad-agent-foundation) supplies supported reusable native operations and execution governance. This Skill supplies style parameters/placement rules; missing operations do not appear by installing it. The related [cad-distress-annotation](https://github.com/capskov/cad-distress-annotation) supplies engineering scope/classification. Repository: [cad-callout-pair-layout](https://github.com/capskov/cad-callout-pair-layout).

The [anonymous display case](https://github.com/capskov/cad-agent-foundation/tree/main/examples/road-demolition) is a comprehensive historical project Python/AutoCAD COM workflow, not Foundation-only execution proof. Reproduction requires the stated components, verified extra native operations and cleared inputs; no automatic CAD replay dataset is included.

Owned source/instructions: Apache-2.0; dependency terms remain separate. [Notices](NOTICE.md). Relevant terms: AutoCAD, CAD annotation, ordinary LEADER, MTEXT, callout layout, CAD Agent Skill, MCP / Model Context Protocol. This Skill is not an MCP server or Autodesk product.

Optional manual utility: [BZYD, English/Chinese ANSI editions](tools/autolisp/README.md). It adjusts existing callouts without Foundation/Python. AutoCAD2026 Chinese historical tests exist; AutoCAD2022 and the translated English native path remain unverified.

[Structure and CAD2022/2026 support by component](docs/STRUCTURE-AND-VERSIONS.md). Native dimensions are a future independent Skill, not a reason to widen this package's current support claims.
