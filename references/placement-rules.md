# Placement rules

[完整中文规则](placement-rules.zh-CN.md). Preserve the existing algorithm, not a new design.

Use approved frame-local x/y; world Y is not road side. A is anchor, B bend, C tail; opening_sign +1/-1 determines horizontal direction. A→B x shares that sign; the angle at B is strictly 90°–180°. Actual formatted MTEXT width/height, attachment 9 and bottom-right insertion apply to both openings.

Read nearest road centerline P and tangent; choose normal n toward anchor. All leader points stay on that side, diagonal points outward and all text corners stay beyond confirmed edge distance plus margin. Unknown edge/side is not guessed; a local normal does not prove clearance from distant road bends.

Stage 1: fixed connected new-text conflict groups per round, excluding background/leader relationships. Parallel same-opening rays project to common y_ref: x_ref=B.x+(y_ref-B.y)*u.x/u.y. Do not rank by B.x/road distance. Right-opening order right-to-left: keep rightmost C, clear B/C and stop B immediately, then handle A against placed B. Temporary conflict with unprocessed A does not prevent B/C clearing. Mirror for left opening. Mixed openings, nonparallel/near-horizontal rays or tied projection are manual.

Stage 2: process actual leader/other-new-text clearance pairs, not one leader graph. Use opening/projection choice; check both leader/text directions and text clearance. The new-text conflict set may only shrink, never gain pairs. This extra restriction belongs to stage 2, not stage 1's neighbor stop.

Extend by 5, preserving anchor/angle, with five accepted extensions/25 additional units shared across all rounds. Rejected trials do not consume accepted-length budget. Validate frame bounds, target-anchor and road constraints. On failure retain last valid length and try whole-unit horizontal offsets -2,+2,-4,+4,-6,+6 including anchor; never enlarge target to allow movement. In leader stage retain only geometry also preserving no-new-text conflicts.

Stop on clear/no-change/three rounds. Keep last valid geometry, report manual_ids/remaining_conflicts; line-line/background diagnostics do not trigger a fourth round. No all-unit extension, within-stage regrouping, angle changes or budget reset. Configurable script values do not hard-enforce this task policy; Agent checks inputs. Drawing-unit defaults are not paper millimetres.
