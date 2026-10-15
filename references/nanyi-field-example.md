# 南一路第二处实战成果 / Second-area field result

Final result accepted by the user on 2026-10-15: 15 + 20 ordinary LEADER/MTEXT callouts, planned from approved text and anchor identities without copying old bend/text positions. The original drawing was protected; old annotations were reversibly archived in the test copy, while fills, boundaries and symbols remained.

用户于2026-10-15认可最终成果：第一处15组、第二处20组。Agent先读取内框候选、识图分区、判断开口与顺序；工具核算实际字框及冲突，再经底座落图、读回和保存。灰色残留允许压盖，不为避让背景把引线拉长。

![Second area / 第二处](../examples/nanyi-20261015/area-2.png)

[Second-area native PDF / 第二处单页原生PDF](../examples/nanyi-20261015/callout-area-2-pm.pdf) — pm.ctb, A3, 1:500, model-space windows. The displayed image is a direct crop of the second-area final PDF; no extra title-block anonymization was performed, as requested. Published with the user's explicit authorization. Only the second-area result is displayed, as selected by the user; the first area is not published here. Source engineering DWG, CTB, fonts and private execution logs are not included.

## What the trial changed / 实战反馈

The initial geometric check passed, but PDF inspection revealed two labels entering hatch edges. The Agent moved them outward, checked neighboring groups, read back and saved, then reprinted. This is why explicit-geometry checks cannot replace visual interpretation. 灰色残留和有效工程填充必须区别对待；不能把本例具体坐标固化成通用排布规则。

## Evidence and limits / 证据与限制

- 35 native callout groups / 140 objects; final supplied-geometry review had no new-label overlap or leader/text conflict. This does not prove exhaustive background clearance.
- One native MTEXT was edited and restored; its four associated members matched their prior native properties, with anchor, association and horizontal tail retained. Objects remain manually editable; significant width changes still need coordinated tail updates.
- Queried ordinary base entities matched the initial inventory: 1067 polylines, 189 hatches, 14 circles, 562 lines, 1453 block references and 276 DBText objects. One of seven proxies changed its display extents after reopening; metadata was unchanged and no proxy was written. Internal proxy geometry is not certified by this comparison.
- Annotation writes/readback/save: Foundation MCP. Manual edit smoke test: native CAD UI. PDF: explicitly authorized AutoCAD COM PlotToFile on an independently opened read-only saved test copy. Printing is not claimed as Foundation MCP validation.
- Runtime native schemas must support the needed association offset. An older backend's formatted-text update validation issue was worked around after confirmed rollback; this is not a claim that all backend bugs were fixed.
- Current-case acceptance is not a promise of zero bugs on every drawing. Other scales and automatic text/dot resizing remain unverified/unimplemented.
