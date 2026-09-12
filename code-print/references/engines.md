# Engine card - what the two scripts do, and what they cost

Parameters live here, not in SKILL.md. Both engines are pure geometry plus SVG filters:
no dependencies, no network, no image generation.

## woodcut.py - line quality

| Function | What it does |
|---|---|
| `noise(seed, harmonics, base)` | Correlated noise (summed sine phases). **Hand tremor must use this** - white noise gives you a digital fringe, not a hand |
| `smooth(ctrl, n, closed)` | Catmull-Rom through hand-placed control points → dense point list. Smooth a closed form before `cut_shape` |
| `cut_stroke(pts, w0, w1, ...)` | Centre line + width envelope → closed outline. Tapering at both ends is the knife entering and leaving; `notches` randomly removes small triangles for chipping |
| `cut_shape(pts, ...)` | Closed form, perturbed along its outward normals |
| `ink_line(pts, w, curve_gain)` | **Width follows curvature**: thick where it turns, thin where it runs. `curve_gain` 0.4-1.0 |
| `limb(p0, p1, w0, w1, bow)` | Tapered limb around a bone. Place joints, then grow flesh - never guess the outline. **Returns `(d, spine_points)`** |
| `coil(x, y, a, s0, turn, ramp, decay, n)` | A spiral. **The `ramp` segment walks straight at constant step**, and only then decays into the coil |
| `ribbon(spine, w0, w1)` | Centre line → tapering closed band (a lock of hair, a wing feather). **Returns points, not a `d`** |
| `scallop(pts, n, depth, keep)` | Edge worked into scales or petals |
| `hatch_field(d, angle, spacing, keep)` | A field of parallel knife lines across a shape's bounding box. Woodcut builds volume with *families of parallel lines*, never scribble. **Returns a list of `d` strings, and does not clip itself** |

### Traps, each one paid for once

- `feDisplacementMap` with `scale > 3` beads the edges. Keep it near 2, with `baseFrequency` 0.016-0.024 - slow is a hand, fast is a fringe.
- **Tapering can only come from geometry; a filter cannot make one.** Do the taper and the chipping in the points, and let the filter do only high-frequency chatter. Two separate layers.
- Hatching that covers everything becomes a zebra and the solid black disappears. Keep it inside 40% of the shadow side.
- Where two forms overlap, cut a paper-coloured gap between them (standard woodcut practice), about 3px. Past 4px it looks like armour plating.
- A coil on a single exponential decay ties "the length thrown out" to "the curl at the end", and no value fixes both. It has to be piecewise.
- Ink bite threshold: `feColorMatrix` alpha bias around −1.78. At −1.5 you get measles.
- **`ribbon()` returns points, not a `d`**. Put it straight into `<path d=...>` and nothing draws - and nothing errors either. Wrap it: `d_of(ribbon(...))`. `limb()` returns a **tuple** `(d, spine)`; take `[0]`. `cut_shape` and `cut_stroke` return a `d` directly.
- **`hatch_field()` returns a list and does no clipping.** Iterate it, and clip the group to the shape: `<g clip-path="url(#shape)">`. Unclipped, the cuts run straight across the sky.
- `limb` thins by about 45% at each end, so shoulder→elbow→wrist leaves gaps at the joints. Pad each joint with a black disc (`cut_shape(ellipse(joint, r≈limb width))`) drawn *under* the limb.
- **Do not draw fingers.** A hand is one closed fist shape, and the object it holds (a bottle, a plate, a gun) says what the hand is doing. Two hands of the same ink overlapping an object become one blob - separate them with the other ink or with paper. Tested three ways on the same subject: every version with finger gaps turned to mud.
- To get a smooth closed line through hand-placed points use `smooth(ctrl, n)` then `cut_shape`. Chaining béziers requires matching tangents by hand, and hand-placed tangents produce corners.

## printlab.py - old printed matter

| Function | What it does |
|---|---|
| `defs(seed, grain, mottle, edge)` | The filter set: rough edge, paper grain, mottling, ink bite |
| `plate(ds, color, dx, dy)` | One colour plate from a list of `d` strings. **The whole character of old printed matter is in those one or two pixels of misregistration** - flatten it and the piece dies |
| `group(markup, dx, dy)` | Same, for markup you built yourself (mixed fills, type) - it leaves your fills alone |
| `svg_document(name, w, h, paper, inner, defs)` | A standalone SVG file, paper rectangle underneath |
| `fur_fast(outline, cx, cy, ...)` | Fur. Five-point tapered slivers - an order of magnitude cheaper than full knife cuts |
| `blob` / `ell` | Wobbled polygon / ellipse |

### Traps

- **Fur is a flow field, not a radial burst.** Put the direction origin at the body centre and you get a dandelion; lift it above the head and the fur sweeps down and out. Wrong direction, and no amount of strands fixes it.
- Light-coloured patches must be drawn **after** the dark blocks, or they are covered and invisible.
- Do not add woodcut tremor to a flat printed piece - the original was clean printing, and the tremor is a mistake in the other direction.
- Whether `fur_fast` gives you bristles or down is three numbers: `w ≤0.7`, length 4-11, group opacity ≤0.6 is down; `w 1.5`, length 9-24, opaque is a porcupine. If the down is not dark enough, do not thicken it - screen the shape underneath.
- Size: full knife cuts for fur reach megabytes and nothing will preview it. Put one colour in one `<g fill>`, round coordinates to integers, and use `fur_fast`.
