# Judging Strategy

> Use this document to ensure your project is optimised for maximum score across all four
> judging criteria. Review before building, and again before submitting.

---

## 🏆 The Four Judging Criteria

### 1. Application of Technology (IBM Bob 2.0)
> *"How complete and well thought-out the project is, with a clear application of IBM Bob 2.0."*

**What judges are looking for:**
- Bob 2.0 is genuinely central — not just used for a few autocomplete suggestions
- The project uses advanced Bob features: Agent mode, subagents, parallel tasks, custom modes/rules
- The prototype is functional, not just a concept demo
- Bob's role in the workflow is clearly visible (in demo video and Bob Usage Statement)

**How to maximise this score:**
- [ ] Use **Agent mode** for the core workflow automation
- [ ] Use **subagents** for at least one parallel processing task
- [ ] Create a **custom mode** or **.bob rules file** tailored to your project
- [ ] Show Bob reading, editing, running, and iterating — not just answering questions
- [ ] In your IBM Bob Usage Statement: list specific features, tasks, and outputs
- [ ] Include `bob_sessions/` screenshots showing substantive work, not trivial queries

---

### 2. Presentation
> *"The clarity and effectiveness of the project presentation."*

**What judges are looking for:**
- Video demo is clear, focused, and compelling
- The problem is immediately understood within the first 30 seconds
- The solution is shown working on screen for at least 90 seconds
- Slides are clean and professional
- Narration guides the viewer — don't silently screencast

**How to maximise this score:**
- [ ] Video structure:
  - 0:00–0:30 — Hook: state the painful problem in one punchy sentence
  - 0:30–0:45 — Brief solution overview (visual diagram or slide)
  - 0:45–2:30 — Live demo: show the solution working, narrate what Bob is doing
  - 2:30–3:00 — Before/after impact numbers, call to action
- [ ] Use screen recording with face-cam if possible (more personal)
- [ ] Record at 1080p minimum
- [ ] Do NOT just talk over a static slide for 3 minutes — show the tool running
- [ ] Edit out dead time (waiting for commands to run, etc.)
- [ ] Slide deck: 6–10 slides max, clean design, big numbers for impact metrics

---

### 3. Business Value
> *"The impact and practical value, considering how effectively the solution addresses a high priority issue."*

**What judges are looking for:**
- The problem is real and costly (not a toy/hypothetical)
- Impact is quantified (time saved, errors reduced, steps automated)
- The solution would actually be useful to a real developer team today
- Broad applicability — works on real-world or representative codebases

**How to maximise this score:**
- [ ] Choose a problem that happens **every day** in software teams
- [ ] Quantify the pain: "takes X hours", "X% error rate", "X manual steps"
- [ ] Quantify the solution impact: "reduced to Y minutes", "Y% error reduction"
- [ ] Show the demo on a realistic repo (use a public GitHub project if needed)
- [ ] In the Long Description, explicitly state ROI: "saves ~4 hours per PR review cycle"
- [ ] Make it sound like something a VP of Engineering would fund immediately

---

### 4. Originality
> *"The uniqueness and creativity of the solution and the approach in applying IBM Bob 2.0 to address the stated issue."*

**What judges are looking for:**
- The problem or solution approach is not obvious or generic
- Bob is used in an interesting, non-trivial way
- The combination of features is creative (e.g., actor-critic pattern, multi-agent pipelines)
- Something surprising or impressive happens in the demo

**How to maximise this score:**
- [ ] Avoid the most obvious submission ideas (basic chatbot, simple code completion)
- [ ] Use Bob in an **agentic loop** or **multi-agent pipeline** — not just one-shot Q&A
- [ ] Combine Bob with other tools/MCP servers in an unexpected way
- [ ] Create a novel workflow pattern (e.g., Bob writes tests that prove Bob's own fixes work)
- [ ] Think about edge cases or niche problems that most people haven't addressed
- [ ] The "aha moment" in your demo should make judges think "I didn't know Bob could do that"

---

## 📊 Score Optimisation Table

| What to Do | Criteria Boosted |
|-----------|-----------------|
| Use Agent mode + subagents in parallel | Application of Technology |
| Create custom mode or .bob rules file | Application of Technology |
| Build a functional prototype (not just concepts) | Application of Technology |
| Include bob_sessions/ screenshots of real work | Application of Technology |
| Write specific IBM Bob Usage Statement (500w) | Application of Technology |
| Video: show solution working for 90+ seconds | Presentation |
| Clear narration in video | Presentation |
| Before/after impact metrics in slides | Presentation + Business Value |
| Pick a real, daily developer pain point | Business Value |
| Quantify time/error savings | Business Value |
| Demo on realistic repo/codebase | Business Value |
| Use Bob in an agentic pipeline, not just Q&A | Originality |
| Novel multi-agent workflow | Originality |
| Surprising "aha moment" in the demo | Originality |

---

## 🎬 Video Script Template

```
[0:00 - 0:25] PROBLEM HOOK
"Every developer team loses [X hours/week] to [painful problem].
 [Describe the frustrating manual process in 2 sentences].
 We built [Solution Name] to fix this."

[0:25 - 0:40] SOLUTION OVERVIEW
Show a single diagram slide:
 - Input → IBM Bob 2.0 (Agent mode + subagents) → Output
 - Name the key Bob features being used

[0:40 - 2:30] LIVE DEMO (this is the most important part)
Step 1: Show the broken/painful starting state
Step 2: Trigger the IBM Bob workflow (show Agent mode running)
Step 3: Show subagents spinning up / parallel work happening
Step 4: Show the output / fixed state
Step 5: Show the verification / proof it works

[2:30 - 3:00] IMPACT
"Before: X hours. After: Y minutes."
"Before: Z manual steps. After: fully automated."
"We saved [metric] — here's the Bob session summary showing [N] Bobcoins used."
```

---

## 🔴 Anti-Patterns (Things That Kill Your Score)

| Anti-Pattern | Why It Hurts | Fix |
|-------------|-------------|-----|
| "Bob helped us code this" (generic) | Vague, scores low on Application of Technology | Specify which feature, which task, what exact output |
| Demo is just typing in the chat and reading answers | Not agentic, not impressive | Use Agent mode with actual file edits and command execution |
| Problem is too abstract ("improve productivity") | Low Business Value score | Pick a specific, daily, measurable workflow pain |
| Video is 3 minutes of slides with no live demo | Low Presentation score | Show the tool working on screen for 90+ seconds |
| Used Bob for 2 tasks, manual for everything else | Low Application of Technology | Run the whole workflow through Bob end-to-end |
| Submission last-minute, video shaky | Low Presentation score | Prepare video by Sep 26 to allow for re-recording |
