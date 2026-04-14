# Project Proposal

**Project Name:** Agent Crucible

**Team Members:** Muhammad Shayaan, Mohammad Farzam Ghouri

**One-Line Description:** An education-first red-team and blue-team framework for LLM safety testing, with turn-by-turn attack visualization, configurable defenses, and a structured evaluation suite.

**Abstract:** We are building an educational testing framework where red-team agents execute adaptive multi-turn jailbreak attacks against blue-team safety guardrails, and every step is visualized and explained. Unlike existing enterprise tools (PyRIT, DeepTeam, garak) that are designed for security engineers and have steep learning curves, our framework is education-first with real-time visualization and attack/defense explanations. Students building LLM applications often skip safety testing due to tool complexity, and existing frameworks produce raw output that is difficult to interpret without prior security knowledge. Our framework makes adversarial AI testing accessible for students learning security concepts by making failures visible, explainable, and measurable. A structured evaluation suite measures attack success rates, detection latency, and over-refusal across eight attack families, giving students a clear picture of where their system is vulnerable and why.

**Target Customer/User:** CS students in AI/GenAI courses building LLM-powered projects, junior developers learning LLM security, instructors designing hands-on safety lab exercises, and researchers needing quick and interpretable safety baselines.

**Impact:** Educational impact through hands-on adversarial AI learning with reduced barriers to entry, allowing students to run structured safety tests and receive interpreted results rather than raw logs. Secondary impact for small organizations and researchers who need a lightweight safety validation tool without the overhead of enterprise-grade frameworks. The key differentiator over existing tools is that attack and defense outcomes are explainable and measurable, not just recorded.

**Technical Implementation:** Red-team uses custom adaptive agents with eight attack strategies (direct jailbreak, roleplay jailbreak, policy confusion, instruction override chain, context poisoning, benign-malicious sandwich, system prompt probing, multi-step escalation) and a converter pipeline for prompt transformation. Blue-team uses a layered detector architecture with a rule-based policy engine, Meta LlamaGuard, and NVIDIA NeMo Guardrails, supporting five configurable policies and five response actions (allow, block, redact, safe_rewrite, escalate). Backend is FastAPI with a JSON-backed run store. Frontend is React with a real-time turn-by-turn visualization, a structured 20-case evaluation suite with post-run analysis, and a freeform sandbox for manual testing. LLM providers are abstracted and currently support Groq (Llama 3) and a mock provider for offline testing.

**Schedule & Milestones:**

**Week 1: Foundation & Architecture** - Project setup, literature review, system design, provider abstraction layer, baseline tooling

**Week 2: Red-Team Agent** - Eight multi-turn adaptive attack strategies with converter chains and objective-based scoring

**Week 3: Blue-Team Agent** - Rule detector, LlamaGuard integration, NeMo Guardrails integration, five-policy registry, dry-run mode

**Week 4: Integration & Optimization** - Unified pipeline, full turn tracing, run persistence, performance testing

**Week 5: Evaluation Suite** - 20-case dataset across eight attack families including benign control cases, post-run analysis with per-category and per-difficulty breach rates, over-refusal measurement, and blue-team miss rate

**Week 6: Advanced Features** - Multi-provider support, configurable detector thresholds, policy tuning, benchmark regression tracking

**Week 7: Visualization** - Turn-by-turn sequential reveal of attacker prompt, blue-team verdict, and model response; blue-team evidence drawer; live benchmark panel; evaluation insights section

**Week 8: Testing & Refinement** - End-to-end testing, eval suite stop and restart, UI polish, bug fixes

**Week 9: Documentation, demo, and final presentation**
