# BZYD manual callout adjustment

[中文](README.zh-CN.md). Optional human-operated tool, separate from Agent rules and solver. No Foundation, MCP, Python or Shapely is required. BZYD is one command, not separate BZ/YD commands; it adjusts existing callouts, not creation.

## Manual operation

1. Choose callout_move.en.lsp or callout_move.zh-CN.lsp and APPLOAD only one. Both define BZYD/bzym:move; loading the other replaces the prompt language. Follow existing trusted-load settings; do not disable SECURELOAD. First try an isolated drawing copy and preserve an existing installation.
2. Enter BZYD and select one ordinary three-vertex LEADER, or preselect exactly one first. Multiple selection, MLeader or text-only selection is rejected.
3. Click a new elbow location; the current elbow is the default base. Anchor stays fixed; elbow/tail/associated MTEXT move and the diagonal reconnects.
4. Enter B for a custom base, then pick base/target. Escape or zero displacement leaves objects unchanged. This is not a live whole-group drag preview.
5. A valid acute-angle result can flip the tail/text side while preserving text orientation/content and tail length; right/obtuse angles keep the side. Inspect the resulting placement/background. One U/UNDO restores a successful operation. If restoration is unconfirmed, undo and inspect immediately; do not keep retrying.

Only ordinary straight three-vertex LEADER with one unique same-space MTEXT association. Locked layers/shared annotation/wrong type or association/noncoplanar/degenerate targets are rejected. No DIMENSION/MLeader/proxy/unlinked line support, batch creation or whole-drawing avoidance.

## Encoding and compatibility

Both files are ANSI, specifically CP936/GBK with no BOM. English is ASCII-compatible; documentation is UTF-8. Chinese file is byte-identical to the accepted tool. English changes only 50 UI/error strings and comments; Lisp expressions, control strings, command names and DXF semantics match.

The original Chinese version has 11 historical AutoCAD2026 isolated angle/undo/save-reopen checks (2026-10-12), not manual mouse-experience/full-drawing approval. Nonzero DXF213 and hooked leaders remain untested. The English translation has encoding/expression equivalence checks only, no new CAD-native acceptance.

AutoCAD2022 is unverified. Use of older AutoLISP APIs does not establish tested version compatibility. This utility is independent of the 2026 native bridge; a targeted 2022 check can later add a supported-host row in this same package without a separate old repository.

Manual Lisp directly edits the selected drawing and does not participate in Foundation request identity/journal/fences. Do not use it to bypass unresolved writes or describe its undo/readback as Foundation governance. See root LICENSE/NOTICE.
