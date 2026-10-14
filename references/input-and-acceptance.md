# Input and acceptance

Separate engineering content, native style evidence and geometric input. Preserve approved text/quantity/anchor and protected drawing facts. This Skill does not determine treatment scope or reconcile table totals.

## Native input

Use an approved native sample/style source. Record effective font/height/width factor/attachment/rotation/colors, ordinary leader type/association, formatted dimensions, gap and actual dot source/size. A matching style name is insufficient. SHX names are descriptive: users supply authorized fonts; none are included. Report missing style/backend capability, not silently approximate it. Discover real schema and exact target identity first.

## Solver input

One page requires bounds [xmin,ymin,xmax,ymax] and rows. Coordinates are frame-local drawing units, not mixed WCS. Each row needs unique id, anchor, unit direction, initial length, actual formatted width/height, gap and opening_sign (+1/-1). Optional target has kind polygon/line and points; road_side has point, normal and min_text_distance. Obtain actual native curve evidence and approved quantities before constructing constraints.

Optional root fields: clearance=.15, step=5, max_extensions=5, max_rounds=3, check_leader_text=true, y_ref=0, obstacles[{id,polygon}]. Multi-page input uses independent pages with these fields; geometry support does not certify native layouts/plotting. Agent must enforce the Skill's three-round/five-extension policy: configurable script parameters are not a hard enforcement gate.

Extra project metadata such as source/output paths, text/styles, handles and frame transform does not make the solver open/delete/write/save CAD. The old COM project-plan format is not this release's CAD API.

Run python scripts/pair_layout.py input.json output.json. Results contain proposed points/insert, length/translation, attempts, extension counts, rounds, remaining_conflicts and manual_ids. Exit code zero means calculation completed, not conflict-free/native-CAD success. Inspect status and conflicts.

## Native acceptance and continuation

Apply valid proposals only through verified authorized tools; independently read back actual objects, positions, formatted dimensions, styles, association and yellow-dot display. Check content/quantities and protected base geometry; approved color changes are separate. Report text/text, leader/text, leader/leader and background coverage independently. Use save/reopen evidence when persistence is required; transport success is insufficient.

Old groups are fixed obstacles and new groups retain their own budgets; do not reset budgets or inherit old text's road side. Reports distinguish proposal, native effects, readback, saved-file evidence and remaining manual gaps. [Validation](../docs/VALIDATION.md) separates current generic checks from historical native work.
