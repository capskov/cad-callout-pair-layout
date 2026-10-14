# Evidence and limits / 验证与限制

## Public package (existing candidate evidence reused)

The algorithm is byte-identical to the existing private v0.3 solver. Generic exported regressions are retained; the real 31-row fixture and two actual-project/measurement tests are excluded, not replaced and relabeled as synthetic proof. Current packaging checks cover these generic tests, the synthetic CLI example, archive extraction, naming/metadata and links. No new CAD instance, full native acceptance or case annotation rerun is performed.

原算法逐字节保留。仅导出通用回归，真实31行夹具与两个实际工程／测量测试不导出，不冒称以合成数据重新验收。当前包装检查不构成新增CAD实机证明。

## Historical native evidence

The later reviewed record dated 2026-10-03 reports 33 ordinary LEADER/MTEXT callouts checked after save/close/reopen: content, styles, associations, position/elevation, obtuse angle, tail width and outward-road constraints. Internal new-callout text/leader conflicts were zero in that record. Older references saying one group was complete are stale and reconciled here. This is historical task evidence, not a new public-version test.

Actual historical roles: UC4N/COM path for some geometry/layers/save; BEIM compatibility backend for bulk geometry and ordinary LEADER/MTEXT creation; Bimwright for query/color/property integration; project-specific fixed adapters for exact styles; earlier Foundation0.7 for bound independent readback. These differ from the current Foundation v1 profile. No historical helpers or arbitrary code are bundled.

33组标注的部分验收不等于整图最终工程验收：综合底图指纹不同，已核字段未覆盖所有几何；背景文字候选覆盖不完整；工程表不能证明所有范围与总量闭合；外参／出图未验。原DWG、实坐标、句柄和私有证据日志不导出。

The later anonymous demolition display in Foundation's repository used project-specific Python/AutoCAD2026 COM and Shapely plans with this solver. It is a different comprehensive visual workflow, not this 33-group test or Foundation-only certification.

Observed candidate results (2026-10-14): 19/19 exported generic solver tests passed; official Skill frontmatter validator and UI metadata checks passed. The unchanged algorithm hash was checked against the original. Package example/extraction and byte integrity are recorded in the review manifest; these are not new native CAD acceptance.

本轮候选：19/19通用几何回归通过，官方Skill结构校验／UI元数据检查通过，原算法哈希一致。包装示例与解压完整性单独记录，不替代CAD实机证据。
