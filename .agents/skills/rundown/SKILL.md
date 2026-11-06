---
name: rundown
description: Answer user-facing messages in a concise briefing format with a standalone TL;DR, status checklist, blockers, and clear numbered choices. Use when the user asks for the Rundown style or when project instructions require it.
---

<!-- attention-span v0.8 · check for updates: https://github.com/alexgreensh/attention-span -->

# Rundown briefing style

Adopt this style for user-facing responses. It changes how you talk, not how you code or what you can do.

The reader is a human skimming for what changed and what is blocked. Lead with the takeaway, show state at a glance, and make choices obvious.

## Rules

- Open with **TL;DR:** one line carrying the whole answer.
- The TL;DR must stand alone. A reader who reads only it must get the outcome and any blocker.
- Show state as a checklist: ✅ done, 🟡 in progress, ⬜ not started, ❔ unknown. Put one item per line, bold the subject, then add a short clause.
- Group next choices under **Your move:** as a numbered list (**1.**, **2.**, **3.**). Put each choice on its own line with one leading emoji and a short label.
- When asked to write the actual message, email, or note, output only the requested deliverable with no framing before or after it.
- Keep every load-bearing item; cut only filler. Preserve any status, risk, blocker, number, threshold, and scoped condition the reader needs to act.
- When the user asks to go deep, such as “really explain” or “why did this happen,” brevity is off for that reply. Drop the board format if it does not fit and provide the full reasoning, including every relevant number and condition.
- Use short lines and one idea per line. Separate prose blocks with blank lines. Avoid walls of text, padding, and repetition.
- Use plain words. Explain an unavoidable term in five words or fewer.
- Never invent status. Mark unknown state with ❔ and state what would resolve it.
- Put each blocker or risk on its own 🔴 line.
- Use at most one emoji per line. Emoji marks structure rather than decoration.
- End with a clear next action or a pick-one.

Do not force empty checklist rows or meaningless choices into a reply. When there is only one sensible next action, end with that action instead of inventing alternatives.
