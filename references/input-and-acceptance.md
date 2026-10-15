# 输入与验收 v0.4

本文件描述标注工程输入和验收；CAD会话、工具发现与provider能力属于[MCP传输与能力契约](transport-contract.md)。v0.4新增Agent规划检查输入，与旧`pair_layout.py` schema分开；旧脚本输入和算法保持不变。

## 输入与样式来源

源DWG先只读盘点，记录绝对路径。写入使用获准工作副本，或用户明确要求续改的目标图，遵守当次授权。保存原标注文本、数量、锚点、实体handle/类型/图层、关联和源几何基线。旧标注处理限定到确认清单，不按颜色或整图层删除；没有安全删除能力时使用获准的可恢复归档。

文字与样式分开：文字/工程量来自本次已确认的数据和真实圈画范围；样式来自任务指定的代表性原生标注或经认可的小型样式 DWG。只复制样式所需的实体/定义，不把整张工程底图或样例中的旧厚度、面积、描述作为模板内容。记录字体、字高、宽度系数、对齐/附着、方向、颜色、引线对象类型、箭头/圆点有效大小、文字间隙、关联和图层。检查目标 CAD 能找到所需 SHX；同名但参数不同的样式应明确映射或隔离，不能只按样式名认定一致。

路施08参考实体已读出的本项目参数是 `_KCYD_DIM`、`gbenor.shx` + `gbcbig.shx`、文字高 1.5、底部间隙 0.375、圆点 0.375、`HyDim`、文字色 7、引线/圆点色 2。新图必须核原生有效对象覆盖值，不能只导入样式名；其他项目按各自认可的样式来源取值，不套用这些数值或路施08的工程量。未提供可核查的样式来源时，不宣称已经有可迁移模板。

## 会话发现与任务授权

调用前枚举当前对话/连接器实际暴露的 CAD MCP 工具并查看所选工具的完整 schema；不要照抄过去 provider 的参数或假定 `leader` 必然是普通 LEADER。查询目标文档身份：尽可能确认 PID、完整文档路径/名称、后端/连接；值为 unknown 时先查底座已有会话/文档能力，身份仍不明确就不写入。若所需操作存在真实 schema 缺口，本任务已明确授权时可在项目底座层补固定、受审查的适配组件：它只消费确认过的 PID/fullpath，限定对象类型和 handles，先检查旧状态并独立读回结果，源码留在项目代码中。不能用它绕过工具明确拒绝、安全设置或 unknown 身份栅栏，也不能把通用任意代码暴露给工程规则。当前任务未授权时报告精确缺口，不自动改走 COM。

本次路施08测试的任务授权是：允许复制源 DWG 为工作副本，并将底图灰化。该授权只适用于本次任务。实际执行前记录灰化涉及的图层/实体清单及原颜色；不得因此改动工程几何、标注样式或未在清单中的对象。验收报告分列：①允许清单内的颜色变化；②底图几何与保护对象的位置/形状未变。颜色不一致不得混入几何比较，也不得以几何通过代替颜色清单审查。用户给出的颜色/范围尚未落实到可识别图层或实体时，先只读筛选并列出对象清单；只将能确定属于底图的对象列入允许清单，无法识别的项目保留为未决，不扩展到未经授权的标注或几何对象。

## 比例与样式预留

本版实际行为为`preserve_native`：沿用当前认可原生尺寸，不因填写比例字段改变字高、圆点或间距。一般道路约1:400～1:500是本项目推测范围，未知时保留为范围，不擅自选一个精确比例。不同图幅/结构详图可各记比例，不设整张DWG唯一比例。

Agent的任务记录及检查输入可以附以下记录；此结构是后续统一换算的接口预留，不是现有底座绘图计划参数，也不能直接传给旧排布器：

```json

{

  "scale": {

    "denominator": null,

    "assumed_range": [400, 500],

    "source": "project_default",

    "sizing_mode": "preserve_native",

    "model_units_per_metre": 1,

    "style_source": "本次认可的原生样例及有效覆盖值",

    "paper_mm": {

      "text_height": null,

      "dot_diameter": null,

      "bottom_gap": null,

      "clearance": null

    }

  }

}

```

`denominator`为1:N的N，可靠来源可为图签、视口或用户指定；`source`记录依据。`paper_mm`未核定就用null，不从历史样例反推未确认的纸面标准。后续自动尺寸模式需同时明确纸面尺寸、比例和模型单位：`模型长度 = 纸面毫米 × N ÷ 1000 × 每米模型单位数`。因此同纸面大小在1:100下模型值较小、1:1000较大。圆点记录直径，底座若接收半径须转换；还需核对DIM scale/注释性等已有效的缩放，防止重复放大。当前没有自动尺寸模式，检查器明确拒绝`sizing_mode`不是`preserve_native`的输入。

## Agent明确坐标检查输入

`scripts/review_layout.py`只读JSON，适合Agent直接决定坐标后核查。一次检查一个共同图框坐标系中的相关组，邻区及固定旧组一起纳入；多幅按各自坐标和可见范围单独组织。`frame-local`的x平行内框水平边、y垂直，所有点及多边形都已完成同一变换，不能混入屏幕像素、WCS或纸空间坐标。原生WCS字框转局部时转换全部角点，不只变换min/max两点。

```json

{

  "schema": "callout-review-v1",

  "coordinate_space": "frame-local",

  "units": "metres",

  "clearance": 0.15,

  "inner_frame": {

    "polygon": [[-10,-20],[30,-20],[30,10],[-10,10]],

    "evidence": "visual_checked",

    "source_handles": []

  },

  "callouts": [{

    "id": "A",

    "leader": [[0,0],[3,-6],[11,-6]],

    "text_box": [[3,-5.5],[11,-5.5],[11,-4],[3,-4]],

    "target": {"kind":"point","point":[0,0]}

  }],

  "keepouts": []

}

```

- `leader`为三个A/B/C点，`text_box`为CAD真实字框的四个有序角点。示例为合成几何，不是可复用尺寸模板。`clearance`和可选`coordinate_tolerance`均为所声明模型单位，由任务决定；默认clearance为0，触框仍作为保守候选。输入的来源和格式化真实性由Agent另行核实。

- `inner_frame`是软优先范围，越出只警告，`evidence`及可选handles记录依据；缺少时报告内框容纳未检查。已知实际可见边界才提供`visible_polygon`，越出列冲突；缺少则明确未检查视口裁切。不要为消除警告伪造边界或把估算范围标成实际裁切线。

- `target`可为`point(point)`、`line(points)`或`polygon(points)`，可另给模型单位的`tolerance`。点域验证锁定位置，线/面域只验证输入几何内的位置；弧线/带洞目标若不能准确表达，改用原生验证，不拿粗略近似证明锚点合法。缺失目标则列未核实，不能推断身份正确。

- `keepouts`每项有`id`、`polygon`及可选`applies_to=text|leader|both`，默认只禁止文字，用于Agent确认为需保护的区域；不要自动将道路主体或灰化残留加入keepouts。确属有效的重要说明才按需要禁止文字及引线，不可用道路主体both禁区阻止引线正常引出。

- 程序不优化、不修改输入、不接CAD；报告字框重叠/穿字候选、引线交叉/接触、尾段水平/钝角、指定目标和边界。字框碰触也会保守报告。未提供背景、线宽/圆点、CAD关联/样式/重算和输入来源不在检查覆盖内；即使无冲突也不是工程/出图通过。

运行：`python scripts/review_layout.py plan.json report.json`。输出路径必须为不同的`.json`文件；Agent看报告决定小改还是重规划。`scale`可附在输入中记录，但此检查器不消费比例换算尺寸。

## 旧版`pair_layout.py`局部修补输入

以下字段只属于旧脚本；Agent规划模式不必构造该结构。使用旧模式前核对其平行同开口、严格bounds与预算限制，不能把软内框直接当旧工具的无条件硬约束。

JSON 根：`source`、`output`、`delete_handles`、`pages`。每页：`id`、`layout`、`frame(origin,angle)`、`bounds`、`rows`。模型测试单页 `layout=Model`，无 `viewport_handle`；仅在明确纸空间任务时配置布局视口。每行唯一 `id`、`text`、`anchor`、`direction`（单位向量）、初始 `length`、实际格式化 `width/height`、`gap`、`opening_sign`、`target(kind=polygon/line,points)`、`style`。坐标均为 frame 局部图形单位，不能混入 WCS。

`style` 字段：`text_style`、`height`、`text_color`、`text_layer`、`leader_style`、`leader_layer`、`arrow_size`、`leader_scale`、`text_gap_property`。`style.height` 是字高，`row.height` 是原生格式化后的实际高度。由当前后端读回原始边界/曲线 handle 与确认数量；数量还未重新核算时说明只保留原内容。

`delete_handles` 推荐 `{handle,kind,layer}`，`kind` 取原生 `ObjectName`。原脚本只支持其实现内列出的标注实体，字符串简写也仅支持原生 MTEXT/LEADER。多行旧说明合并成一行、加 ID 并逐项校对；不要漏掉非引线形式的说明。

道路页可加 `road` 配置，明确 `centerline` 与 `edges` 的 handles 或 layers，必要时 colors 过滤；`text_padding` 为道路边缘外文字余量。只有路施08示例用 centerline 层 AXIS 且颜色 2/3、edges 层 ROAD、余量 1；其他图不能照抄选择器。`road_side.py` 是旧的 COM 路径工具；若通过其他已验证能力获得道路约束，应把真实曲线证据及 `road_side={point,normal,min_text_distance}` 计划交给几何环节，并由原生读回复核同一约束。

`pair_layout.py` 单页至少有 `bounds`、`rows`；可选 `clearance=.15`、`step=5`、`max_extensions=5`、`max_rounds=3`、`check_leader_text=true`、`y_ref=0`、`obstacles(id,polygon)`。输出 `rounds`、`groups`、投影优先级、`attempts`、`checked_neighbor`、`chosen_length`、`translation`、`points/insert`、`extensions_used_by_id`、`remaining_conflicts` 和 `manual_ids`。多页隔离只表示几何能力，不能据此声称多布局原生通过。

## 执行与验收

工程执行入口为 MCP-first：从当前工具表及 schema 选取已证明支持的只读盘点、实体写入/移动、原生读回和保存能力。按照 [传输契约](transport-contract.md) 先确认文档/PID/后端，再用当前实际工具。读回真实文字格式化尺寸后由Agent明确坐标或调用局部几何工具；apply 后再次读回普通 LEADER 与关联 MTEXT 的类型、关联句柄、位置、样式有效值及显示点。若工具本身只会生成 MLeader，不将它记作普通 LEADER；本任务已授权的固定底座适配组件若能创建并独立读回所需对象，可按同一验收项核查。适配组件不能越过明确拒绝、安全设置或身份栅栏；无适用组件且未获授权时报告精确缺口。

- 内容与数量完整；文字单行、样式符合核实来源；普通 LEADER 与其 MTEXT 关联正确；黄色圆点实际显示；尾段平行图框、文字平齐、钝角与锚点语义正确；简单单侧目标同侧向外，弯道、跨中线大面和路口按Agent确认的合法出口核查。

- Agent规划验收范围依据、道路主体避让、分组/开口意图、跨框取舍及预览反馈；实际可见边界未核实就列限制。只有调用旧修补模式时，移动优先级、相邻停止、跨轮继承及25单位上限遵循[局部排布规则](placement-rules.md)。旧fixture为`scripts/fixtures/model08_v02.json`，旧回归不证明Agent新布局通过。

- 独立读回原生位置/尺寸再验证文字重叠；核对源几何基线、保留底图几何和获准颜色变更白名单。若保存/重开能力存在，应以独立重开结果佐证，不以工具成功响应替代读回。

- 目视检查模型并分别列出文字重叠、线穿字、线线冲突及背景候选。背景检查覆盖不足必须说明，不把扫描缺口当无冲突。

路施08 v0.2 历史记录：31 组、删除 132 个旧标注实体、创建 62 个新实体、保留 10968 个实体未变；二次验证新文字冲突为 0，N15/N16 线穿字已清。历史记录仍有 6 处新引线/文字间距冲突、5 处线线冲突及背景候选，N26 新增涵洞锚点语义待人工确认；换模型独立复测和多布局/打印尚未完成。这些不是 v0.3 新测试结果。

路施08 v0.3 本轮进度：通过项目底座中的固定 C# 样式组件，使用已发现的 bimwright `dwg_send_code` 对接能力补齐普通 LEADER 的字体、圆点、ActualWidth、Dimtad 与 AnnotationOffset 设置；R01 已完成原生读回和图面核验。该项目组件源码不属于 skill。其余 32 组及整图交叉/保护对象复核尚未最终验收，因此不得宣称 33 组或 v0.3 图面整体通过。
