# Install and try the public preview

[中文](INSTALL.zh-CN.md) · [README](../README.md)

Download [v0.3.0-rc.1](https://github.com/capskov/cad-callout-pair-layout/releases/tag/v0.3.0-rc.1) and choose cad-callout-pair-layout-v0.3.0-rc.1.zip. It has top-level cad-callout-pair-layout/. Extract into your Agent client's configured Skill directory with no extra nesting; preserve SKILL.md, agents, references and scripts. Back up an existing private installation; installation is manual; do not overwrite it without checking differences. Client discovery remains the client's responsibility. No automatic dependency installer exists.

```text
<agent-skill-directory>/cad-callout-pair-layout/SKILL.md
<agent-skill-directory>/cad-callout-pair-layout/scripts/pair_layout.py
```

Python3.10+ and pinned Shapely2.1.2 are required for the solver. In an appropriate environment, from the extracted Skill root:

```text
python -m pip install -r requirements.txt
python scripts/pair_layout.py examples/synthetic-input.json output.json
python -m unittest discover -s scripts -p test_pair_layout.py
```

Inspect output status/manual_ids/remaining_conflicts. It computes frame-local proposals only; no Foundation installation, CAD write/save or native style certification occurs. Nonzero conflicts can coexist with exit code zero.

Native callouts need [Foundation](https://github.com/capskov/cad-agent-foundation), approved style evidence and verified tools. Foundation has no public runnable binary asset yet; see its [build/install boundary](https://github.com/capskov/cad-agent-foundation/blob/main/docs/BUILD.md). [Compatibility](COMPATIBILITY.md) lists missing exact style/native coverage. Report missing components/tools before dependent writes; do not invent automatic COM fallback or replay uncertain writes.

Ordinary callouts do not need the [distress Skill](https://github.com/capskov/cad-distress-annotation). Distress/demolition needs all three components; install both public Skill folders as siblings. See the [distress installation guide](https://github.com/capskov/cad-distress-annotation/blob/main/docs/INSTALL.md).

Optional manual-only installation: use [BZYD APPLOAD instructions](../tools/autolisp/README.md); neither Python nor Foundation is needed for that utility. Keep tools/ if installing the whole Skill ZIP.
