#!/usr/bin/env python3
"""Generate README.md and data/benchmarks.csv from scripts/data.py.

Never edit README.md by hand: it is derived. Edit scripts/data.py and re-run
    python3 scripts/build.py
"""
import csv
import datetime as dt
import sys

sys.path.insert(0, "scripts")
from data import BENCHMARKS, SECTIONS  # noqa: E402

REVIEWED = "2026-08-31"

ACTION_BADGE = {
    "L0": "![L0][l0-badge]",
    "L1": "![L1][l1-badge]",
    "L2": "![L2][l2-badge]",
    "L3": "![L3][l3-badge]",
    "L4": "![L4][l4-badge]",
}

SECTION_INTRO = {
 "reasoning":
   "Does the system know how the physical world behaves? These are almost all **L0/L1**: no action, no "
   "state change, cheap to run. They are the right first filter for a perception-reasoning backbone and the "
   "wrong evidence for a claim about control.",
 "worldmodel":
   "Generative models judged as predictors of physical futures. An agentic system uses these as its "
   "imagination; a high score means plausible rollouts, not a usable policy. Judging is the weak link - "
   "most rely on human raters or a VLM judge, so read the judge's human-agreement number before trusting a "
   "leaderboard.",
 "spatial":
   "Metric and relational grounding: where things are, in whose frame, and how far. This is the capability "
   "that most often silently bottlenecks a downstream manipulation policy, and it is measurable at **L0** "
   "cost.",
 "eqa":
   "The first genuinely agentic family: the question cannot be answered from the initial observation, so the "
   "agent must move to gather evidence. Watch for benchmarks that score the answer only - an agent can guess "
   "correctly without having looked.",
 "planning":
   "High-level decision making with an executable environment underneath. The action space is symbolic or "
   "skill-level, so these isolate the reasoning stack from the controller. This is where most LLM/VLM "
   "agent work is actually evaluated.",
 "manip":
   "Closed-loop control with contact. Success requires a policy, not a plan, and results are sensitive to "
   "controller, camera pose, and seed. Report the number of trials and the evaluation protocol or the number "
   "is not comparable.",
 "nav":
   "Movement through space under a language, image, or category goal. The cheapest closed-loop family, and "
   "the one with the most mature metric discipline (SPL, nDTW) for penalizing right-answer-wrong-route.",
 "loco":
   "Whole-body and high-DoF control. Included because agentic physical AI increasingly assumes a humanoid or "
   "legged base, and because these expose the hierarchy problem: high-level reasoning is useless without a "
   "low-level skill that survives contact.",
 "driving":
   "The most operationally mature physical-AI domain, and the source of the field's best habits: closed-loop "
   "scoring, infraction accounting, and reactive versus non-reactive protocols. Worth reading even if you "
   "never touch a vehicle.",
 "realeval":
   "Infrastructure for measuring policies on hardware. The bottleneck is not the model, it is reset, success "
   "detection, and cross-site comparability. Any claim about a generalist policy eventually has to pass "
   "through this row of the table.",
 "safety":
   "Physical action makes failure irreversible, so refusal and process-level safety are separate axes from "
   "capability. Note that most of these measure whether the agent *does* the unsafe thing, not whether it "
   "*could have known* it was unsafe.",
 "enabler":
   "Simulators, datasets, and frameworks that everything above is built from. They are listed for "
   "navigation, not as evaluations: reporting a number on a held-out split of a training corpus is not a "
   "benchmark result.",
}

HEADER = f"""<div align="center">

# 🦾 Awesome Agentic Physical AI

**A curated, high-signal index of benchmarks for agentic systems in physical AI: physical reasoning, spatial grounding, embodied planning, manipulation, navigation, driving, safety, and real-robot evaluation.**

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
![License: CC0-1.0](https://img.shields.io/badge/license-CC0--1.0-blue.svg?style=flat-square)
![Entries](https://img.shields.io/badge/entries-{len(BENCHMARKS)}-2563EB?style=flat-square)
![Links verified](https://img.shields.io/badge/links-machine--verified-059669?style=flat-square)

</div>

_Last reviewed: {REVIEWED}. Every arXiv ID and URL below is checked by [`scripts/verify.py`](./scripts/verify.py); `README.md` is generated from [`scripts/data.py`](./scripts/data.py) and should not be edited by hand._

> [!IMPORTANT]
> **A physical-AI benchmark is not automatically an agentic benchmark.** A benchmark is agentic to the degree that the system's own decisions change what it observes next. Most published "embodied" numbers come from static question answering, where a wrong answer costs nothing and the next input is fixed in advance. Those results are useful and cheap, but they cannot support a claim about closed-loop competence. This list sorts every entry by exactly that property first.
"""

SCOPE = """## Scope and labels

Four axes. The first is the one people conflate.

### 1. Action involvement (primary axis)

| Label | The agent... | Environment responds? | Typical failure it can expose | What it can never show |
| --- | --- | --- | --- | --- |
| ![L0][l0-badge] | answers about a fixed observation | No | missing physical knowledge, bad spatial grounding | anything about control |
| ![L1][l1-badge] | predicts or generates a future | No | implausible dynamics, wrong causal model | whether a plan is executable |
| ![L2][l2-badge] | emits actions scored against offline data | No | poor action decoding, bad plan structure | recovery from its own mistakes |
| ![L3][l3-badge] | acts in a simulator that steps state | Yes | compounding error, contact failure, dead ends | real-world contact, sensing, and latency |
| ![L4][l4-badge] | acts on real hardware | Yes | everything, expensively | little - this is the ground truth |

The distinction that matters most is **L2 to L3**. An open-loop score is computed against a trajectory the agent did not produce, so it never sees the states its own errors lead to. Every benchmark that crosses into L3 reports large drops for the same checkpoint, and that gap is the compounding-error term, not noise.

### 2. Capability

Physical and causal reasoning · spatial and 3D grounding · long-horizon planning · manipulation and contact · navigation and mobility · whole-body control · human-robot interaction and multi-agent · safety and refusal. Tagged per entry in [`data/benchmarks.csv`](./data/benchmarks.csv).

### 3. Cost to run

Cost is a first-class property here, because it decides how often you can afford to measure - and a benchmark you run once per paper is not a development signal.

| Cost | Means | Order of magnitude for one full evaluation |
| --- | --- | --- |
| `$` | API calls or CPU only | minutes to a few hours; dollars |
| `$$` | Single-GPU simulation | hours; tens of dollars |
| `$$$` | Photorealistic or large-scale parallel simulation | many GPU-hours to GPU-days; hundreds of dollars |
| `$$$$` | Real hardware, human supervision or teleoperation | days to weeks; hardware, lab space, and staff time |

These are order-of-magnitude planning numbers for a single full evaluation pass at the scale the benchmark authors report, not measured billing. Seeds multiply them: a credible `$$` manipulation result needs enough trials per task that the reported standard error is smaller than the effect being claimed, which routinely means 3 to 5 repeats of the whole suite.

### 4. Verifier

What actually produces the score: **exact match / MCQ** (cheap, gameable by format tricks), **programmatic task success** (the gold standard where it exists), **learned or LLM judge** (report human agreement or it is not evidence), **human rating** (expensive, still necessary for generation), **physical measurement** (real hardware).

### Inclusion decision

| Artifact | Included? | Where |
| --- | --- | --- |
| Fixed question set about physics or space, no actions | Yes | L0 sections, labeled as such |
| Generative model scored on physical plausibility | Yes | World models |
| Offline trajectory dataset with a held-out split | Only as an enabler | Datasets and environments |
| Simulator or framework with no canonical task set or metric | Only as an enabler | Datasets and environments |
| Task suite with a stepped environment and a defined success predicate | Yes | The core of this list |
| Real-robot protocol, including remote or distributed evaluation | Yes | Real-robot evaluation |
| Leaderboard with no public tasks, code, or scoring definition | No | - |

Excluded by default: single-paper evaluation sets used only by their authors, benchmarks whose scoring code was never released, and demo videos.
"""

STARTER = """## Start here

Six entries that between them cover the whole action axis, in the order a new project should adopt them.

1. ![L0][l0-badge] **[PhysBench](https://arxiv.org/abs/2501.16411)** - cheapest honest check that your backbone knows any physics at all.
2. ![L0][l0-badge] **[VSI-Bench](https://arxiv.org/abs/2412.14171)** - the spatial-grounding bottleneck, measurable before you own a robot.
3. ![L2][l2-badge] **[Embodied Agent Interface](https://arxiv.org/abs/2410.07166)** - decomposes decision making into four modules and returns an error taxonomy instead of one number.
4. ![L3][l3-badge] **[LIBERO](https://arxiv.org/abs/2306.03310)** - separates spatial, object, goal, and long-horizon shift, so a regression tells you *which* kind of generalization broke.
5. ![L3][l3-badge] **[BEHAVIOR-1K](https://arxiv.org/abs/2403.09227)** - full-physics, house-scale, long-horizon; where planning and control stop being separable.
6. ![L4][l4-badge] **[AutoEval](https://arxiv.org/abs/2503.24278)** - unattended real-robot evaluation; the only way L3 numbers stay honest.

For sim results intended to predict real performance, add **[SIMPLER](https://arxiv.org/abs/2405.05941)** (calibrated real-to-sim) and **[COLOSSEUM](https://arxiv.org/abs/2402.08191)** (which perturbation actually breaks the policy).
"""

FOOTER = """## Choosing a benchmark

- **Evaluating a VLM backbone for a robot stack?** Start L0: PhysBench, VSI-Bench, ERQA, RoboSpatial. If it cannot answer where an object is relative to the gripper, the control results will not save it.
- **Evaluating a planner or an LLM agent loop?** L2/L3 with module-level error reporting: Embodied Agent Interface, EmbodiedBench, PARTNR, LoTa-Bench.
- **Evaluating a VLA policy?** L3 with an explicit generalization structure: LIBERO, COLOSSEUM, GemBench, VLABench - then SIMPLER or RobotArena ∞ before claiming real-world transfer.
- **Claiming a generalist policy?** L4 is not optional: AutoEval, RoboArena, RoboChallenge, HomeRobot OVMM.
- **Long-horizon, house-scale, multi-agent?** BEHAVIOR-1K, PARTNR, Habitat 3.0.
- **Deploying anything near people?** SafeAgentBench and IS-Bench for hazardous instructions, MSSBench for context-dependent risk at L0, SafeVLA for the safety-utility trade-off, RoboPAIR and Embodied Red Teaming for adversarial pressure. Report refusal separately from success.
- **Humanoid or legged base?** HumanoidBench and LocoMuJoCo in sim, Humanoid-Gym for measured zero-shot transfer, BEHAVIOR Robot Suite for real whole-body tasks.

## What a convincing agentic physical-AI evaluation should report

- **The action level, stated explicitly.** An L0 or L2 number presented as evidence of embodied competence is the single most common overclaim in this field.
- **Trials and variance.** Success rate over how many episodes, how many seeds, and the standard error. Manipulation results with one seed are anecdotes.
- **The unseen split, named.** Unseen instructions, objects, scenes, or embodiments are four different claims; say which one was held out.
- **The verifier.** If a model judges, report its agreement with humans on this task distribution, not on the paper it came from.
- **Compute and wall-clock.** GPU-hours, API cost, and human supervision time. A method that needs a 10x budget for a 2-point gain should have to say so.
- **The sim-real relationship.** If the claim is about the real world, report either real trials or a calibrated real-to-sim evaluator, and the measured correlation.
- **Failures, not just successes.** Which stage failed - grounding, planning, or control - and the recovery behaviour after the first mistake.
- **Safety and refusal, separately.** A policy that completes hazardous instructions faster is not a better policy.

## Known gaps

Places where the benchmark landscape is thin, listed as open work rather than complaint.

- **Cross-embodiment evaluation.** Data pooling across embodiments is far ahead of evaluation across embodiments; there is no widely accepted protocol for scoring one policy on multiple robot morphologies.
- **Persistent, multi-session agents.** Almost everything here resets between episodes. Physical agents that accumulate a map, a skill library, and preferences over weeks are barely measured.
- **Cost-normalized leaderboards.** Almost no benchmark reports score per GPU-hour or per dollar, which makes scaling-based gains indistinguishable from method gains.
- **Human-in-the-loop and interruption.** Handover, correction mid-task, and graceful stopping are common in deployment and rare in benchmarks.
- **Long-tail failure and irreversibility.** Success rate treats all failures alike; dropping a plate and pausing are not the same outcome.
- **Judge reliability under distribution shift.** VLM judges are increasingly load-bearing in this list, and their agreement with humans is usually measured once, on the benchmark's own distribution.

## Related collections

- [Embodied AI Paper List](https://github.com/HCPLab-SYSU/Embodied_AI_Paper_List) - broad embodied-AI survey repository and reading list.
- [Awesome Embodied Robotics and Agent](https://github.com/zchoi/Awesome-Embodied-Robotics-and-Agent) - LLM/VLM-driven embodied agents and robotics papers.
- [Awesome Vision-Language-Action Models](https://github.com/yueen-ma/Awesome-VLA) - VLA architectures, data, and evaluation.
- [Awesome LLM Robotics](https://github.com/GT-RIPL/Awesome-LLM-Robotics) - long-running index of language models in robotics.
- [Awesome World Models](https://github.com/LMD0311/Awesome-World-Model) - world-model papers spanning driving, robotics, and video generation.
- [Awesome Recursive Self-Improvement](https://github.com/pinkbubblebubble/awesome-rsi) - the format this list follows, for self-improving agent systems.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) first. Entries are added to [`scripts/data.py`](./scripts/data.py), not to `README.md` - a pull request that edits the generated file will be asked to move the change. Every entry must state its action level, cost tier, and verifier, and must pass `python3 scripts/verify.py`.

## License

[CC0-1.0](./LICENSE). The linked works belong to their respective authors.

<!-- Shared badge definitions -->

[l0-badge]: https://img.shields.io/badge/L0-passive-64748B?style=flat-square
[l1-badge]: https://img.shields.io/badge/L1-predict-0EA5E9?style=flat-square
[l2-badge]: https://img.shields.io/badge/L2-open--loop-7C3AED?style=flat-square
[l3-badge]: https://img.shields.io/badge/L3-closed--loop_sim-2563EB?style=flat-square
[l4-badge]: https://img.shields.io/badge/L4-real_robot-DC2626?style=flat-square
[code-badge]: https://img.shields.io/badge/Code-181717?style=flat-square&logo=github&logoColor=white
[project-badge]: https://img.shields.io/badge/Project-0EA5E9?style=flat-square&logo=googlechrome&logoColor=white
[dataset-badge]: https://img.shields.io/badge/Dataset-FFD21E?style=flat-square&logo=huggingface&logoColor=111827
"""


def primary(b):
    if b.get("url"):
        return b["url"]
    if b.get("arxiv"):
        return f"https://arxiv.org/abs/{b['arxiv']}"
    return b.get("project") or b.get("code")


def links(b):
    out = []
    if b.get("code"):
        out.append(f'[![Code][code-badge]]({b["code"]} "Code")')
    if b.get("project"):
        out.append(f'[![Project][project-badge]]({b["project"]} "Project")')
    if b.get("data"):
        out.append(f'[![Dataset][dataset-badge]]({b["data"]} "Dataset")')
    return " ".join(out)


def action_cell(b):
    return " ".join(ACTION_BADGE[a] for a in b["action"].split("/"))


def build_readme():
    parts = [HEADER, ""]
    toc = ["## Contents", "", "- [Scope and labels](#scope-and-labels)", "- [Start here](#start-here)"]
    for key, title in SECTIONS:
        anchor = title.lower().replace(",", "").replace("(", "").replace(")", "").replace(" ", "-")
        toc.append(f"- [{title}](#{anchor})")
    toc += [
        "- [Choosing a benchmark](#choosing-a-benchmark)",
        "- [What a convincing agentic physical-AI evaluation should report](#what-a-convincing-agentic-physical-ai-evaluation-should-report)",
        "- [Known gaps](#known-gaps)",
        "- [Related collections](#related-collections)",
        "- [Contributing](#contributing)",
        "",
    ]
    parts.append("\n".join(toc))
    parts.append(SCOPE)
    parts.append(STARTER)

    for key, title in SECTIONS:
        rows = [b for b in BENCHMARKS if b["section"] == key]
        parts.append(f"## {title}\n\n{SECTION_INTRO[key]}\n")
        parts.append("| Benchmark | Venue | Action | Cost | Verifier | Scale | What it measures |")
        parts.append("| --- | --- | :-: | :-: | --- | --- | --- |")
        for b in rows:
            name = f'[{b["name"]}]({primary(b)})'
            lk = links(b)
            if lk:
                name = f"{name} {lk}"
            parts.append(
                f'| {name} | {b["venue"]} | {action_cell(b)} | `{b["cost"]}` | '
                f'{b["verifier"]} | {b["scale"]} | {b["desc"]} |'
            )
        parts.append("")

    parts.append(FOOTER)
    return "\n".join(parts)


def build_csv():
    cols = ["section", "name", "venue", "action", "cost", "verifier", "scale", "caps",
            "arxiv", "url", "code", "project", "data", "desc"]
    with open("data/benchmarks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for b in BENCHMARKS:
            row = []
            for c in cols:
                v = b.get(c, "")
                if c == "caps":
                    v = "; ".join(v)
                if c == "url" and not v:
                    v = primary(b)
                row.append(v)
            w.writerow(row)


if __name__ == "__main__":
    open("README.md", "w").write(build_readme())
    build_csv()
    print(f"README.md + data/benchmarks.csv written ({len(BENCHMARKS)} entries, {dt.date.today()})")
