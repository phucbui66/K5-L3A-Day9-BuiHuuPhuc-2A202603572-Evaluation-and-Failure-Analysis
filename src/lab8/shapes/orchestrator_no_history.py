"""Ablation: the same orchestrator without the optional refund-history read."""

from __future__ import annotations

from lab8.schemas import RunResult
from lab8.shapes.orchestrator import _run_claim


def run_claim(claim_id: str, *, seed: int, store_path: str,
              crash_at: str | None = None) -> RunResult:
    return _run_claim(claim_id, seed=seed, store_path=store_path,
                      crash_at=crash_at, include_history=False)
