# CAD Callout Pair Layout — 引线标注 Skill

[English](README.md) · [安装](docs/INSTALL.zh-CN.md) · [兼容范围](docs/COMPATIBILITY.md) · [验证与限制](docs/VALIDATION.md)

**为AI Agent提供普通CAD引线标注样式与有限两两排布规则。** 首个公开预览 v0.3.0-rc.1，维护者capskov；沿用v0.3规则和原算法。

- 普通LEADER＋关联MTEXT、黄色圆点、单行内容约定。
- 锚点、道路侧／开口约束及图框局部投影排序。
- 两阶段有限排布，任务最多3轮、每单元总计5次有效延长；剩余冲突列人工。
- Python／Shapely纯几何建议，不直接打开或修改CAD。

| 任务 | 所需组件 | 限制 |
| --- | --- | --- |
| 已支持的基础CAD操作 | 仅底座 | 本Skill按需安装；底座当前为源码预览。 |
| 本项目引线样式与排布 | 底座＋本Skill | 完整样式／排布未由底座首版单独认证，先查原生工具缺项。 |
| 病害／拆除流程 | 底座＋本Skill＋病害拆除Skill | 专业范围由病害技能提供；独立公开规则预览 v0.1.0-rc.1。 |
| 仅计算离线几何建议 | 排布器＋Python／Shapely | 不需CAD或底座；计算成功不等于原生落图通过。 |

默认及实战证据来自米制道路图；其他专业、园林品种和毫米样式需适配，尚未验证。AI Skill／排布器不带原生写入器或自动安装，可选人工Lisp单独列明。不打包字体、工程DWG或旧COM辅助脚本。可先试[纯合成示例](docs/INSTALL.zh-CN.md)。

本次通用几何检查与历史CAD流程分开。历史33组标注保存重开读回通过，不证明整图保护和完整背景覆盖；公开包没有新增CAD实机认证。见[验证说明](docs/VALIDATION.md)。

[底座](https://github.com/capskov/cad-agent-foundation)负责受支持原生操作和执行治理，本Skill负责样式参数／排布规则，安装技能不会补出缺失原生接口。[病害拆除Skill](https://github.com/capskov/cad-distress-annotation)负责专业范围与分类。本仓库：[cad-callout-pair-layout](https://github.com/capskov/cad-callout-pair-layout)。三者独立开发发布，两个Skill不设为底座的全局依赖。

[匿名综合展示案例](https://github.com/capskov/cad-agent-foundation/tree/main/examples/road-demolition)实际使用项目Python／AutoCAD COM，不是全流程底座执行证明。复现还需指定组件、核验的补充操作和清理后的CAD输入；这里不附自动回放数据。

自有源码／说明采用Apache-2.0，依赖保留自身许可，见[声明](NOTICE.md)。相关词：AutoCAD、CAD annotation、LEADER、MTEXT、callout layout、CAD Agent Skill、MCP／Model Context Protocol。本Skill不是MCP服务器或Autodesk产品。

可选人工小工具：[BZYD中英文ANSI版本与使用说明](tools/autolisp/README.zh-CN.md)。直接调整已有标注，无需底座／Python。中文版本有AutoCAD2026历史实测；AutoCAD2022和英文提示版原生运行仍待验证。

[组件结构与CAD2022／2026分层支持](docs/STRUCTURE-AND-VERSIONS.md)。未来尺寸标注另建Skill，不把规划写成当前引线Skill能力。
