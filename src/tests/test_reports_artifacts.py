"""Evidence files in src/reports/ must match what the lab tools produce."""

import json
from pathlib import Path

from lab8.metrics import summarize

REPORTS = Path(__file__).resolve().parents[1] / "reports"
SHAPES = {"workflow", "single", "orchestrator", "swarm"}
SEEDS = [11, 22, 33, 44, 55]


def _load(name: str) -> dict:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


def test_crash_report_is_20_of_20():
    crash = _load("crash.json")
    assert crash["count"] == 20
    assert crash["passed"] == 20
    assert crash["crash_safety"] == "20/20"


def test_benchmark_covers_four_shapes_ten_claims_five_seeds():
    bench = _load("benchmark.json")
    cv = bench["controlled_variables"]
    assert set(bench["by_shape"]) == SHAPES
    assert cv["seeds"] == SEEDS
    assert len(cv["claim_ids"]) >= 10
    assert cv["latency"] == "unavailable"
    assert cv["pricing"]["simulated"] is True


def test_benchmark_summary_is_recomputed_from_trials():
    bench = _load("benchmark.json")
    recomputed = summarize(bench["trials"])
    for shape in SHAPES:
        stored, fresh = bench["by_shape"][shape], recomputed[shape]
        for key in ("trials", "successes", "pass_rate", "pass_5", "seed_variance", "cost_per_success_vnd"):
            assert stored[key] == fresh[key], (shape, key)


def test_seed_ablation_removes_swarm_seed_55_failure():
    base = _load("benchmark.json")["by_shape"]
    abl = _load("ablation_seeds.json")
    assert not set(abl["controlled_variables"]["seeds"]) & set(SEEDS)
    assert base["swarm"]["pass_rate"] < 1.0
    assert abl["by_shape"]["swarm"]["pass_rate"] == 1.0
    for shape in ("workflow", "single", "orchestrator"):
        assert abl["by_shape"][shape]["pass_rate"] == base[shape]["pass_rate"] == 1.0
