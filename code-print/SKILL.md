---
name: code-print
description: Draw printed matter in code instead of generating it - single-ink and two-ink posters, covers, zine pages, tickets, invitations, labels, screenprint and risograph looks, halftone and spot-colour work. Vector out, PDF-ready, type that is never wrong, same input same output. Use when asked for a poster, a cover, a print piece, "draw it yourself", "does this have to be image generation", or when the subject is type, geometry, objects, charts or repeated elements rather than skin, hair and photographic light. Ships two drawing engines, a worked example, and a six-question acceptance test.
license: CC-BY-NC-SA-4.0
version: 1.0.0
---

# code-print

One sheet, one or two plates, one focus, one area of air.

This tool produces **printed matter drawn in code**: vector, exportable to PDF, type that never warps, and the same output from the same input. Its opposite is not "a nice picture" - it is *rolling the dice with an image model*. Image generation draws skin and brushwork; it cannot place a line of type correctly. This draws no skin, but the type is always right and the dimensions are always print-grade.

## What this cuts, and what it does not

**Comes here:** pieces whose subject is type, geometry, object silhouettes, diagrams, pattern, or repeated elements. Also pieces that contain a photograph *used as one halftone block of colour*.

**Does not come here:** pieces whose subject must be photographic - skin, hair, real light, painted brushwork. Use an image model for that.

**Mixed jobs:** get the photographic layer from an image model as one image, then bring it back here and use it **as a plate** - screened to halftone, flattened to one ink, placed in the layout. Type and layout are always drawn in code.

## Work card - eight steps, each with a touchpoint

Do not move to the next step without the touchpoint for the current one.

1. **Look at the source, write three columns.** What is there / what is fixed (change it and the thing dies) / what is *unexpected* - each pointing at something specific (who is in front, what is largest, what is loudest). Write them into the build script's docstring. **No unexpected element found means you have not looked long enough.** Go back.
2. **Write the anchor in one sentence.** It grows out of the unexpected thing, and it must be a claim that could be wrong. A reference sample, if there is one, lends only craft - stock, number of inks, where the type sits. Its composition and language are not yours to copy.
3. **Fill in the recipe** (section 1, every field). Two inks maximum and each gets one written job; the paper gets a job too (the brightest real object in the source becomes paper). One focus. One area of air.
4. **Write a script; do not hand-write SVG.** The engines are in `scripts/` (`woodcut.py`, `printlab.py`; parameters and traps in [references/engines.md](references/engines.md)). Copy the skeleton from `scripts/example_two_ink_poster.py`. Joints before flesh; form right before texture.
5. **Render and look.** `rsvg-convert -z 2 x.svg -o x.png`, then look at it again shrunk to a thumbnail. Fix one problem per round, three to five rounds. **An assertion you have not rendered does not go into the report.**
6. **Answer the six acceptance questions** (section 7). Any you cannot answer sends you back to step 4.
7. **审 - audit the finished piece** (section 8). Only at this step, never before.
8. **Deliver:** the file, one line of recipe (section 6), and one line of self-assessment. No method language in the piece itself.

**Two traps that catch weaker models every time:** ① small type may only carry real facts (a date, a place, a speed) - invented catalogue numbers, factory names and process names are decoration, cut every one; ② putting everything from the source into the frame makes an illustration, not a poster - delete everything that is not load-bearing, then add back one item if the anchor has stopped standing up.

## 1. Start by solving the job into a recipe

Before a line of code:

```
subject:    one recognisable person / object / place / idea - exactly one
intent:     announce / observe / notify / record / invite / specimen
text:       given text is changed by nobody; if none is given, write 2-8 characters
            and then lock it
format:     poster / cover / zine page / ticket / sleeve / label
size:       section 6; default A5 portrait 559x794
inks:       primary hex + (secondary hex, or none)
division:   what the primary ink does, what the secondary does - one sentence each.
            Cannot say it? Then do not use a second ink
layout:     one of the six families in section 3
focus:      exactly one. Name the object
air:        one area. Name where it is
paper:      25-55% of the sheet
texture:    0-2 items (contemporary) / 2-3 items (aged, archival, handmade)
```

**Put the recipe and the three columns in the build script's docstring**, not in a separate file: when you change a parameter and re-run, the judgement is in front of you.

**The same input must solve to the same recipe.** Do not change ink, layout or proportion for novelty. This is the only thing that makes the tool reproducible by someone else - the recipe is an interface, not a style note.

## 2. Ink

### Six to start with

Do not memorise a swatch book. These six are a starting hand; when the subject is not in the table, mix your own with the method below.

| Name | hex | Eats |
|---|---|---|
| indigo | `#1B3FA0` | city, knowledge, music, night, technology |
| cinnabar | `#C1352C` | announcements, performance, markets, public events |
| pine | `#0A7A50` | plants, ecology, bookshops, archives |
| ochre | `#B45A33` | food, travel, objects, summer |
| ink | `#2A2A2D` | architecture, photography, research, restraint |
| vine violet | `#5E3C6B` | literature, film, privacy, late night |

### Mixing your own

1. Take the primary from **the real object**: the largest area of colour in the source, pulled to where print can reach it - L between 0.35 and 0.55, C pushed to 0.13-0.20. A spot colour is saturated, not grey.
2. Derive the secondary in oklch: **same L, same C, hue rotated 150-210°.** This is an *opposing* colour, not a colour scheme - it has to look like another plate, not like a tint of the first.
3. There is no third ink. A dark produced by overprinting two plates does not count as one. Paper is not an ink.

### Division of labour

Write down what each plate is responsible for before you draw: *indigo = subject and title; cinnabar = the date and one circle, nothing else.*
The primary takes 70-85% of the inked area, the secondary 15-30%. **The secondary may never be sprinkled evenly across the page** - it concentrates on one event, or it does not get used.
With one ink, build levels by density: solid, 70% screen, 30% screen, fine line. One ink gives four levels, which is enough.

### Paper

Paper has to be visible. Three stocks: neutral white `#FAFAF7` (contemporary, crisp, colour subjects), cool grey `#EAEAE6` (architecture, technology, ink-based), warm white `#F4F0E7` (food, travel, tactile, archival).

**Paper gets a job too**: the brightest real object in the source (a face, a neck, metal, a title) becomes paper - that is, a hole cut in the ink plate. Title type set in paper colour over a solid plate *comes out of the sheet*. If you need a third grey inside two inks, screen the plate with a dot pattern; do not add an ink.

**Screening does not mean ageing.** Yellowing, foxing, distressed borders and retro type only appear if someone asked for them.

## 3. Plates and layout

### Six families - pick one, do not mix

- **Image-dominant** - one object or halftone crossing at least one edge, the title pressed onto it or hard against it. Image 60-80%.
- **Type-dominant** - the type is the subject; one sentence governs the page and a small image holds it down. Type 55-80%.
- **Specimen** - one to three cut-out objects floating on the sheet, numbered small type walking around them, a large area of air. Objects 45-65%.
- **Notice** - one rule splits the page: title above, facts below (time, place, price), thin column rules, small date. Image 45-65%.
- **Object field** - one object repeated at different sizes, crops and angles, forming rhythm, with one space left for the title.
- **Overprint** - each plate carries its own content, crossing in a chosen area. The crossing is deliberate, not a page-wide mess.

### One focus, one area of air

This is the single most important rule here.

**There is exactly one focus**, and it is one of these five: oversized type / an extreme crop / one enormous object / one concentrated overprint collision / one abnormal scale relation.
**There is exactly one area of air**, and it must be noticeably quieter than the focus - not evenly distributed emptiness, but one large area that is quiet.

The test: shrink the piece to a thumbnail. The focus must be recognisable instantly and the air must still read as air. If not, it has no focus - go back; do not patch it with small type.

**Looseness is not weakness.** Looseness is unevenly distributed energy: one place bold, everything else released. Making every element small, pale and tasteful is flat, not loose.

### Ranking, on the page, is three things

Whatever ranks first among your load-bearing material takes **the largest size, the frontmost layer, and the only crop**. All three to one object and the focus appears; split across three objects and you have three focuses, which is none. Whatever was nearer the camera stays in front - do not invert depth to make the "main character" clearer. Inverted scale and inverted depth are often exactly the unexpected thing, and therefore the focus.

### Three ways to die

- Title left, a complete photograph right, a gutter between them. The safe layout, and the dullest.
- Everything centred and evenly spaced, like a template.
- The area of air filled with decorative small type, small icons and small notes.

## 4. Chinese typography

This chapter is specific to CJK work. The Latin skeleton vocabulary (serif / sans / condensed) does not transfer: Chinese has no condensed display tradition, and its tension comes from **weight, tracking, vertical setting, Song-against-Hei, traditional-against-simplified, and measure**.

| Skeleton | Typeface | When | How it gets tension |
|---|---|---|---|
| **Song** | 宋体 / Source Han Serif | literature, observation, privacy, tea and objects | size up, leading tight, break lines on breath not grammar |
| **Hei** | 黑体 / PingFang Semibold-Heavy | announcements, performance, markets, public | tracking closed until the strokes nearly touch |
| **Kai** | 楷体 | handwritten feel, invitations, private notes | interjections only; never carries dates or places |
| **Vertical** | Song or Hei | covers, one-word titles, poems | vertical setting *is* the one disruption; do not add a second |
| **Type-as-object** | huge Song or Hei | when the type is the subject | 12-20x the small type; one character may be cropped off the page |

### Hard rules

- **One display skeleton plus one functional face** (small type, numerals, Latin) per sheet. A third voice is allowed only as a single handwritten interjection.
- **One scale jump, and make it violent**: the largest type is 5-12x the smallest. Less than that is not hierarchy.
- **Do not apply Latin tracking logic to Chinese display type.** Latin looks expensive opened up; Chinese looks powerful closed up. Opened-up Chinese display type looks like a slide deck.
- **Punctuation:** delete full stops in titles. Delete commas where a space or a line break will do. Keep quotation and title marks where the content needs them.
- **Numerals and Latin in a monospace or tight sans**, contrasting in material with the Chinese face. It is a free layer of hierarchy.
- **Short beats long.** A title is 2-8 characters. Longer than that is body copy.

### Type and export traps

For print, the exported file *is* the piece, so never gamble on a font being present:

- **CJK display type uses system stacks**: `"Songti SC", "STSong", "Noto Serif CJK SC", serif` / `"PingFang SC", "Heiti SC", "Noto Sans CJK SC", sans-serif` / `"Kaiti SC", "STKaiti", serif`. Screen and export then agree.
- **Webfonts only for Latin display**, and always with a fallback of similar width (Bebas Neue → Impact; Instrument Serif → Georgia).
- Leave 10% headroom on display sizes for the fallback.
- **Lock the width of Latin display type**: `<text textLength="650" lengthAdjust="spacing">` cannot overflow the sheet whatever font substitutes. That is harder than headroom.
- **To hand type to geometry operators** (distortion, knock-out, cutting): use `fontTools` to extract a single face from the `.ttc`, then `SVGPathPen` + `TransformPen` to get outlines directly in your target coordinate system.

## 5. Print texture - paste-ready SVG

Texture happens only in the **reproduction layer**. It may not change the composition, move the type, or shift the subject.

Contemporary editorial work: 0-2 items. Aged, archival or handmade work: 2-3. **The same recipe uses the same values** - do not re-randomise per run.

```html
<defs>
  <!-- paper grain: on the bottom-most paper layer -->
  <filter id="paper" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="7" result="n"/>
    <feColorMatrix in="n" type="saturate" values="0" result="g"/>
    <feComponentTransfer in="g" result="soft"><feFuncA type="table" tableValues="0 0.09"/></feComponentTransfer>
    <feBlend in="SourceGraphic" in2="soft" mode="multiply"/>
  </filter>

  <!-- dry ink break-up: for display type and solids; never for small type -->
  <filter id="dryedge" x="-3%" y="-3%" width="106%" height="106%">
    <feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves="2" seed="7" result="w"/>
    <feDisplacementMap in="SourceGraphic" in2="w" scale="4" xChannelSelector="R" yChannelSelector="G"/>
  </filter>

  <!-- halftone: use as a fill; dot density is ink density -->
  <pattern id="dots60" width="8" height="8" patternUnits="userSpaceOnUse">
    <circle cx="4" cy="4" r="2.6" fill="INK"/>
  </pattern>
  <pattern id="dots30" width="8" height="8" patternUnits="userSpaceOnUse">
    <circle cx="4" cy="4" r="1.7" fill="INK"/>
  </pattern>
</defs>
```

- **Misregistration:** translate the secondary plate's group by `transform="translate(2.5,-1.5)"`. Two to four pixels. More than that is a misprint.
- **Overprint:** `style="mix-blend-mode: multiply"` on both plate groups. The dark where they cross is not a third ink.
- **Paper coming through from inside:** cut shapes out of the ink (a `fill="paper"` shape, or a `<mask>`) so paper becomes a form *inside* the image, not just the border. This is the line between "printed" and "filled with colour".
- **One handmade gesture:** a drawn circle, an arrow, a registration cross, one crooked label - **one family only**. Two kinds of scribble and it is a scrapbook.

### If you add a hand-drawn library (Rough.js and similar)

- **Scale law:** divide every hand-drawn parameter by the group's transform scale (`roughness/k`, `strokeWidth/k`, `hachureGap/k`, `fillWeight/k`). Without it, scaled-up strokes become caterpillars and scaled-down ones become wire. This applies to any texture under any scaling.
- **Give fill and stroke different roughness:** a solid fill at high roughness self-intersects, the nonzero rule cancels it, and the shape comes out hollow. Fill `0.7/k`, stroke `1.3/k`. Hatched fills do not have this problem.
- Draw the object anatomically correctly first (a bow needs a string and recurve, an urn needs its handles), then add the hand. Line quality lives in the reproduction layer; it cannot rescue a wrong skeleton.

## 6. Output

### Sizes (96px/inch, use directly as canvas w/h)

| Piece | px |
|---|---|
| A5 portrait (default poster) | 559 × 794 |
| A4 portrait | 794 × 1123 |
| Letter portrait | 816 × 1056 |
| Square (sleeve/sticker) | 800 × 800 |
| Vertical cover (4:5) | 720 × 900 |
| Ticket strip | 900 × 380 |

Body copy from 12pt (16px). Legal small type no smaller than 12px. No rule thinner than 1px, or it will not print.

### Deliver with one line of recipe

`inks: indigo #1B3FA0 + cinnabar #C1352C (primary: subject and title / secondary: the date only) · layout: type-dominant · focus: oversized title crossing the object · paper 38%`

## 7. Acceptance - six questions, answered while looking at the render

1. At thumbnail size, **is the focus recognisable instantly**? Is the air still a quiet area?
2. How many inks can you count? **More than two is a reject** (overprint darks do not count).
3. Does paper come through from **inside** the image, or is it only a border?
4. Is the largest type at least **5x** the smallest?
5. Did it hit any of the three ways to die?
6. Is the given text intact - **not one character changed, cut, or squeezed out of shape**?

Six questions you can answer with your eyes. Do not write a twenty-item checklist; anything you cannot judge by looking does not belong on it.

## 8. 审 - the audit, at the last moment before delivery

Open this **only** when the piece is finished and about to go out, or when it comes back with "too literal", "not as good as the last one", "you let yourself off". **Do not open it while drawing** - work with the judgement in your hand, and what comes out is the judgement, not the picture.

Audit the finished piece against four negations, from the calligrapher Fu Shan (1607-1684) - the sharpest anti-slick standard anyone has written:

> 宁拙毋巧，宁丑毋媚，宁支离毋轻滑，宁直率毋安排
> *Rather clumsy than clever. Rather ugly than ingratiating. Rather broken-apart than slick. Rather blunt than arranged.*

- **Clever** - is there a move here whose only job is to be admired? The clever move is the first thing to cut.
- **Ingratiating** - does any part of this exist to be liked? This is the hardest of the four to see in your own work, because it feels like care.
- **Slick** - is every transition smooth, every edge resolved, nothing snagging? Then nothing is happening.
- **Arranged** - is the composition balanced because the subject demanded it, or because you tidied it?

Then count which weapons you actually drew: colour beyond form / material / crop / layer order / negative space. If only one or two came out of the scabbard, the piece is thinner than it looks.

Finish with a number: how many tenths is this, and which tenth is missing? A self-assessment with no missing tenth is not a self-assessment.

## 9. Files here

```
code-print/
  SKILL.md                            this file
  references/engines.md               every parameter and every trap in the two engines
  scripts/woodcut.py                  line quality: taper, hand tremor, nicks, hatching
  scripts/printlab.py                 old printed matter: misregistration, grain, mottle, fur
  scripts/example_two_ink_poster.py   a worked piece - copy this skeleton
  scripts/selftest.py                 proves the engines still draw
```

```bash
python3 scripts/selftest.py                     # verify the toolchain
python3 scripts/example_two_ink_poster.py       # writes example_two_ink_poster.svg
rsvg-convert -z 2 scripts/example_two_ink_poster.svg -o poster.png
```

Pure geometry plus SVG filters. No dependencies, no image generation, no network.

---

Licensed CC BY-NC-SA 4.0 — free to use, adapt and share for non-commercial purposes, with attribution, under the same licence. Commercial use is not permitted. The recipe-before-drawing idea, the per-plate job rule and one-focus-one-area-of-air were taken from the open-source [mono-color-skill](https://github.com/yanliudesign/mono-color-skill) and then rewritten; its fixed swatch book, English-default copy, twenty-item quality gate and image-prompt-compiler route are deliberately not followed here, because what this tool ships is a printing plate, and on a plate the type has to be right.
