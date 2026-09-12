---
name: audit-anything
description: Audit a thing (a deliverable, a document, code, a report, a config, a checklist) or an action (something an agent or a person did - an overreach, a bypassed guard, an unauthorised change) and come out with a verdict, not a list of observations. Use when asked to audit, review, verify, second-check, sign off, decide whether something was acceptable, or work out whether it was worth it. Covers scoping, an evidence hierarchy, three tracks (thing / action / judgement), verdict tiers, and the auditor's own self-audit. Not for style or taste calls, and not a substitute for running the tests.
license: CC-BY-NC-SA-4.0
version: 1.0.0
---

# audit-anything

**Core rule:** an audit is not error-hunting, it is judgement. A finding that only says "this is wrong" is still an observation. It becomes an audit when it also answers **what it was for, what it caused, and whether it was worth it.**

Judgement does not improve by writing finer rules. It improves by looking back at cases. This file is a procedure plus a place to keep those cases; it is not a scale that weighs for you.

## 0. Four things to settle before auditing

1. **What kind of audit.** A *thing* (is it right, is it worth it), an *action* (should it have been done, and why), or a *judgement* (does the chain from evidence to conclusion hold - a research report, a classification, a recommendation). The three ask different questions; they are separated below.
2. **For whom, and why.** To decide, to backfill, to classify, or to decide whether to continue. The purpose sets the shape of the verdict. If it goes to a decision-maker, the first sentence is the conclusion.
3. **How deep.** Probability of error × cost of error. Audit everything in the high×high cell. **Anything where a single failure alone exceeds the tolerable line gets a full pass** - irreproducible material, handoffs between people or systems, irreversible actions. Everything else is sampled or skipped. Depth is the only knob an auditor controls; do not leave it at "medium" for everything.
4. **Who audits whom.** The author cannot audit their own work. A self-check along the same chain of reasoning is labelled *self-check* and does not count as an audit. If the same model audits its own output, use a separate session or a different model and say so in the report. Cross-vendor review beats same-vendor self-review by default.

## 1. Evidence rules

- **Hierarchy.** Re-running it yourself > reading the original yourself > third-party records (logs, receipts, ledgers) > the subject's own account with corroboration > the subject's own account alone. "I asked and it said it did" is *insufficient evidence*, not *verified*.
- **Claims against touchpoints.** For every "done / verified / passed", find the touchpoint: a file, an exit code, a number, a screenshot, a receipt. No touchpoint means unverified claiming to be verified. Multiple independent sources beat one; two sources derived from the same origin are not independent.
- **Confidence in plain words, with a range.** Almost impossible / unlikely / even / likely / almost certain - one vocabulary per report, and each term paired with a sentence on where the evidence and the uncertainty come from. When neither the source nor the content can be verified, write "cannot be established", not "pending verification".

## 2. Auditing an action

**Track first: disclosure is the entry ticket.** Said at the time → *learning track*: read motive and situation generously, scrutinise the system. Discovered later → *accountability track*: scrutinise the objective consequences and whether it was concealed. Disclosure decides the track; it does not cancel the harm.

**Three tests** - run them on every overreach, boundary crossing or unilateral act before classifying it:
1. **Purpose.** For the task, for oneself, or to save effort.
2. **Consequence.** Did it touch what the guard protects? Reversible or not? Who was harmed?
3. **Disclosure.** Was it said at the time? And did the behaviour change after it was reported - reported but repeated is normalised deviance; reported and stopped is the case blameless review protects.

All three pass → no case; record it as a positive (exposing a flawed rule is a contribution). Consequence over the line, or repeated after reporting → case. Self-serving and concealed → serious.

**Three supporting tests**
- **Substitution.** Would an equally capable operator in the same situation have done the same? Yes → the system, rule or situation is sick; fix the rule. No → now it can be individual responsibility.
- **Necessity and proportion.** Was the task genuinely impossible without breaking the rule? Was there no less damaging alternative? Was the harm avoided greater than the harm caused? Was the situation not of the actor's own making? All four must hold before "broke the rule but justified" applies. Good intent alone does not excuse; it still lands on what was done and what it caused.
- **Signs of a broken rule.** One rule bypassed "of necessity" by several people repeatedly points at the rule, not the people - change the rule, do not add punishment. One person, one time, no pressure → individual.

**Depth.** A single bounded overreach: five whys is enough. Once it is *not the first time*, or it touches guard placement and permissions, switch to a control-structure view: did whoever designed this guard anticipate this situation, and which link in the enforcement-and-feedback loop failed?

Audit the action, not the person. The report says which step, what was done, whether there was authorisation, and whether it is reversible. It does not describe character.

## 3. Auditing a thing

1. **Ask for intent and the acceptance line first.** What did the author set out to do, and what counts as done? If there is no acceptance standard, write one before auditing. The right to call for review belongs to the author: answer what they asked first, then add your own findings - and keep "here is a problem" separate from "here is how you should fix it".
2. **Four questions.** What is new here (relative to what exists)? Does it hold (logic, evidence, actually run)? Is it clearly said? Is it worth it?
3. **Split the columns.** Factual items - numbers, paths, exit codes, whether the output matches the spec - can be machine-checked. Taste, sound, trade-offs and whether to keep going: mark them as belonging to a human's eyes, and do not rule on them.
4. **Approve and reject.** If it is clearly better than the status quo, approve it; imperfection is not a reason to stall. Mark non-essential comments as minor. A rejection must be actionable - say what is missing and what minimum evidence would count as fixed. **Point at the problem and stop; fixing belongs to the author** unless you were explicitly asked to fix it.
5. **Scale turning point.** Past roughly four hundred lines or an hour, an audit degrades into browsing. Split large objects: structure first, then paragraphs, then proofreading - and never polish sentences in a section you are about to cut.
6. **Two layers of acceptance.** Is this particular thing right (scenario level)? And does it pass the floor every deliverable must pass - written to disk, correct paths, reproducible, no known blockers? Acceptance counts only what landed, never what was described.

## 4. Auditing a judgement

A report, a classification, a recommendation: the question is whether the chain from evidence to conclusion holds.

1. **Pull the chain.** Take the three strongest claims, trace each to its touchpoint (the quoted text, the number, the file) and open one yourself. A broken touchpoint drops the whole report one tier.
2. **Find the opponent.** What other explanation does the same evidence support? Did the report consider it? An unconsidered rival explanation matters more than a found error.
3. **Delete the template.** Cover every paragraph a template could have generated. Does what remains still stand, and how much is left? Nothing left means form-filling, not judgement.
4. **Test the kill condition.** Is the stated weakness a condition that could actually be falsified, or a decorative hedge ("we will revise if contrary evidence appears")? A kill condition that cannot be operated is not a kill condition.

**For any tidy-up, migration or restructuring deliverable, add one question:** for every item that was moved or changed, was it checked for inbound references (aliases, hooks, indexes, other systems' configs) *before* the change? A handover note with no "references checked" line is a defect.

## 5. Verdicts

- **Four tiers:** clean pass / conditional pass (write the "except for ...") / not credible as a whole (problems too broad, conclusions void) / **cannot determine** (say plainly that the evidence is not obtainable; do not manufacture a pass or a fail).
- **For actions, four levels:** violation of a stated rule (cite it) / dereliction (unverified claimed as verified, unilateral action, a bypassed guard whose consequence crossed the line, sitting idle) / blemish / nothing found (state what was and was not checked).
- **One line per finding:** level | object:location | defect | touchpoint | disposition (something executable now, never "be careful next time").
- **The hardest calls:** even on an overall pass, list separately the call that was hardest to make, why it was singled out, and how it was resolved.
- **End with three things:** the auditor's own kill condition (what evidence would overturn this verdict), what was not audited, and known blind spots.

## 6. The auditor's self-audit

Run this before issuing anything:

- Am I anchored on the first number or phrasing I saw? Did I look for counter-evidence - did I list candidate explanations and falsify them, or pick a story and collect support?
- **Is this a situational failure or a character failure?** Not asking defaults to blaming the person; it is the most common self-deception in auditing behaviour.
- Is this hindsight? A judgement written after the outcome was known must say so.
- Am I favouring what agrees with me, what is longer, or what sounds authoritative?
- **Delay the overall verdict.** Score evidence strength, situational attribution, consequence and disclosure separately; only then combine. Intuition goes last, not first.
- **Conclusion and reasons land together.** A conclusion without written reasons is an unfinished judgement.

## 7. Case review - the only way this gets better

Every verdict carries a falsifiable confidence. When the outcome is later knowable, record one line: date, object, verdict, confidence, what actually happened. A hit rate you can see beats another round of rule-writing.

## Boundaries

- Taste, aesthetics and creative trade-offs belong to a human's eyes. An audit can say a claim has no touchpoint; it cannot say a piece is beautiful.
- This is not a substitute for running the tests. If something can be checked by executing it, execute it.
- An audit produces a report. It does not edit the audited files.

---

Licensed CC BY-NC-SA 4.0 — free to use, adapt and share for non-commercial purposes, with attribution, under the same licence. Commercial use is not permitted. Distilled from real audits of AI-produced work; the case log is where it gets sharper, so keep one.
