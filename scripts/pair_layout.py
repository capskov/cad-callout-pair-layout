"""Self-contained adjacent-pair layout for CAD callout labels.

Coordinates are frame-local. The module only computes proposed geometry; it
does not access or modify CAD documents. Requires Shapely for robust distances.
CLI: python pair_layout.py input.json output.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from shapely.geometry import LineString, Point, Polygon, box

EPS = 1e-9
DIRECTION_TOL = 1e-7
HORIZONTAL_TOL = 1e-8
OFFSETS = [(-2., 0.), (2., 0.), (-4., 0.), (4., 0.), (-6., 0.), (6., 0.)]


def _geometry(row: dict, length: float, translation=(0., 0.)) -> dict:
    ax, ay = map(float, row["anchor"])
    ux, uy = map(float, row["direction"])
    dx, dy = translation
    a = (ax + dx, ay + dy)
    b = (a[0] + ux * length, a[1] + uy * length)
    sign, width, gap, height = (int(row.get("opening_sign", 1)), float(row["width"]),
                                float(row["gap"]), float(row["height"]))
    c = (b[0] + sign * width, b[1])
    rect = box(min(b[0], c[0]), b[1] + gap,
               max(b[0], c[0]), b[1] + gap + height)
    leader = LineString([a, b, c])
    # MTEXT attachment 9: insert is always the rectangle's bottom-right.
    insert = (max(b[0], c[0]), b[1] + gap)
    return {"a": a, "b": b, "c": c, "rect": rect, "leader": leader, "insert": insert}


def _inside(g: dict, bounds) -> bool:
    xmin, ymin, xmax, ymax = bounds
    return (g["leader"].bounds[0] >= xmin - EPS and g["leader"].bounds[1] >= ymin - EPS
            and g["leader"].bounds[2] <= xmax + EPS and g["leader"].bounds[3] <= ymax + EPS
            and g["rect"].bounds[0] >= xmin - EPS and g["rect"].bounds[1] >= ymin - EPS
            and g["rect"].bounds[2] <= xmax + EPS and g["rect"].bounds[3] <= ymax + EPS)


def _target_ok(row: dict, anchor) -> bool:
    target = row.get("target")
    if not target:
        return True
    p = Point(anchor)
    if target["kind"] == "polygon":
        return Polygon(target["points"]).covers(p) or Polygon(target["points"]).distance(p) <= 1e-6
    if target["kind"] == "line":
        return LineString(target["points"]).distance(p) <= 1e-6
    raise ValueError(f"{row['id']}: target.kind must be polygon or line")


def _dist(a, b) -> float:
    return a.distance(b)


def _text_pairs(rows, geoms, clearance):
    return [(str(a["id"]), str(b["id"])) for i, a in enumerate(rows) for b in rows[i+1:]
            if _dist(geoms[str(a["id"])]["rect"], geoms[str(b["id"])]["rect"]) + EPS < clearance]


def _trigger_pairs(rows, geoms, clearance, check_leader_text=True):
    """Pairs eligible for grouping; line-line clearance stays diagnostic only."""
    found = []
    for i, a in enumerate(rows):
        ga = geoms[str(a["id"])]
        for b in rows[i + 1:]:
            gb = geoms[str(b["id"])]
            if (_dist(ga["rect"], gb["rect"]) + EPS < clearance
                    or (check_leader_text and
                        (_dist(ga["leader"], gb["rect"]) + EPS < clearance
                         or _dist(gb["leader"], ga["rect"]) + EPS < clearance))):
                found.append((str(a["id"]), str(b["id"])))
    return found


def _leader_pairs(rows, geoms, clearance):
    return [(str(a["id"]), str(b["id"])) for i, a in enumerate(rows) for b in rows[i + 1:]
            if (_dist(geoms[str(a["id"])]["leader"], geoms[str(b["id"])]["rect"]) + EPS < clearance
                or _dist(geoms[str(b["id"])]["leader"], geoms[str(a["id"])]["rect"]) + EPS < clearance)]


def _pair_clear(g, h, clearance, check_leader_text=True):
    return (_dist(g["rect"], h["rect"]) + EPS >= clearance
            and (not check_leader_text or
                 (_dist(g["leader"], h["rect"]) + EPS >= clearance
                  and _dist(h["leader"], g["rect"]) + EPS >= clearance)))


def _pair_reasons(g, h, clearance, check_leader_text=True):
    reasons = []
    if _dist(g["rect"], h["rect"]) + EPS < clearance:
        reasons.append("pair_text_clearance")
    if check_leader_text:
        if _dist(g["leader"], h["rect"]) + EPS < clearance:
            reasons.append("leader_text_clearance")
        if _dist(h["leader"], g["rect"]) + EPS < clearance:
            reasons.append("leader_text_clearance")
    return reasons


def _candidate_valid(row, g, bounds):
    reasons = []
    if not _inside(g, bounds):
        reasons.append("outside_frame")
    if not _target_ok(row, g["a"]):
        reasons.append("anchor_outside_target")
    side = row.get("road_side")
    if side:
        cx, cy = map(float, side["point"])
        nx, ny = map(float, side["normal"])
        minimum = float(side.get("min_text_distance", 0.))
        signed = lambda p: (p[0] - cx) * nx + (p[1] - cy) * ny
        if any(signed(g[k]) < -EPS for k in ("a", "b", "c")):
            reasons.append("road_side_leader_crosses_centerline")
        if min(signed(p) for p in list(g["rect"].exterior.coords)[:-1]) + EPS < minimum:
            reasons.append("road_side_text_clearance")
        ux, uy = map(float, row["direction"])
        if ux * nx + uy * ny <= EPS:
            reasons.append("road_side_ray_not_outward")
    return reasons


def _components(ids, pairs):
    adj = {x: set() for x in ids}
    for a, b in pairs:
        adj[a].add(b); adj[b].add(a)
    seen, result = set(), []
    for x in ids:
        if x in seen or not adj[x]:
            continue
        stack, comp = [x], []
        seen.add(x)
        while stack:
            u = stack.pop(); comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); stack.append(v)
        result.append(comp)
    return result


def _validate(data):
    bounds = tuple(map(float, data["bounds"]))
    if len(bounds) != 4 or bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
        raise ValueError("bounds must be [xmin,ymin,xmax,ymax] with positive area")
    clearance, step = float(data.get("clearance", .15)), float(data.get("step", 5.))
    max_ext = int(data.get("max_extensions", 5))
    max_rounds = int(data.get("max_rounds", 3))
    y_ref = float(data.get("y_ref", 0.))
    if not all(math.isfinite(x) for x in bounds + (clearance, step, y_ref)):
        raise ValueError("bounds, clearance, step and y_ref must be finite")
    if clearance <= 0 or step <= 0 or max_ext < 0 or max_rounds < 1:
        raise ValueError("clearance/step must be positive, max_extensions nonnegative and max_rounds positive")
    rows = data["rows"]
    ids = [str(r["id"]) for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("row ids must be unique within a page")
    for row in rows:
        rid = str(row["id"])
        if len(row["anchor"]) != 2 or len(row["direction"]) != 2:
            raise ValueError(f"{rid}: anchor and direction must each contain 2 numbers")
        anchor = list(map(float, row["anchor"]))
        direction = list(map(float, row["direction"]))
        if not all(math.isfinite(x) for x in anchor + direction):
            raise ValueError(f"{rid}: anchor/direction must be finite")
        if abs(math.hypot(*direction) - 1.) > 1e-6:
            raise ValueError(f"{rid}: direction must be a unit vector")
        for key in ("length", "width", "height", "gap"):
            value = float(row[key])
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{rid}: {key} must be finite and positive")
        sign = int(row.get("opening_sign", 1))
        if sign not in (-1, 1):
            raise ValueError(f"{rid}: opening_sign must be -1 or +1")
        # The inside angle at the elbow must be strictly obtuse. This also
        # excludes a degenerate/reversing tail that self-overlaps the ray.
        ux, _ = direction
        if sign * ux <= EPS or abs(direction[1]) <= EPS:
            raise ValueError(f"{rid}: ray/tail elbow must be strictly obtuse and non-self-overlapping")
        side = row.get("road_side")
        if side:
            try:
                point, normal = side["point"], side["normal"]
                if len(point) != 2 or len(normal) != 2:
                    raise ValueError
                point, normal = list(map(float, point)), list(map(float, normal))
                minimum = float(side.get("min_text_distance", 0.))
            except (KeyError, TypeError, ValueError):
                raise ValueError(f"{rid}: road_side requires point, normal and nonnegative min_text_distance")
            if (not all(math.isfinite(v) for v in point + normal + [minimum]) or minimum < 0
                    or abs(math.hypot(*normal) - 1.) > 1e-6):
                raise ValueError(f"{rid}: road_side point/normal must be finite, normal unit length and min_text_distance nonnegative")
        target = row.get("target")
        if target:
            if target.get("kind") == "polygon":
                poly = Polygon(target["points"])
                if len(target["points"]) < 3 or poly.is_empty or not poly.is_valid or poly.area <= EPS:
                    raise ValueError(f"{rid}: target polygon must be a valid nondegenerate polygon")
                if not (poly.covers(Point(anchor)) or poly.distance(Point(anchor)) <= 1e-6):
                    raise ValueError(f"{rid}: initial anchor is outside target polygon")
            elif target.get("kind") == "line":
                line = LineString(target["points"])
                if len(target["points"]) < 2 or line.is_empty or line.length <= EPS:
                    raise ValueError(f"{rid}: target line must be nondegenerate")
                if line.distance(Point(anchor)) > 1e-6:
                    raise ValueError(f"{rid}: initial anchor is outside target line")
            else:
                raise ValueError(f"{rid}: target.kind must be polygon or line")
    obstacles = []
    for obstacle in data.get("obstacles", []):
        poly = Polygon(obstacle["polygon"])
        if len(obstacle["polygon"]) < 3 or not poly.is_valid or poly.area <= EPS:
            raise ValueError(f"obstacle {obstacle.get('id', '')}: polygon must be valid and nondegenerate")
        obstacles.append((str(obstacle.get("id", "")), poly))
    return bounds, clearance, step, max_ext, max_rounds, y_ref, rows, obstacles


def _full_conflicts(rows, geoms, obstacles, clearance):
    found = []
    for i, row in enumerate(rows):
        rid, g = str(row["id"]), geoms[str(row["id"])]
        if _dist(g["leader"], g["rect"]) + EPS < clearance:
            found.append({"type": "single", "id": rid, "reason": "own_text_leader_clearance"})
        for oid, poly in obstacles:
            if _dist(g["rect"], poly) + EPS < clearance:
                found.append({"type": "single", "id": rid, "reason": f"text_background:{oid}"})
            if _dist(g["leader"], poly) + EPS < clearance:
                found.append({"type": "single", "id": rid, "reason": f"leader_background:{oid}"})
        for other in rows[i+1:]:
            oid, h = str(other["id"]), geoms[str(other["id"])]
            if _dist(g["rect"], h["rect"]) + EPS < clearance:
                found.append({"type": "pair", "ids": [rid, oid], "reason": "text_text_clearance"})
            if _dist(g["leader"], h["rect"]) + EPS < clearance:
                found.append({"type": "pair", "ids": [rid, oid], "reason": "leader_text_clearance"})
            if _dist(h["leader"], g["rect"]) + EPS < clearance:
                found.append({"type": "pair", "ids": [oid, rid], "reason": "leader_text_clearance"})
            if _dist(g["leader"], h["leader"]) + EPS < clearance:
                found.append({"type": "pair", "ids": [rid, oid], "reason": "leader_leader_clearance"})
    return found


def solve_page(data: dict[str, Any]) -> dict[str, Any]:
    bounds, clearance, step, max_ext, max_rounds, y_ref, rows, obstacles = _validate(data)
    check_leader_text = bool(data.get("check_leader_text", True))
    ids = [str(r["id"]) for r in rows]
    rowmap = {str(r["id"]): r for r in rows}
    lengths = {str(r["id"]): float(r["length"]) for r in rows}
    extensions_used = {rid: 0 for rid in ids}
    translations = {rid: (0., 0.) for rid in ids}
    tried_translations = {rid: set() for rid in ids}
    signs = {str(r["id"]): int(r.get("opening_sign", 1)) for r in rows}
    geoms = {rid: _geometry(rowmap[rid], lengths[rid]) for rid in ids}
    initial = {rid: {k: list(geoms[rid][k]) for k in ("a", "b", "c")} for rid in ids}
    for rid in ids:
        if not _inside(geoms[rid], bounds):
            raise ValueError(f"{rid}: initial callout is outside bounds")
        reasons = _candidate_valid(rowmap[rid], geoms[rid], bounds)
        if reasons:
            raise ValueError(f"{rid}: initial callout violates road_side/target constraints: {', '.join(reasons)}")
    initial_pairs = _text_pairs(rows, geoms, clearance)
    attempts = {rid: [] for rid in ids}
    status = {rid: "retained" for rid in ids}
    groups, projections, rounds = [], {}, []

    stop_reason = "max_rounds_reached"
    tried_candidates = {rid: set() for rid in ids}
    for round_index in range(1, max_rounds + 1):
        before = {rid: (lengths[rid], translations[rid]) for rid in ids}
        word_pairs = _text_pairs(rows, geoms, clearance)
        leader_pairs = _leader_pairs(rows, geoms, clearance) if check_leader_text else []
        trigger_pairs = sorted(set(word_pairs) | set(leader_pairs))
        round_groups = []
        projections = {}
        for rid in ids:
            row, g = rowmap[rid], geoms[rid]
            ux, uy = map(float, row["direction"])
            if abs(uy) < HORIZONTAL_TOL:
                projections[rid] = {"y_ref": y_ref, "x_ref": None, "status": "manual_horizontal_ray"}
            else:
                xref = g["b"][0] + (y_ref - g["b"][1]) * ux / uy
                projections[rid] = {"y_ref": y_ref, "x_ref": xref, "status": "projected"}

        # Stage one: text-only components preserve the original text priority.
        for gi, comp in enumerate(_components(ids, word_pairs), 1):
            entry = {"id": f"R{round_index}-W{gi}", "round_index": round_index,
                     "phase": "word", "members": list(comp), "neighbor_pairs": [], "status": "processed"}
            if len({signs[x] for x in comp}) > 1:
                entry["status"] = "manual_mixed_opening"; round_groups.append(entry); continue
            if not all(max(abs(float(rowmap[x]["direction"][k]) - float(rowmap[comp[0]]["direction"][k]))
                            for k in (0, 1)) <= DIRECTION_TOL for x in comp):
                entry["status"] = "manual_nonparallel"; round_groups.append(entry); continue
            if any(projections[x]["x_ref"] is None for x in comp):
                entry["status"] = "manual_horizontal_ray"; round_groups.append(entry); continue
            sign = signs[comp[0]]
            tied = {x for x in comp if sum(abs(projections[x]["x_ref"] - projections[y]["x_ref"]) <= EPS
                                           for y in comp) > 1}
            if tied:
                entry["status"] = "manual_tied_projection"; round_groups.append(entry); continue
            ordered = sorted(comp, key=lambda x: projections[x]["x_ref"], reverse=(sign == 1))
            entry["members"] = ordered
            for i in range(len(ordered) - 1):
                moving, neighbor = ordered[i + 1], ordered[i]
                entry["neighbor_pairs"].append([moving, neighbor])
                if _dist(geoms[moving]["rect"], geoms[neighbor]["rect"]) + EPS >= clearance:
                    continue
                row, base_length = rowmap[moving], lengths[moving]
                base_level = int(round((base_length - float(row["length"])) / step))
                last_legal = None
                succeeded = False
                for level in range(base_level + 1, max_ext + 1):
                    candidate_len = float(row["length"]) + level * step
                    key = ("word", neighbor, round(candidate_len, 9))
                    if key in tried_candidates[moving]:
                        continue
                    tried_candidates[moving].add(key)
                    cand = _geometry(row, candidate_len, translations[moving])
                    reasons = _candidate_valid(row, cand, bounds)
                    clear = _dist(cand["rect"], geoms[neighbor]["rect"]) + EPS >= clearance
                    if not clear: reasons.append("pair_text_clearance")
                    attempts[moving].append({"phase": "extend", "stage": "word", "round_index": round_index,
                                             "length": candidate_len, "translation": list(translations[moving]),
                                             "passed": not reasons, "checked_neighbor": neighbor,
                                             "reasons": reasons})
                    if not [r for r in reasons if r != "pair_text_clearance"]:
                        last_legal = (candidate_len, cand)
                    if not reasons:
                        lengths[moving], geoms[moving], status[moving] = candidate_len, cand, "extended"
                        succeeded = True
                        break
                if not succeeded and last_legal and last_legal[0] > lengths[moving]:
                    lengths[moving], geoms[moving], status[moving] = last_legal[0], last_legal[1], "extended"
                if not succeeded:
                    for off in OFFSETS:
                        candidate_translation = (translations[moving][0] + off[0], translations[moving][1] + off[1])
                        tkey = tuple(round(v, 9) for v in candidate_translation)
                        key = ("word_translate", neighbor, tkey)
                        if tkey == (0., 0.) or tkey in tried_translations[moving] or key in tried_candidates[moving]:
                            continue
                        tried_candidates[moving].add(key)
                        tried_translations[moving].add(tkey)
                        cand = _geometry(row, lengths[moving], candidate_translation)
                        reasons = _candidate_valid(row, cand, bounds)
                        if _dist(cand["rect"], geoms[neighbor]["rect"]) + EPS < clearance:
                            reasons.append("pair_text_clearance")
                        attempts[moving].append({"phase": "translate", "stage": "word", "round_index": round_index,
                                                 "length": lengths[moving], "translation": list(candidate_translation),
                                                 "passed": not reasons, "checked_neighbor": neighbor,
                                                 "reasons": reasons})
                        if not reasons:
                            translations[moving], geoms[moving], status[moving] = candidate_translation, cand, "translated"
                            succeeded = True
                            break
            round_groups.append(entry)

        # Stage two: process each real leader/text crossing independently. It never
        # joins those edges into a transitive component and cannot create text overlap.
        for rid in ids:
            row, g = rowmap[rid], geoms[rid]
            ux, uy = map(float, row["direction"])
            if abs(uy) < HORIZONTAL_TOL:
                projections[rid] = {"y_ref": y_ref, "x_ref": None, "status": "manual_horizontal_ray"}
            else:
                xref = g["b"][0] + (y_ref - g["b"][1]) * ux / uy
                projections[rid] = {"y_ref": y_ref, "x_ref": xref, "status": "projected"}
        current_leaders = _leader_pairs(rows, geoms, clearance) if check_leader_text else []
        leader_jobs = []
        for a, b in current_leaders:
            if signs[a] != signs[b]:
                round_groups.append({"id": f"R{round_index}-L{a}-{b}", "round_index": round_index,
                                     "phase": "leader", "members": [a, b], "neighbor_pairs": [],
                                     "status": "manual_mixed_opening"})
                continue
            if max(abs(float(rowmap[a]["direction"][k]) - float(rowmap[b]["direction"][k]))
                   for k in (0, 1)) > DIRECTION_TOL or projections[a]["x_ref"] is None or projections[b]["x_ref"] is None:
                round_groups.append({"id": f"R{round_index}-L{a}-{b}", "round_index": round_index,
                                     "phase": "leader", "members": [a, b], "neighbor_pairs": [],
                                     "status": "manual_nonparallel"})
                continue
            xa, xb = projections[a]["x_ref"], projections[b]["x_ref"]
            if abs(xa - xb) <= EPS:
                round_groups.append({"id": f"R{round_index}-L{a}-{b}", "round_index": round_index,
                                     "phase": "leader", "members": [a, b], "neighbor_pairs": [],
                                     "status": "manual_tied_projection"})
                continue
            moving, neighbor = (a, b) if (signs[a] == 1 and xa < xb) or (signs[a] == -1 and xa > xb) else (b, a)
            leader_jobs.append((projections[moving]["x_ref"], moving, neighbor))
        leader_jobs.sort(key=lambda x: (signs[x[1]], -x[0] if signs[x[1]] == 1 else x[0]))
        for li, (_, moving, neighbor) in enumerate(leader_jobs, 1):
            entry = {"id": f"R{round_index}-L{li}", "round_index": round_index,
                     "phase": "leader", "members": [moving, neighbor],
                     "neighbor_pairs": [[moving, neighbor]], "status": "processed"}
            row = rowmap[moving]
            if not _pair_clear(geoms[moving], geoms[neighbor], clearance, True):
                before_text = set(_text_pairs(rows, geoms, clearance))
                start_level = int(round((lengths[moving] - float(row["length"])) / step))
                last_safe = None
                succeeded = False
                for level in range(start_level + 1, max_ext + 1):
                    candidate_len = float(row["length"]) + level * step
                    key = ("leader", neighbor, round(candidate_len, 9))
                    if key in tried_candidates[moving]: continue
                    tried_candidates[moving].add(key)
                    cand = _geometry(row, candidate_len, translations[moving])
                    reasons = _candidate_valid(row, cand, bounds)
                    if not _pair_clear(cand, geoms[neighbor], clearance, True):
                        reasons.extend(_pair_reasons(cand, geoms[neighbor], clearance, True))
                    candidate_text = set(_text_pairs(rows, {**geoms, moving: cand}, clearance))
                    if not candidate_text.issubset(before_text): reasons.append("new_text_conflict")
                    attempts[moving].append({"phase": "leader_extend", "round_index": round_index,
                                             "length": candidate_len, "translation": list(translations[moving]),
                                             "passed": not reasons, "checked_neighbor": neighbor,
                                             "reasons": reasons})
                    if all(r in ("pair_text_clearance", "leader_text_clearance") for r in reasons):
                        last_safe = (candidate_len, cand)
                    if not reasons:
                        lengths[moving], geoms[moving], status[moving] = candidate_len, cand, "extended"
                        succeeded = True
                        break
                if not succeeded and last_safe and last_safe[0] > lengths[moving]:
                    lengths[moving], geoms[moving], status[moving] = last_safe[0], last_safe[1], "extended"
                for off in OFFSETS if not succeeded else []:
                    candidate_translation = (translations[moving][0] + off[0], translations[moving][1] + off[1])
                    tkey = tuple(round(v, 9) for v in candidate_translation)
                    key = ("leader_translate", neighbor, tkey)
                    if tkey == (0., 0.) or tkey in tried_translations[moving] or key in tried_candidates[moving]:
                        continue
                    tried_candidates[moving].add(key); tried_translations[moving].add(tkey)
                    cand = _geometry(row, lengths[moving], candidate_translation)
                    reasons = _candidate_valid(row, cand, bounds)
                    if not _pair_clear(cand, geoms[neighbor], clearance, True):
                        reasons.extend(_pair_reasons(cand, geoms[neighbor], clearance, True))
                    candidate_text = set(_text_pairs(rows, {**geoms, moving: cand}, clearance))
                    if not candidate_text.issubset(set(_text_pairs(rows, geoms, clearance))):
                        reasons.append("new_text_conflict")
                    attempts[moving].append({"phase": "leader_translate", "round_index": round_index,
                                             "length": lengths[moving], "translation": list(candidate_translation),
                                             "passed": not reasons, "checked_neighbor": neighbor,
                                             "reasons": reasons})
                    if not reasons:
                        translations[moving], geoms[moving], status[moving] = candidate_translation, cand, "translated"
                        succeeded = True; break
            round_groups.append(entry)
        extensions_used = {rid: min(max_ext, max(0, int(round((lengths[rid] - float(rowmap[rid]["length"])) / step))))
                           for rid in ids}
        groups.extend(round_groups)
        changed = any(before[rid] != (lengths[rid], translations[rid]) for rid in ids)
        rounds.append({"round_index": round_index, "trigger_pairs": [list(p) for p in trigger_pairs],
                       "word_pairs": [list(p) for p in word_pairs],
                       "leader_pairs": [list(p) for p in leader_pairs],
                       "group_count": len(round_groups), "geometry_changed": changed,
                       "extensions_used": dict(extensions_used)})
        if not changed:
            stop_reason = "no_geometry_change"
            break
        if not _text_pairs(rows, geoms, clearance) and not (check_leader_text and _leader_pairs(rows, geoms, clearance)):
            stop_reason = "no_actionable_conflicts"
            break

    # Diagnostics across all texts, leaders and supplied background polygons;
    # these are reported only and never trigger additional movement.
    remaining = _full_conflicts(rows, geoms, obstacles, clearance)
    active_ids = {rid for c in remaining if c.get("type") == "pair"
                  and c.get("reason") in ("text_text_clearance", "leader_text_clearance")
                  for rid in c["ids"]}
    for rid in ids:
        if rid in active_ids:
            status[rid] = "failed"
        elif status[rid] == "failed":
            if translations[rid] != (0., 0.): status[rid] = "translated"
            elif lengths[rid] > float(rowmap[rid]["length"]): status[rid] = "extended"
            else: status[rid] = "retained"
    manual = set()
    for conflict in remaining:
        if "ids" in conflict: manual.update(conflict["ids"])
        elif "id" in conflict: manual.add(conflict["id"])
    outrows = []
    for row in rows:
        rid, g = str(row["id"]), geoms[str(row["id"])]
        outrows.append({**row, "chosen_length": lengths[rid],
                        "translation": list(translations[rid]),
                        "points": [list(g[k]) for k in ("a", "b", "c")], "insert": list(g["insert"]),
                        "status": status[rid], "attempts": attempts[rid]})
    return {**data, "rows": outrows, "groups": groups,
            "initial_points": initial,
            "projection_metadata": {"y_ref": y_ref, "by_id": projections,
                                    "rule": "x_ref = B.x + (y_ref-B.y)*u.x/u.y; equivalent to anchor projection; independent of ray length"},
            "initial_text_conflicts": [{"type": "pair", "ids": list(p), "reason": "text_text_clearance"} for p in initial_pairs],
            "remaining_conflicts": remaining, "manual_ids": [x for x in ids if x in manual],
            "rounds": rounds, "round_count": len(rounds), "stop_reason": stop_reason,
            "extensions_used": sum(extensions_used.values()),
            "extensions_used_by_id": extensions_used,
            "summary": {"row_count": len(rows), "group_count": len(groups),
                        "retained": sum(x == "retained" for x in status.values()),
                        "extended": sum(x == "extended" for x in status.values()),
                        "translated": sum(x == "translated" for x in status.values()),
                        "failed": sum(x == "failed" for x in status.values()),
                        "remaining_conflict_count": len(remaining)},
            "status": "solved" if not remaining and not manual else "partial_conflicts"}


def solve(data: dict[str, Any]) -> dict[str, Any]:
    if "pages" not in data:
        return solve_page(data)
    pages = data["pages"]
    solved = [solve_page(page) for page in pages]
    return {**{k: v for k, v in data.items() if k != "pages"}, "pages": solved,
            "summary": {"page_count": len(solved), "row_count": sum(x["summary"]["row_count"] for x in solved),
                        "manual_count": sum(len(x["manual_ids"]) for x in solved),
                        "remaining_conflict_count": sum(len(x["remaining_conflicts"]) for x in solved)},
            "status": "solved" if all(x["status"] == "solved" for x in solved) else "partial_conflicts"}


def main(argv):
    if len(argv) != 3:
        print("Usage: python pair_layout.py input.json output.json", file=sys.stderr)
        return 2
    src, dst = map(Path, argv[1:])
    result = solve(json.loads(src.read_text(encoding="utf-8")))
    dst.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
