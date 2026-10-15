# Compatibility / 兼容范围

Current source preview v0.6 adds Agent planning and the read-only reviewer; the legacy pairwise solver remains unchanged from v0.3. Solver checked on Windows/Python3.13.14/Shapely2.1.2; pinned dependency requires Python3.10+. Other Python/OS combinations are not independently tested here. Native workflow host/patch/client support must be established by actual tools, not this package name.

| Needed capability / 所需能力 | Foundation v1.0.0-rc.1 | Boundary / 边界 |
| --- | --- | --- |
| Identity/requests/object readback / 身份请求读回 | Limited implementation / 有限实现 | Use actual schema, full groups and unresolved-fence protection. |
| Basic ordinary Leader/MText/yellow dot / 基础标注组 | Local native evidence / 本地实机证据 | Not this Skill's full style. Core circle/fill dot differs from the historical arrow-block style; verify semantics and task approval, never claim automatic exact equivalence. |
| Fonts/style management and text/leader separate colors / 字体样式及文字引线分色 | Full adaptation absent / 完整适配未提供 | Needs approved native style source and reviewed operations. Skill does not add missing interfaces. |
| Actual formatted dimensions, attachment/end/gap / 真实尺寸附着端点间隙 | Partial properties/primitives / 部分覆盖 | Check actual returned field semantics and missing coverage, not inferred fidelity from bbox/width parameter. |
| Full placement algorithm / 完整排布 | This Skill / 本Skill | Applying proposals and readback still need compatible native tools. No complete Foundation-only certification. |
| Save/reopen / 保存重开 | Limited local workflow / 有限本地流程 | Solver alone does not save CAD. |
| Dimensions/MLeader/layout/plot/xref / 尺寸多重引线布局打印外参 | Not current profile / 当前未支持 | Not added by this Skill or comprehensive case display. |
| Other units/domains / 其他单位专业 | Core writes metres only / 底座写入限米 | Solver is unit-agnostic math, but native styles/rules require unvalidated adaptation. |

No blanket Foundation>=1.0 full-workflow guarantee. Components develop/release independently. Foundation owns native operations and execution governance; Skill owns style/placement rules. External tools do not automatically share journals, transactions or fences.

没有“底座≥1.0就完整兼容”的承诺。组件独立开发发布；通用原生操作／执行治理归底座，样式／排布归Skill。外部工具不自动共享账本、事务或栅栏。

Optional manual BZYD editions: Chinese has historical AutoCAD2026 native evidence; English UI only has static expression/encoding equivalence; AutoCAD2022 is unverified for both. It does not depend on the 2026 Foundation bridge. See [manual guide](../tools/autolisp/README.md) and [component/version discussion](STRUCTURE-AND-VERSIONS.md).

Current field evidence / 当前实战：AutoCAD2026两处35组经支持关联偏移的底座版本完成标注、读回与保存；原生人工编辑恢复通过。只展示第二处成果，见[案例](../references/nanyi-field-example.md)。运行时核对schema，不因同名旧后端推定兼容。PDF经用户授权COM打印，非底座打印能力。
