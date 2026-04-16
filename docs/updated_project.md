# Project Proposal

**Project Name:** Agent Crucible

**Team Members:** Muhammad Shayaan, Mohammad Farzam Ghouri

**One-Line Description:** An education-first red-team and blue-team framework for LLM safety testing, with turn-by-turn attack visualization, configurable defenses, and a structured evaluation suite.

**Abstract:** We are building an educational testing framework where red-team agents execute adaptive multi-turn jailbreak attacks against blue-team safety guardrails, and every step is visualized and explained. Unlike existing enterprise tools (PyRIT, DeepTeam, garak) that are designed for security engineers and have steep learning curves, our framework is education-first with real-time visualization and attack/defense explanations. Students building LLM applications often skip safety testing due to tool complexity, and existing frameworks produce raw output that is difficult to interpret without prior security knowledge. Our framework makes adversarial AI testing accessible for students learning security concepts by making failures visible, explainable, and measurable. A structured evaluation suite measures attack success rates, detection latency, and over-refusal across eight attack families, giving students a clear picture of where their system is vulnerable and why.

**Target Customer/User:** CS students in AI/GenAI courses building LLM-powered projects, junior developers learning LLM security, instructors designing hands-on safety lab exercises, and researchers needing quick and interpretable safety baselines.

**Impact:** Educational impact through hands-on adversarial AI learning with reduced barriers to entry, allowing students to run structured safety tests and receive interpreted results rather than raw logs. Secondary impact for small organizations and researchers who need a lightweight safety validation tool without the overhead of enterprise-grade frameworks. The key differentiator over existing tools is that attack and defense outcomes are explainable and measurable, not just recorded.

**Technical Implementation:** Red-team uses a native function-calling agentic loop (Groq/OpenAI tool use API, no LangChain) with eight attack strategies and a converter pipeline for prompt transformation. The agent reasons between steps, selects converters, and adapts across turns rather than executing a fixed pipeline. Blue-team uses a layered detector architecture with a rule-based policy engine, supporting six configurable policies (including medical prescription guidance) and five response actions (allow, block, redact, safe_rewrite, escalate). Policies are defined in `config/policies.json` and loaded at runtime without code changes. Backend is FastAPI with a JSON-backed run store. Frontend is React with real-time turn-by-turn visualization, a structured evaluation suite, a freeform sandbox, and a lab exercise system. Lab exercises are stored as individual JSON files in a `labs/` directory and served via `GET /api/v1/labs` — adding a new lab requires only dropping a JSON file, no code changes. Labs support a scripted mode where the instructor pre-defines the exact attacker prompt and target response per turn, bypassing both LLMs to guarantee a reproducible outcome for classroom use. LLM providers are abstracted and currently support Groq (Llama 3) and a mock provider for offline testing.

**Schedule & Milestones:**

**Week 1 (Mar 2–9): Foundation & Architecture** - Project setup, literature review, system design, provider abstraction layer, baseline tooling

**Week 2 (Mar 9–16): Red-Team Agent** - Agentic tool-calling loop, eight attack strategies, converter pipeline, objective-based scoring

**Week 3 (Mar 16–23): Blue-Team Agent** - Rule detector, six-policy registry, five response actions (allow, block, redact, safe_rewrite, escalate), dry-run mode, runtime policy configuration via JSON

**Week 4 (Mar 23–30): Pipeline & Evaluation Suite** - Unified red/blue pipeline, full turn tracing, run persistence, 20-case evaluation dataset across eight attack families, post-run analysis with breach rates and over-refusal measurement

**Week 5 (Mar 30–Apr 6): UI & Live Attack Lab** - Real-time turn-by-turn visualization, blue-team evidence drawer, turn detail panel, live benchmark section, multi-run history

**Week 6 (Apr 6–13): Sandbox & Lab Exercises** - Freeform attack sandbox mode, lab exercise system with file-based plugin architecture, scripted turn mode for reproducible classroom labs, six built-in lab exercises across beginner/intermediate/advanced levels

**Week 7 (Apr 13–20): Testing & Refinement** - End-to-end testing, policy tuning, eval suite regression, UI polish, bug fixes
