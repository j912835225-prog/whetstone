---
name: tame-sprawl
description: Tidy a sprawling system - a skill library, a docs set, a rules or config collection, a prompt library, an over-grown module - without reorganising it into a different mess. Four steps that may not be skipped, a rule for what may be cut, and an acceptance test that is not a file count. Use when asked to clean up, consolidate, reorganise, deduplicate or "there are too many of these now, sort it out". Not for one-off file tidying, and not for refactoring code whose tests are the real authority.
license: CC-BY-NC-SA-4.0
version: 1.0.0
---

# tame-sprawl

**One line:** you cannot tidy a system you have not read, and a system with a generating principle does not need tidying twice.

Most cleanups fail the same way: someone reads the index, invents categories that sound orderly, moves everything into them, and reports "47 files down to 12". Nothing was resolved - the contradictions moved house. These four steps exist to make that outcome impossible.

**One object at a time.** Do not tidy two systems in one pass; the second one is what makes you skip step 1 on the first.

## 1. Traverse

- List every item in the object and **open each one**. Not the index, not the file names - the contents.
- Where an item points at reality (a path, a host, a state, a version), spot-check whether it is still true. Having read it is not having verified it.
- Output: a traversal list, one line per item, saying what that item is.
- Forbidden: concluding anything from the index or directory listing alone.

## 2. Fuse

- Answer, in writing, in one sentence: **what is the generating principle of this pile?** Then group by it. **Seven groups maximum** - if you need more, the principle is wrong, not the limit.
- If you cannot write that sentence, stop and go back to step 1. The inability to state it means you have not read enough, and every category you invent from here will be decoration.
- Pick a shape for the result that matches the material:
  - one item governs the rest → **hoist the governing one**
  - the pile is genuinely several kinds → **split by kind**
  - a hierarchy exists → **outline it**, principle above, items below
  - several items say one thing → **fuse and cut**
  - the whole thing has drifted from its purpose → **return to the original constraint**
  - it is simply too elaborate for what it does → **simplify**, and say what you gave up

## 3. Cut

Only three things may be touched. Anything else stays.

1. **Contradicts the principle** → change it.
2. **Duplicated across two places** → merge into one source; leave a pointer where the other one was.
3. **Belongs to nothing** → report it to the owner for a decision. Do not delete it yourself.

Before changing anything old, decide about backup by one test only: **is there a way back?** Not "is this file old". Content that cannot be regenerated gets backed up; anything reproducible from source does not. Where merges are involved, show the full merged text to the owner before it lands.

Output: a change list - one line per change: type, original, destination, backup location if any.

## 4. Raise the principle, then get out of the way

Write the grouping from step 2 into the object's **index or entry layer, and only that layer**. Do not stamp a category field onto every leaf item. The principle exists so a reader finds things; it does not need to be repeated on each one.

## Acceptance

- Pick any three items at random. Say within ten seconds which part of the principle each one hangs from. Cannot → back to step 2.
- **Never report "N files down to M".** A file count measures deletion, not order. Report instead: how many contradictions were resolved, how many duplicate sources were merged, and where the principle now lives.
- The tidying itself must not leave behind a new permanent file. One report, and it is over.

## Why each step is load-bearing

| Skipped step | What you get |
|---|---|
| 1 Traverse | Categories invented from titles; the contradiction survives inside a tidier folder |
| 2 Fuse | Groups that do not divide anything, so items land in whichever looks closest |
| 3 Cut | Everything preserved and renamed - the mess, reorganised |
| 4 Raise | The principle written everywhere, which means it is enforced nowhere |

## Boundaries

- Code whose tests define correctness is refactoring, not this: let the tests lead.
- One-off file tidying (a downloads folder) does not need four steps.
- This produces a decision about structure. Running the changes is ordinary work, and irreversible ones still need their owner's go-ahead.

---

Licensed CC BY-NC-SA 4.0 — free to use, adapt and share for non-commercial purposes, with attribution, under the same licence. Commercial use is not permitted. The four steps are old (traverse, fuse, cut, raise is a classical Chinese editorial method); the failure modes in the table are contemporary and were paid for.
