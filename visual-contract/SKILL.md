---
name: visual-contract
description: State the visual contract before designing anything, so a reference image, a bug fix, or the word "modern" cannot quietly overwrite a design language. Use when building or changing a page, poster, deck, long-form layout, portfolio or visual system - especially when the user supplies a screenshot or competitor shot, or asks to "clean it up", "make it modern", "make it look higher-end", or "just fix the overlap". Carries a five-line contract, a reference-image rule, a typography discipline, an anti-slop avoid list, an acceptance checklist and a drift check. Not for dashboards, admin tools, or product pages that should feel friendly and mainstream.
license: CC-BY-NC-SA-4.0
version: 1.0.0
---

# visual-contract

**One line:** a reference image lends you its *structure*, never its *taste* - and "make it modern" is not a mandate to reset the design language.

Most visual drift in AI-assisted design has one of two causes: a screenshot got treated as an aesthetic brief, or a functional request ("fix the overlap", "make it responsive") was read as permission to redesign. This skill stops both by making the agent write down what it is and is not borrowing, before it opens an editor.

## Quick table

| Situation | What to do | Section |
|---|---|---|
| The user supplies a reference image, screenshot, or competitor shot | Borrow structure only (information architecture, interaction, grouping, flow, engineering constraints). Do not borrow colour, type, radius, shadow | 1 |
| The user says "modern", "cleaner", "nicer", "higher-end", "just fix it", "redo it" | These mean structure, function or readability must improve. They do not trigger a style reset. To deviate, say why first and wait | 1 |
| Before touching any design | Write the five-line contract into the reply. A bug-fix job must state "fixing function and structure, not resetting the visual language" | 2 |
| Deciding what this thing should look like | Three sources in order: what was said and shown this turn; the temperature of the material itself; otherwise ask, or ship one small sample first | 3 |
| Laying out | Titles are verdicts. Material is evidence, not illustration. Whitespace under pressure. Never restate what the layout already says | 4 |
| You just produced rounded cards, a purple-blue gradient, decorative English microcopy, or a polite summary paragraph | All on the avoid list. Delete | 5 |
| Before delivery | Ten acceptance questions; if the job involved a reference image, a "modernise", or a bug fix, add the seven drift questions | 6, 7 |
| This skill conflicts with the user, safety, accessibility or correctness | Those win, every time | 8 |

## 1. Reference-image priority

When the user supplies any visual sample, borrow by default:
information architecture, interaction patterns, node relationships, content grouping, flow and disclosure order, engineering constraints (sizes, occlusion, responsive behaviour).

Do **not** borrow by default: palette, type personality, corner radius, shadow and gradient language, soft white card feel, slide-deck flowchart look, consulting-diagram look, friendly-SaaS styling.

Only an explicit instruction - "match this style", "use these colours too" - moves an item from the second list to the first.

These words never trigger a style reset on their own: *modern, nice, like this one, no overlap, interactive, cleaner, higher-end, more like a real tool, just fix it, redo it.* They mean structure, function, readability or completeness should improve. If deviating from the established visual language really is the right call, say why and wait for confirmation.

## 2. The contract

Before any page, HTML, poster, deck, long-form layout, portfolio or image prompt, put this in the reply:

```text
Visual contract
- Aesthetic source:
- Borrowing from the reference:
- Not borrowing from the reference:
- What this change is fixing:
- Explicitly avoiding:
```

For a job that fixes occlusion, interaction, layout bugs or mobile behaviour, the contract must state: **fixing function and structure, not resetting the established visual language.** No contract, no design work.

## 3. Style is not preset

This skill defines no style. No default palette, no default warmth, no motif library, no house look. What a given piece looks like comes from three sources, in order:

1. What was said and shown this turn - a base image outranks a stated intent, which outranks an adjective.
2. The material itself: the subject's temperature, the evidence it carries.
3. Neither available → ask, or ship one small sample and let the answer come from looking at it. Never silently import a style from previous work.

## 4. Layout discipline

- A title is a verdict, not an introduction.
- Images, names, lists, fragments and objects are evidence, not decoration.
- Whitespace should be under pressure, not merely "airy".
- Small English type, stamps, tags, footnotes and captions appear only when they build structure.
- Grouping, numbering, scale, density, order and absence matter more than ornament.
- If the layout already says it, do not restate it in words.
- Never add an element to balance a composition.
- Never explain the design inside the work.

One page, or one slide, usually needs one strong judgement and one set of material that can carry it.

## 5. Avoid list

Friendly-SaaS styling · stacked rounded cards · purple-blue gradients · consulting-firm icon systems · decorative English microcopy · decorative stamps and seals · design-intent captions · explanatory footnotes · taste commentary · a polite closing paragraph · over-explained symbolism · text that apologises for the material · official-looking cultural cliché standing in for cultural taste (ink wash, zen, and emptiness are not a country; a flag palette is not a culture - and the same trap exists in every direction).

## 6. Acceptance checklist

Before delivery, answer each one:
Is there an actual judgement here? Does the material read as evidence or as decoration? Has the surplus explanation been cut? Does the first screen or first page stand up immediately? Is the whitespace under pressure? Are scale, order and density doing work? Do the labels, footnotes, captions and small English type have a structural reason? Can every element answer "why am I here"? Have friendly-SaaS, purple-blue gradients and empty "premium" gestures been avoided? With the explanations removed, does the piece still stand?

## 7. Drift check

If the job involved a reference image, a "modernise", an interaction upgrade, an occlusion or responsive fix, a bug fix, a "redo", a "cleaner" or a "higher-end", add:

- Did a reference image's *visuals* get mistaken for an aesthetic direction?
- Was the established visual language abandoned in order to solve an occlusion or interaction problem?
- Did large white rounded cards, soft gradients, faint grids, pill buttons, slide-deck flowcharts or consulting node diagrams appear?
- Did "modern" turn into friendly-SaaS or a template dashboard?
- Were explanations, captions, decorative tags, English microcopy or meaningless icons added to look finished?
- With the interactivity removed, does the visual judgement still hold?
- Was each functional element translated into the author's structural language, rather than wearing a generic UI skin?

Any of these true: report the drift point first, then correct course. Do not ship the drifted result as the deliverable.

## 8. Priority and tone

This skill never overrides: the user's explicit instruction, file and privacy boundaries, output format limits, readability and accessibility, technical correctness, domain safety requirements.

If the user asks for warm, cute, bright, soft, friendly, playful, corporate or mainstream - give them that. This is a discipline against drift, not a taste to impose.

While it is in force, the reply follows the same rule: judgement first, explanation short, no design-intent essay, no decorative praise; give structure and direction, not mood words; if something is weak, say where it is weak and what to delete.

---

Licensed CC BY-NC-SA 4.0 — free to use, adapt and share for non-commercial purposes, with attribution, under the same licence. Commercial use is not permitted. Written against real drift incidents in AI-assisted design work; if a rule costs you something, change it and say why.
