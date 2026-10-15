"""Review Agent-proposed callouts in one frame; never reads or writes CAD.

CLI: python review_layout.py plan.json report.json
Requires Shapely. Input contract: references/input-and-acceptance.md.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon

EPS = 1e-9


def _points(value, minimum):
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"Expected at least {minimum} XY points")
    result = []
    for item in value:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("Points must be XY pairs in the declared frame")
        xy = tuple(float(v) for v in item)
        if not all(math.isfinite(v) for v in xy):
            raise ValueError("Coordinates must be finite")
        result.append(xy)
    return result


def _polygon(value):
    result = Polygon(_points(value, 3))
    if not result.is_valid or result.area <= EPS:
        raise ValueError("Polygon must be valid and have positive area")
    return result


def _number(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("Tolerance/clearance must be finite and nonnegative")
    return result


def _near(a, b, clearance):
    # Touching boxes are conservative candidates, not proof of ink overlap.
    return a.intersects(b) or a.distance(b) + EPS < clearance


def review(plan):
    if plan.get("schema") != "callout-review-v1":
        raise ValueError("Expected schema callout-review-v1")
    if plan.get("coordinate_space") != "frame-local":
        raise ValueError("Convert all geometry to frame-local coordinates first")
    if plan.get("units") not in ("metres", "millimetres"):
        raise ValueError("Declare metres or millimetres; no automatic conversion")
    scale = plan.get("scale", {})
    if scale.get("sizing_mode", "preserve_native") != "preserve_native":
        raise ValueError("Automatic scale sizing is reserved, not implemented")
    if scale.get("denominator") is not None:
        if _number(scale["denominator"]) == 0:
            raise ValueError("Scale denominator must be positive")
    clearance = _number(plan.get("clearance", 0))
    tolerance = _number(plan.get("coordinate_tolerance", 1e-6))
    inner = plan.get("inner_frame")
    preferred = _polygon(inner["polygon"]) if inner else None
    visible = _polygon(plan["visible_polygon"]) if plan.get("visible_polygon") else None
    conflicts, warnings, rows = [], [], []

    def record(items, reason, *ids):
        items.append({"reason": reason, "ids": list(ids)})

    source = plan.get("callouts", [])
    if not source:
        raise ValueError("Provide at least one callout")
    ids = set()
    for row in source:
        rid = row["id"]
        if not isinstance(rid, str) or not rid or rid in ids:
            raise ValueError("Callout IDs must be unique nonempty strings")
        ids.add(rid)
        points = _points(row["leader"], 3)
        if len(points) != 3 or len(row["text_box"]) != 4:
            raise ValueError("Ordinary Leader needs 3 points; text_box needs 4 corners")
        a, b, c = points
        leader, text = LineString(points), _polygon(row["text_box"])
        if abs(b[1] - c[1]) > tolerance:
            record(conflicts, "tail_not_frame_horizontal", rid)
        ab = (a[0] - b[0], a[1] - b[1])
        cb = (c[0] - b[0], c[1] - b[1])
        product = math.hypot(*ab) * math.hypot(*cb)
        cosine = sum(x * y for x, y in zip(ab, cb)) / product if product else 1
        if not (-1 + EPS < cosine < -EPS):
            record(conflicts, "bend_not_strictly_obtuse", rid)
        # Own bottom gap belongs to the style; inter-label clearance does not
        # apply to the acute approach near this callout's own bend.
        if leader.intersects(text):
            record(conflicts, "self_leader_text_candidate", rid)
        if preferred is not None and not (preferred.covers(leader) and preferred.covers(text)):
            record(warnings, "outside_preferred_inner_frame", rid)
        if visible is not None and not (visible.covers(leader) and visible.covers(text)):
            record(conflicts, "outside_supplied_visible_polygon", rid)
        target = row.get("target")
        if target:
            kind = target["kind"]
            if kind == "point":
                shape = Point(_points([target["point"]], 1)[0])
            elif kind == "line":
                shape = LineString(_points(target["points"], 2))
            elif kind == "polygon":
                shape = _polygon(target["points"])
            else:
                raise ValueError("target.kind must be point, line or polygon")
            if shape.distance(Point(a)) > _number(target.get("tolerance", tolerance)):
                record(conflicts, "anchor_outside_supplied_target", rid)
        else:
            record(warnings, "anchor_target_not_supplied", rid)
        rows.append((rid, leader, text))

    blockers = []
    for obstacle in plan.get("keepouts", []):
        applies = obstacle.get("applies_to", "text")
        if applies not in ("text", "leader", "both"):
            raise ValueError("keepout.applies_to must be text, leader or both")
        blockers.append((obstacle["id"], applies, _polygon(obstacle["polygon"])))
    for i, (rid, leader, text) in enumerate(rows):
        for other, other_leader, other_text in rows[i + 1:]:
            if _near(text, other_text, clearance):
                record(conflicts, "text_text_candidate", rid, other)
            if _near(leader, other_text, clearance):
                record(conflicts, "leader_text_candidate", rid, other)
            if _near(other_leader, text, clearance):
                record(conflicts, "leader_text_candidate", other, rid)
            if leader.crosses(other_leader):
                record(conflicts, "leader_crossing", rid, other)
            elif leader.intersects(other_leader):
                record(warnings, "leader_contact_or_overlap", rid, other)
        for oid, applies, shape in blockers:
            if applies in ("text", "both") and _near(text, shape, clearance):
                record(conflicts, "text_keepout_candidate", rid, oid)
            if applies in ("leader", "both") and _near(leader, shape, clearance):
                record(conflicts, "leader_keepout_candidate", rid, oid)
    unchecked = ["CAD_association_and_style", "native_recompute_and_actual_display",
                 "target_identity_and_input_provenance", "unprovided_background", "dot_and_line_weight"]
    if visible is None:
        unchecked.append("viewport_clipping")
    if preferred is None:
        unchecked.append("inner_frame_containment")
    return {"schema": "callout-review-result-v1", "callout_count": len(rows),
            "status": "conflicts_found" if conflicts else "no_conflicts_in_supplied_geometry",
            "geometry_conflicts": conflicts, "warnings": warnings, "not_checked": unchecked,
            "inner_frame_evidence": inner.get("evidence") if inner else None,
            "scale_record": scale, "cad_effects": "none"}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: review_layout.py plan.json report.json")
    source_path, output_path = (Path(p).resolve() for p in sys.argv[1:])
    if source_path == output_path or output_path.suffix.lower() != ".json":
        raise SystemExit("Use a distinct .json report path; input is never overwritten")
    result = review(json.loads(source_path.read_text(encoding="utf-8-sig")))
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
