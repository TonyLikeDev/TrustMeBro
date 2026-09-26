# Plan: <project title>

<One paragraph: what this project is, which source documents this plan merges (if any), and how the schedule works. Every phase lists what to build, what to measure, and what to write down, so the final deliverables are assembled from the phase outputs instead of written from scratch.>

---

## 0. Decisions

<!-- Every conflict between the sources, and every choice made up front. Later changes go in Deviations, not here. -->

| Topic | What the sources say / options | Decision | Why |
| :--- | :--- | :--- | :--- |
| | | | |

---

## 1. Objectives

**General objective.** <one sentence>

**Specific objectives.**
1. ...

**Deliverables.** <software, report, paper, demo video, slides...>

---

## 2. Technical design

<Core idea, architecture, key formulas or interfaces, directory layout, tech stack. Enough detail that a phase item can point to it.>

---

## 3. Research framing

<!-- Research projects only; delete this section otherwise. -->

### 3.1 Research questions
- **RQ1.** ...

### 3.2 Contributions to claim
1. ...

### 3.3 Metrics
| Metric | Measures | Tool |
| :--- | :--- | :--- |

### 3.4 Planned experiments and ablations
- ...

### 3.5 Evaluation data
<What it is and when it is frozen. Never change it after freezing, so all tables stay comparable.>

### 3.6 Experiment logging rules
- Every run writes `experiments/<date>_<name>/` with its config, results, outputs, and a log of seed, device and git commit.
- Fixed seeds; headline numbers are mean and standard deviation over 3 seeds.
- Never overwrite an experiment folder; add a new one.

---

## 4. Environments

<!-- Only if the project runs on more than one machine or the hardware matters. -->

| Profile | Machine | Role |
| :--- | :--- | :--- |

---

## 5. Schedule (<N weeks | N milestones>)

Each phase has **Build**, **Measure**, **Write**, and **Exit criteria**. "Write" items go straight into the report. A phase with nothing real to measure or write drops that part.

### Week 1: <title>
**Build**
- ...

**Measure**
- ...

**Write**
- ...

**Exit criteria**: ...; ...; ...

---

## 6. Report outline

<!-- Only if there is a report or paper: map each section to the phases that produce it. -->

| Section | Source phases | Key figures and tables |
| :--- | :--- | :--- |

---

## 7. Risks and fallbacks

| Risk | Signal | Fallback |
| :--- | :--- | :--- |

---

## 8. Deviations

<!-- Dated, user-approved changes to this plan: `- YYYY-MM-DD: change, reason`. The sections above are never rewritten to record progress. -->
