---
title: Agent Crucible — Project Feedback
source: Course review session
---

# Agent Crucible — Project Feedback

**Team:** Muhammad Shayaan, Mohammad Farzam Ghouri
**One-liner:** Educational red-team/blue-team sandbox for LLM safety testing.

---

## Summary

Red-team agents run adaptive multi-turn jailbreak attempts, blue-team modules apply configurable defenses, and the system visualizes turn-by-turn what happened and why. The value prop is a learning-first safety testing environment that makes failures explainable and measurable.

---

## Closest Existing Work (Idea-Similarity Check)

- **PyRIT** — open-source red-teaming framework (Microsoft)
- **Promptfoo** — red teaming docs and tooling
- **NVIDIA garak** — LLM vulnerability scanner

---

## What's Strong

The educational-first angle is the right wedge. Students skip safety testing because existing tools are heavy, and this framework tries to make red/blue interactions visible and understandable.

---

## Where This Looks Too Similar to Existing Work

Red-teaming frameworks already exist and are actively maintained (PyRIT, Promptfoo, garak). Shipping "a framework that runs jailbreak prompts" is rebuilding the wheel.

---

## How to Build a Moat

Your moat has to be **pedagogy + visualization**:

- Turn-by-turn attack intent, defense decision, and explanation of why something succeeded or failed
- "Lab exercises" that students can complete
- A plugin system that makes writing new attacks/defenses part of the learning experience

---

## Evaluation & Responsible AI Must-Haves

Measure both learning value and technical value:

| Metric | Description |
|--------|-------------|
| Time-to-first-test | How fast can a student run their first test? |
| Attack family coverage | Which attack families are covered? |
| Success rate | How often do attacks succeed? |
| Detection latency | How quickly does the blue team catch attacks? |
| Over-refusal rate | How often does the blue team block benign inputs? |

Show at least one multi-turn attack where the visualization explains the failure better than existing tools.

---

## Action Items for Next Iteration

- [ ] Narrow to **4–6 attack strategies** + **3 defense patterns** and make them excellent
- [ ] Build the timeline visualization early — it's the primary differentiator
- [ ] Add a plugin template so new attacks/defenses are straightforward to implement
- [ ] Benchmark against a baseline workflow (e.g., a PyRIT run) to prove usability/insight advantage
