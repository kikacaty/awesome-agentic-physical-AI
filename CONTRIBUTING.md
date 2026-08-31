# Contributing to Awesome Agentic Physical AI

Thank you for helping keep this a precise, high-signal index.

## The one rule that is different here

`README.md` and `data/benchmarks.csv` are **generated**. Add or edit entries in
[`scripts/data.py`](./scripts/data.py) and run:

```bash
python3 scripts/verify.py   # arXiv titles resolve, every URL returns 200
python3 scripts/build.py    # regenerate README.md and data/benchmarks.csv
```

A pull request that edits `README.md` directly will be asked to move the change into `scripts/data.py`.

## Inclusion criteria

An entry must be a **benchmark**: a defined task set, a defined scoring procedure, and a released
artifact that someone other than the authors can run. Simulators, datasets, and frameworks without a
canonical task set and metric belong in *Datasets and environments* and are labeled as enablers.

Every entry must state four things:

1. **Action involvement** (`L0`-`L4`). Does the agent act, and does the environment step in response?
   If a benchmark supports several modes, label the one it is normally reported in and note the other.
2. **Cost to run** (`$`-`$$$$`). Order of magnitude for one full evaluation pass at the scale the
   authors report. Say what dominates: API tokens, GPU-hours, or human supervision.
3. **Verifier.** Exact match, programmatic success predicate, learned or LLM judge, human rating, or
   physical measurement. If a model does the judging, link the human-agreement number.
4. **Scale.** Tasks, episodes, scenes, or questions - whatever the benchmark's own unit is.

Out of scope: single-paper evaluation sets never used outside the paper, leaderboards with no public
tasks or scoring code, demo videos, and results tables presented without a released harness.

## Writing style

- One factual sentence per entry describing what it measures and what makes it distinct.
- Do not copy the abstract, and do not use marketing adjectives.
- Do not report performance claims; benchmarks age, and numbers rot faster than descriptions.
- Prefer the arXiv abstract page as the primary link; add code, project, and dataset badges when
  official versions exist.
- Say what a benchmark *cannot* show when that is the most useful fact about it.

## Action-level classification guide

The common error is labeling an offline evaluation as closed-loop.

- `L0` - the input is fixed; the agent's output does not change what it sees next.
- `L1` - the agent predicts or generates a future, but does not act in an environment.
- `L2` - the agent emits actions scored against a pre-recorded trajectory. No environment step.
- `L3` - the environment steps in response to the agent's action. Errors compound.
- `L4` - the actions occur on real hardware.

If you are unsure between `L2` and `L3`, ask whether the agent can ever reach a state that the
dataset does not contain. If it can, it is `L3`.

## Safety

Entries in the safety section describe attacks and hazardous-instruction datasets. Contribute the
evaluation artifact and its protocol; do not contribute new attack payloads, and do not add content
whose primary use is to make a physical system act unsafely.
