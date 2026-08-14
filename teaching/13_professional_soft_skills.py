# # Section 13: Professional / Soft Skills

# Not code — these are the habits and templates that senior engineers use
# day to day. Copy-paste and adapt these directly.

# ## Pull Request Description Template

# ```
# ## What
# One or two sentences: what does this change do?

# ## Why
# What problem does it solve, or what need does it address?
# (Link an issue/ticket if one exists.)

# ## How
# Brief notes on the approach, especially anything non-obvious.

# ## Testing
# How did you verify this works? (unit tests added, manually tested X flow, etc.)

# ## Screenshots (if UI-facing)
# ```

# ## Code Review — Giving Feedback

# | Bad | Good |
# |---|---|
# | "this is wrong" | "This raises `BookNotFoundError`, but the route only catches `ValueError`, so it'll 500 instead of returning a 404. Want to add `except BookNotFoundError` too?" |
# | "why did you do it this way" | "Curious about the reasoning here — was there a reason to avoid the existing `BookRepository` instead of querying Mongo directly?" |
# | "no" | "This works, but it'll break if `items` is empty — worth adding a guard clause?" |

# Rules of thumb:
# - Comment on the **code**, not the person ("this function" not "you").
# - Distinguish blocking issues from nitpicks — prefix optional ones with
#   "nit:" so the author knows what's required vs. suggested.
# - Ask questions when the intent is unclear, rather than assuming a mistake.
# - Approve with comments when the issues are minor — don't block on style.

# ## Code Review — Receiving Feedback

# - Treat every comment as "this bug got caught before a user hit it" —
#   that's a win, not a criticism of you personally.
# - If you disagree, explain your reasoning once, calmly, with specifics.
#   If the reviewer still disagrees, default to their call unless it's
#   clearly wrong — reviews aren't a negotiation to "win."
# - The engineers who get the MOST review comments over a career are
#   often the most senior ones — they just fix things fast and move on.

# ## Estimating Work & Communicating Uncertainty

# - Never give a single number for anything non-trivial. Give a range and
#   say what the range depends on:
#   > "Probably 2-3 days, could stretch to a week if the Mongo migration
#   > needs a schema change too — I'll know more after looking at the
#   > existing indexes tomorrow."
# - Flag risk EARLY. "This might slip" on day 1 is useful; "this slipped"
#   on the deadline is not.
# - It's fine to say "I don't know yet, let me spend an hour investigating
#   before I commit to a number."

# ## Incident Postmortem Template (blameless)

# ```
# # Incident: [short title]
# Date: YYYY-MM-DD
# Duration: [start] - [end]
# Severity: [e.g. P1 — full outage / P2 — degraded / P3 — minor]

# ## Summary
# One paragraph: what happened, what was the user-facing impact.

# ## Timeline
# - HH:MM — first alert / first report
# - HH:MM — root cause identified
# - HH:MM — mitigation applied
# - HH:MM — fully resolved

# ## Root Cause
# What actually caused it, technically. Not "who caused it."

# ## What Went Well
# (There's always something — fast detection, good communication, etc.)

# ## What Went Wrong
# Be specific and honest. This section is about the SYSTEM, not a person.

# ## Action Items
# - [ ] Concrete fix, with an owner and a deadline
# - [ ] Monitoring/alerting gap to close
# - [ ] Follow-up so this class of bug can't recur
# ```

# The word "blameless" matters: a postmortem that assigns personal blame
# teaches people to hide mistakes instead of surfacing them fast — which
# makes the NEXT incident worse, not better.

# ## Mentoring

# - When someone asks a question you know the answer to, ask "what have
#   you tried so far?" before answering — often they'll solve it
#   mid-explanation, which teaches more than the answer would.
# - Review junior code with the SAME rigor as senior code, but explain the
#   "why" more, not just the "what." A comment like "this could be a race
#   condition — two requests could both read `available=True` before
#   either writes `False`" teaches a concept; "fix this" doesn't.
# - Pair on hard bugs instead of just fixing them yourself and moving on —
#   slower once, faster every time after for the whole team.
