## What is being added

<!-- Benchmark name and one sentence on what it measures. -->

## Required fields

- **Action level:** `L0` / `L1` / `L2` / `L3` / `L4` — and why (does the environment step in response to the agent?)
- **Cost to run:** `$` / `$$` / `$$$` / `$$$$` — and what dominates the cost
- **Verifier:** exact match / programmatic success / learned judge / human / physical measurement
- **Scale:** tasks, episodes, scenes, or questions

## Checklist

- [ ] Entry added to `scripts/data.py`, not to `README.md`
- [ ] `python3 scripts/verify.py` passes (arXiv title resolves, all links 200)
- [ ] `python3 scripts/build.py` re-run and the regenerated files committed
- [ ] Description is one factual sentence, no marketing adjectives, no performance claims
