"""Behavior checks for the Agent geometry reviewer; no CAD side effects."""
import copy
import unittest

from review_layout import review


def polygon(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def row(rid="A", dx=0, dy=0):
    return {"id": rid, "leader": [[dx, dy], [dx + 3, dy - 6], [dx + 11, dy - 6]],
            "text_box": polygon(dx + 3, dy - 5.5, dx + 11, dy - 4),
            "target": {"kind": "point", "point": [dx, dy]}}


def plan(*rows):
    return {"schema": "callout-review-v1", "coordinate_space": "frame-local",
            "units": "metres", "callouts": list(rows or [row()]), "clearance": .1}


class ReviewTests(unittest.TestCase):
    def test_soft_frame_is_warning_but_actual_clipping_is_conflict(self):
        data = plan(); data["inner_frame"] = {"polygon": polygon(-2, -7, 9, 2), "evidence": "visual_checked"}
        result = review(data)
        self.assertEqual(result["geometry_conflicts"], [])
        self.assertIn("outside_preferred_inner_frame", [x["reason"] for x in result["warnings"]])
        data["visible_polygon"] = polygon(-2, -7, 9, 2)
        self.assertIn("outside_supplied_visible_polygon", [x["reason"] for x in review(data)["geometry_conflicts"]])

    def test_collision_with_fixed_old_group_is_checked_and_input_unchanged(self):
        data = plan(row(), dict(row("old", dx=2), fixed=True)); before = copy.deepcopy(data)
        result = review(data)
        self.assertIn("text_text_candidate", [x["reason"] for x in result["geometry_conflicts"]])
        self.assertEqual(data, before)

    def test_road_text_keepout_allows_outgoing_leader(self):
        data = plan(); data["keepouts"] = [{"id": "road", "polygon": polygon(-2, -2, 4, 2)}]
        self.assertEqual(review(data)["geometry_conflicts"], [])
        data["keepouts"][0]["applies_to"] = "both"
        self.assertIn("leader_keepout_candidate", [x["reason"] for x in review(data)["geometry_conflicts"]])

    def test_point_anchor_cannot_move_without_revalidation(self):
        r = row(); r["target"]["point"] = [1, 0]
        self.assertIn("anchor_outside_supplied_target", [x["reason"] for x in review(plan(r))["geometry_conflicts"]])

    def test_crossing_detected_even_without_overlapping_text(self):
        r = {"id": "B", "leader": [[6, 0], [3, -4], [-5, -4]],
             "text_box": polygon(-5, -3.5, 3, -2)}
        self.assertIn("leader_crossing", [x["reason"] for x in review(plan(row(), r))["geometry_conflicts"]])

    def test_angle_and_horizontal_are_independent(self):
        r = row(); r["leader"][2] = [-5, -6]
        self.assertIn("bend_not_strictly_obtuse", [x["reason"] for x in review(plan(r))["geometry_conflicts"]])
        r = row(); r["leader"][2][1] += .3
        self.assertIn("tail_not_frame_horizontal", [x["reason"] for x in review(plan(r))["geometry_conflicts"]])

    def test_steep_own_leader_uses_own_gap_not_neighbor_clearance(self):
        r = row(); r['leader'] = [[0, 0], [3, -30], [11, -30]]
        r['text_box'] = polygon(3, -29.625, 11, -28)
        self.assertNotIn('self_leader_text_candidate', [x['reason'] for x in review(plan(r))['geometry_conflicts']])
        r = row(); r['text_box'] = polygon(2, -5.5, 10, -4)
        self.assertIn('self_leader_text_candidate', [x['reason'] for x in review(plan(r))['geometry_conflicts']])

    def test_reserved_scale_does_not_resize_or_claim_auto_support(self):
        data = plan(); data["scale"] = {"denominator": 1000, "sizing_mode": "preserve_native"}
        before = copy.deepcopy(data)
        self.assertEqual(review(data)["geometry_conflicts"], [])
        self.assertEqual(data, before)
        data["scale"]["sizing_mode"] = "auto"
        with self.assertRaises(ValueError): review(data)

    def test_missing_coverage_is_disclosed(self):
        r = row(); r.pop("target")
        result = review(plan(r))
        self.assertIn("viewport_clipping", result["not_checked"])
        self.assertIn("anchor_target_not_supplied", [x["reason"] for x in result["warnings"]])

    def test_bad_coordinates_and_mixed_space_fail_closed(self):
        for change in ("space", "nan", "duplicate", "polygon"):
            data = plan()
            if change == "space": data["coordinate_space"] = "WCS"
            elif change == "nan": data["callouts"][0]["leader"][0][0] = float("nan")
            elif change == "duplicate": data["callouts"].append(row())
            else: data["callouts"][0]["text_box"] = [[0, 0]] * 4
            with self.assertRaises(ValueError): review(data)


if __name__ == "__main__":
    unittest.main()
