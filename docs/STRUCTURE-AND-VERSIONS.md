# Component structure and host support / 组件结构与版本

## First public-preview structure

Keep cad-callout-pair-layout and its Skill identifier. Scope: ordinary LEADER/MTEXT callout style and pairwise layout. Use a reader-facing title CAD Callout Style and Layout; Chinese 引线标注样式与排布. Renaming the repository/Skill now would break installed identifiers and future cross-links without adding a capability.

```text
SKILL.md / SKILL.zh-CN.md        Agent rules
references/                     Detailed input/placement/backend constraints
scripts/pair_layout.py          Pure geometry
tools/autolisp/                  Optional BZYD human adjustment, EN/ZH ANSI
docs/                           Installation, compatibility and evidence
```

Only reviewed maintained resources are included in the public preview. Private CAD/real fixtures/logs/old COM helpers stay outside. No extra framework or command wrapper is created for publication.

Future native dimensions should use a separate candidate Skill name such as cad-dimension-annotation, with its own dimension types/style/measurement/acceptance rules, sharing supported native operations from Foundation. This future component is not implemented or published. If several Skills later form a coherent workflow, a separate navigation/collection page can link them; do not rename this Skill into a claimed universal annotation engine.

## Host support by layer

| Layer | AutoCAD2026 | AutoCAD2022 | Release wording |
| --- | --- | --- | --- |
| Pair geometry | Offline Python/Shapely tests; no CAD needed | Same mathematical proposals, no native guarantee | Solver is independent of CAD host, not proof of CAD2022 workflow support. |
| Original Chinese BZYD Lisp | Historical 11 angle/undo/persistence checks | Not tested | Tested on specified 2026 examples; 2022 unverified. |
| English BZYD prompts | Encoding/expression equivalence checked | Not tested | Translation prepared, no new native acceptance. |
| Full Skill native workflow | Historical multi-backend evidence, limited current Foundation coverage | Legacy experiments exist but public route uncertified | Inspect actual tools and limits; not universal 2022/2026 support. |
| Current Foundation bridge | Limited 2026/.NET8 profile | No certified current Foundation release | Retained net48 project shell is not a working public 2022 integration. |

Recommend one BZYD code line with EN/ZH message editions and a host compatibility table. Before claiming 2022 support, perform only focused isolated checks: load, ordinary move, angle flip, UCS/association, undo and save/reopen. Do not branch a separate 2022-old repository merely because the code uses older APIs. A failure requiring version-specific behavior can later justify a narrow compatibility adapter.

Porting Foundation is a separate development item: current 2026 net8 journal/governed route must be evaluated against the retained 2022 net48 shell, build references and execution/identity/readback contracts. This is not achieved by changing a year in README or merging all legacy COM scripts. No 2022 port or new native integration is performed by this packaging revision.

建议：引线Skill名称保持，不为未来尺寸线先扩名。人工BZYD中英文同一逻辑，2022先标未验证；通过针对性隔离检查再补同一仓库兼容表。底座2022适配另立工作范围，不混入这次发布整理。
