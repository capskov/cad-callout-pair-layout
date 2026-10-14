"""Focused regressions for the standalone pair-layout tool."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shapely.geometry import box

MODULE = Path(__file__).with_name("pair_layout.py")
SPEC = importlib.util.spec_from_file_location("pair_layout_under_test", MODULE)
layout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(layout)


def row(rid, x=0., y=0., direction=(.6, -.8), length=10., width=4., sign=1, target=None):
    if target is None:
        target = {"kind": "polygon", "points": [[-100, -100], [100, -100], [100, 100], [-100, 100]]}
    return {"id": rid, "anchor": [x, y], "direction": list(direction), "length": length,
            "width": width, "height": 2., "gap": .5, "opening_sign": sign, "target": target}


def data(rows, bounds=(-50, -50, 80, 30), obstacles=None, **cfg):
    return {"bounds": list(bounds), "clearance": .15, "step": 5., "max_extensions": 5,
            "max_rounds": 1, "check_leader_text": False,
            "rows": rows, "obstacles": obstacles or [], **cfg}


class PairLayoutTests(unittest.TestCase):

    def test_default_v02_detects_leader_through_other_text_without_text_overlap(self):
        a = row("A", 1.5603368793712526, 5.074416378935707, width=6.263825136384522)
        b = row("B", -0.9995705599748668, 7.3178621668475365, width=3.1037106528144873)
        source = data([a, b], max_rounds=3)
        source.pop("check_leader_text")
        gs = {r["id"]: layout._geometry(r, r["length"]) for r in (a, b)}
        self.assertGreaterEqual(gs["A"]["rect"].distance(gs["B"]["rect"]), source["clearance"])
        self.assertLess(min(gs["A"]["leader"].distance(gs["B"]["rect"]),
                            gs["B"]["leader"].distance(gs["A"]["rect"])), source["clearance"])
        result = layout.solve(source)
        self.assertTrue(result["rounds"][0]["trigger_pairs"])
        self.assertTrue(any(a["phase"] == "leader_extend" for r in result["rows"] for a in r["attempts"]))

    def test_leader_stage_order_mirrors_for_left_opening_pairs(self):
        pair_points = [(1.5603368793712526, 5.074416378935707, 6.263825136384522),
                       (-0.9995705599748668, 7.3178621668475365, 3.1037106528144873)]

        def make_rows(mirror):
            rows = []
            for prefix, shift in (("A", 0.), ("C", 60.)):
                for index, (x, y, width) in enumerate(pair_points):
                    x += shift
                    if mirror:
                        x, direction, sign = -x, (-.6, -.8), -1
                    else:
                        direction, sign = (.6, -.8), 1
                    rows.append(row(f"{prefix}{index}", x, y, direction=direction,
                                    width=width, sign=sign))
            return rows

        orders = {}
        for mirror in (False, True):
            result = layout.solve(data(make_rows(mirror), bounds=(-120, -30, 120, 30),
                                       max_rounds=1, check_leader_text=True))
            orders[mirror] = [group["neighbor_pairs"][0][0] for group in result["groups"]
                              if group.get("phase") == "leader" and group["neighbor_pairs"]]
        self.assertEqual(orders[False], ["C1", "A1"])
        self.assertEqual(orders[True], ["C1", "A1"])

    def test_three_rounds_rebuild_pairs_and_resolve_a_new_non_neighbor_conflict(self):
        rows = [
            row("A", -.741596978108543, .20261741271695577, width=6.483669763843382),
            row("B", -.39791350985711293, -.20426843595218092, width=6.776117260558581),
            row("C", 3.150137455703593, -4.5156194953569475, width=6.792167825651991),
        ]
        result = layout.solve(data(rows, max_rounds=3, check_leader_text=True))
        self.assertLessEqual(result["round_count"], 3)
        self.assertTrue(all("word_pairs" in r and "leader_pairs" in r for r in result["rounds"]))
        # The remaining crossing is leader-to-leader, which stays diagnostic only.
        self.assertFalse(layout._trigger_pairs(
            result["rows"],
            {r["id"]: layout._geometry(r, r["chosen_length"], r["translation"]) for r in result["rows"]},
            result["clearance"]))

    def test_extension_budget_is_shared_between_rounds_and_translation_is_cumulative(self):
        a = row("A", -2., width=100.)
        b = row("B", -1., width=100.)
        a["height"] = b["height"] = 100.
        result = layout.solve(data([a, b], bounds=(-100, -50, 200, 200), max_rounds=3,
                                   max_extensions=2, check_leader_text=True))
        self.assertLessEqual(result["extensions_used_by_id"]["A"], 2)
        self.assertEqual(result["extensions_used_by_id"]["A"], 2)
        self.assertEqual(result["extensions_used"], sum(result["extensions_used_by_id"].values()))
        attempted = [x["length"] for x in next(r for r in result["rows"] if r["id"] == "A")["attempts"]
                     if x["phase"] == "extend"]
        self.assertEqual(attempted, [15., 20.])
        # Cumulative offsets are based on the last accepted location and are never reset.
        attempts = next(r for r in result["rows"] if r["id"] == "A")["attempts"]
        translations = [x["translation"] for x in attempts if x["phase"] == "translate"]
        self.assertEqual(len(translations), len(set(map(tuple, translations))))

    def test_no_conflict_stays_still_and_road_side_rejects_wrong_side(self):
        solo = row("solo", 0.)
        clean = layout.solve(data([solo], check_leader_text=True))
        self.assertEqual(clean["rows"][0]["points"],
                         [clean["initial_points"]["solo"][k] for k in ("a", "b", "c")])
        self.assertEqual(clean["round_count"], 1)
        self.assertEqual(clean["stop_reason"], "no_geometry_change")
        wrong = row("wrong", 0.)
        wrong["road_side"] = {"point": [0., 0.], "normal": [0., 1.], "min_text_distance": 0.}
        with self.assertRaisesRegex(ValueError, "initial callout violates road_side"):
            layout.solve(data([wrong], check_leader_text=True))

        right = row("right", 0.)
        right["road_side"] = {"point": [0., 0.], "normal": [1., 0.], "min_text_distance": 2.}
        valid = layout.solve(data([right], check_leader_text=True))
        geometry = layout._geometry(valid["rows"][0], valid["rows"][0]["chosen_length"],
                                    valid["rows"][0]["translation"])
        self.assertTrue(all(p[0] >= -layout.EPS for p in (geometry["a"], geometry["b"], geometry["c"])))
        self.assertGreaterEqual(min(p[0] for p in list(geometry["rect"].exterior.coords)[:-1]), 2.)


    def test_same_height_projection_equals_endpoint_left_right_order(self):
        result = layout.solve(data([row("left", -1.), row("right", 1.)]))
        self.assertEqual(result["groups"][0]["neighbor_pairs"], [["left", "right"]])
        self.assertAlmostEqual(result["projection_metadata"]["by_id"]["left"]["x_ref"],
                               result["initial_points"]["left"]["a"][0])

    def test_right_abc_stops_at_c_then_moves_a_after_b_still_overlaps_a(self):
        # Near-horizontal valid obtuse rays keep labels at overlapping heights.
        ux = (1. - .01 ** 2) ** .5
        direction = (ux, -.01)
        a = row("A", -2., direction=direction, width=10.)
        b = row("B", -1., direction=direction)
        c = row("C", -.5, direction=direction)
        result = layout.solve(data([a, b, c]))
        by = {r["id"]: r for r in result["rows"]}
        self.assertEqual(result["groups"][0]["neighbor_pairs"], [["B", "C"], ["A", "B"]])
        self.assertEqual(by["B"]["chosen_length"], 15.)
        self.assertEqual(by["A"]["chosen_length"], 25.)
        # Rebuild rectangles from returned geometry, independently of solver helpers.
        def text_rect(item, source):
            _, tail, corner = item["points"]
            return box(min(tail[0], corner[0]), tail[1] + source["gap"],
                       max(tail[0], corner[0]), tail[1] + source["gap"] + source["height"])
        clearance = data([])["clearance"]
        self.assertGreaterEqual(text_rect(by["B"], b).distance(text_rect(by["C"], c)), clearance)
        initial_a = result["initial_points"]["A"]
        initial_a_rect = box(min(initial_a["b"][0], initial_a["c"][0]),
                             initial_a["b"][1] + a["gap"],
                             max(initial_a["b"][0], initial_a["c"][0]),
                             initial_a["b"][1] + a["gap"] + a["height"])
        self.assertLess(text_rect(by["B"], b).distance(initial_a_rect), clearance)
        self.assertGreaterEqual(text_rect(by["A"], a).distance(text_rect(by["B"], b)), clearance)
        a_attempt = next(x for x in by["A"]["attempts"] if x["phase"] == "extend" and x["passed"])
        self.assertEqual(a_attempt["checked_neighbor"], "B")

    def test_left_open_is_mirror(self):
        result = layout.solve(data([row("A", -3., direction=(-.6, -.8), sign=-1),
                                    row("B", -1., direction=(-.6, -.8), sign=-1),
                                    row("C", 1., direction=(-.6, -.8), sign=-1)]))
        self.assertEqual(result["groups"][0]["neighbor_pairs"], [["B", "A"], ["C", "B"]])

    def test_horizontal_parallel_projection_is_manual_without_division(self):
        nearly_horizontal = (1., 5e-9)
        result = layout.solve(data([row("A", 0., direction=nearly_horizontal), row("B", .1, direction=nearly_horizontal)]))
        self.assertEqual(result["groups"][0]["status"], "manual_horizontal_ray")
        self.assertEqual(set(result["manual_ids"]), {"A", "B"})
        self.assertIsNone(result["projection_metadata"]["by_id"]["A"]["x_ref"])

    def test_nonparallel_conflict_component_is_manual(self):
        result = layout.solve(data([row("A", 0., direction=(.6, -.8)), row("B", .2, direction=(.8, -.6))]))
        self.assertEqual(result["groups"][0]["status"], "manual_nonparallel")
        self.assertEqual(set(result["manual_ids"]), {"A", "B"})
        self.assertTrue(all(r["chosen_length"] == r["length"] for r in result["rows"]))

    def test_mixed_opening_valid_obtuse_rays_are_manual(self):
        result = layout.solve(data([row("right", 0., direction=(.6, -.8), sign=1),
                                    row("left", 12., direction=(-.6, -.8), sign=-1)]))
        self.assertEqual(result["groups"][0]["status"], "manual_mixed_opening")
        self.assertEqual(result["groups"][0]["neighbor_pairs"], [])
        self.assertEqual(set(result["manual_ids"]), {"right", "left"})

    def test_equal_reference_projection_is_manual_not_id_tiebroken(self):
        result = layout.solve(data([row("A", 0., 0.), row("B", .75, -1.)]))
        self.assertAlmostEqual(result["projection_metadata"]["by_id"]["A"]["x_ref"],
                               result["projection_metadata"]["by_id"]["B"]["x_ref"])
        self.assertEqual(result["groups"][0]["status"], "manual_tied_projection")
        self.assertEqual(result["groups"][0]["neighbor_pairs"], [])
        self.assertEqual(set(result["manual_ids"]), {"A", "B"})

    def test_fallback_uses_last_inbounds_ray_and_target(self):
        tiny = {"kind": "polygon", "points": [[-.1, -.1], [.1, -.1], [.1, .1], [-.1, .1]]}
        result = layout.solve(data([row("A", 0., direction=(.8, -.6), target=tiny),
                                    row("B", .05, direction=(.8, -.6), target=tiny)],
                                 bounds=(-2, -10, 13, 5), max_extensions=4))
        moving = next(r for r in result["rows"] if r["id"] == "A")
        self.assertEqual(moving["chosen_length"], 10.)
        self.assertEqual(moving["translation"], [0., 0.])
        self.assertIn("A", result["manual_ids"])
        self.assertTrue(any("anchor_outside_target" in x["reasons"] for x in moving["attempts"] if x["phase"] == "translate"))

    def test_failed_fallback_keeps_last_successfully_extended_inbounds_ray(self):
        ux = (1. - .01 ** 2) ** .5
        direction = (ux, -.01)
        tiny_a = {"kind": "polygon", "points": [[-.1, -.1], [.1, -.1], [.1, .1], [-.1, .1]]}
        result = layout.solve(data([row("A", 0., direction=direction, width=20., target=tiny_a),
                                    row("B", .1, direction=direction, width=20.)],
                                   bounds=(-5, -10, 35, 5)))
        moving = next(r for r in result["rows"] if r["id"] == "A")
        self.assertEqual(moving["chosen_length"], 15.)
        self.assertEqual(moving["translation"], [0., 0.])
        self.assertEqual(moving["status"], "failed")
        self.assertTrue(any(x["phase"] == "extend" and x["length"] == 15. and not x["passed"]
                            and "pair_text_clearance" in x["reasons"] for x in moving["attempts"]))
        self.assertTrue(any(x["phase"] == "extend" and "outside_frame" in x["reasons"]
                            for x in moving["attempts"]))

    def test_singletons_and_line_background_conflicts_are_diagnostic_only(self):
        obstacle = {"id": "strip", "polygon": [[-40, -.1], [50, -.1], [50, .1], [-40, .1]]}
        result = layout.solve(data([row("solo", 0.)], obstacles=[obstacle]))
        solo = result["rows"][0]
        self.assertEqual(solo["chosen_length"], 10.)
        self.assertEqual(solo["translation"], [0., 0.])
        self.assertEqual(solo["attempts"], [])
        self.assertTrue(result["remaining_conflicts"])
        self.assertIn("solo", result["manual_ids"])

    def test_cli_reads_and_writes_json(self):
        with tempfile.TemporaryDirectory() as td:
            src, dst = Path(td) / "in.json", Path(td) / "out.json"
            src.write_text(json.dumps(data([row("solo", 0.)])), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(MODULE), str(src), str(dst)],
                                  capture_output=True, text=True, check=True)
            result = json.loads(dst.read_text(encoding="utf-8"))
            self.assertEqual(result["rows"][0]["id"], "solo")
            self.assertIn('"status": "solved"', proc.stdout)

    def test_batch_pages_scope_duplicate_ids_independently(self):
        result = layout.solve({"pages": [data([row("same", 0.)]), data([row("same", 1.)])]})
        self.assertEqual(result["summary"]["page_count"], 2)
        self.assertEqual([p["rows"][0]["id"] for p in result["pages"]], ["same", "same"])

    def test_strict_obtuse_validation_rejects_horizontal_dummy_angle(self):
        with self.assertRaisesRegex(ValueError, "strictly obtuse"):
            layout.solve(data([row("bad", direction=(1., 0.))]))

    def test_initial_target_bounds_and_nonfinite_reference_are_rejected(self):
        outside_target = {"kind": "polygon", "points": [[10, 10], [20, 10], [20, 20], [10, 20]]}
        with self.assertRaisesRegex(ValueError, "initial anchor is outside target"):
            layout.solve(data([row("outside-target", 0., target=outside_target)]))
        with self.assertRaisesRegex(ValueError, "initial callout is outside bounds"):
            layout.solve(data([row("outside-bounds", 0.)], bounds=(-2, -2, 5, 5)))
        with self.assertRaisesRegex(ValueError, "must be finite"):
            layout.solve(data([row("bad-reference", 0.)], y_ref=float("nan")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
