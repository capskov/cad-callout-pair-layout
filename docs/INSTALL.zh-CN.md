> Current v0.6 source preview / 当前v0.6源码预览：install this repository's main branch to use Agent planning and review_layout.py. Existing v0.3 release ZIPs contain the older pairwise mode. Keep the complete repository folder as the Skill, or preserve SKILL.md, SKILL.zh-CN.md, agents, references, scripts and examples together. No automatic CAD installation is added.

# 安装与试用公开预览包

[English](INSTALL.md) · [README](../README.zh-CN.md)

下载[v0.3.0-rc.1](https://github.com/capskov/cad-callout-pair-layout/releases/tag/v0.3.0-rc.1)，选择cad-callout-pair-layout-v0.3.0-rc.1.zip，包内顶层为cad-callout-pair-layout/；放入Agent客户端配置的Skill目录，不再多嵌套一层，保留SKILL.md、agents、references、scripts。已有私有安装先备份，不自动覆盖。发现由客户端负责，没有自动依赖安装器。

```text
<agent-skill-directory>/cad-callout-pair-layout/SKILL.md
<agent-skill-directory>/cad-callout-pair-layout/scripts/pair_layout.py
```

排布器需要Python3.10+和固定Shapely2.1.2。在适用Python环境内，从解压后的Skill根目录执行：

```text
python -m pip install -r requirements.txt
python scripts/pair_layout.py examples/synthetic-input.json output.json
python -m unittest discover -s scripts -p test_pair_layout.py
```

检查output.json的status／manual_ids／remaining_conflicts，仅计算图框局部几何建议，不安装底座、不写图／保存、不证明原生样式通过。进程成功退出也可能仍有冲突。

原生标注需[底座](https://github.com/capskov/cad-agent-foundation)、经认可的样式来源及可核验CAD工具。底座尚无公开可运行二进制，见[构建／安装边界](https://github.com/capskov/cad-agent-foundation/blob/main/docs/BUILD.zh-CN.md)。精确样式覆盖缺项见[兼容说明](COMPATIBILITY.md)。缺项先报告，不自动转COM或重放未知写入。

普通标注不需要[病害拆除Skill](https://github.com/capskov/cad-distress-annotation)。病害／拆除需三组件；与本Skill同级安装，见[病害Skill安装说明](https://github.com/capskov/cad-distress-annotation/blob/main/docs/INSTALL.zh-CN.md)。

只安装人工小工具时按[BZYD的APPLOAD说明](../tools/autolisp/README.zh-CN.md)操作，无需Python或底座；安装整个Skill ZIP时保留tools/目录。
