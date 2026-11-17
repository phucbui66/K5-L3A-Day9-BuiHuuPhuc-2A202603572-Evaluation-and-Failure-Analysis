"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import comb, isfinite
from numbers import Integral

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge) or not len(human):
        raise ValueError("labels must be non-empty and have equal lengths")
    counts = dict.fromkeys(("tp", "fp", "fn", "tn"), 0)
    for h, j in zip(human, judge):
        if h not in ("PASS", "FAIL") or j not in ("PASS", "FAIL"):
            raise ValueError("labels must be PASS or FAIL")
        counts[("tp" if h == POS else "fp") if j == POS else ("fn" if h == POS else "tn")] += 1
    return counts


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    cm = confusion(human, judge)
    pden, rden = cm["tp"] + cm["fp"], cm["tp"] + cm["fn"]
    return (cm["tp"] / pden if pden else 0.0, cm["tp"] / rden if rden else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    cm = confusion(human, judge)
    n = len(human)
    observed = (cm["tp"] + cm["tn"]) / n
    human_pos = (cm["tp"] + cm["fn"]) / n
    judge_pos = (cm["tp"] + cm["fp"]) / n
    expected = human_pos * judge_pos + (1 - human_pos) * (1 - judge_pos)
    if expected == 1:
        raise ValueError("kappa is undefined when expected agreement is 1")
    return (observed - expected) / (1 - expected)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    if any(not isfinite(x) or not 0 <= x <= 1 for x in (observed_rate, sensitivity, specificity)):
        raise ValueError("rates must be finite probabilities")
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError("Rogan-Gladen needs sensitivity + specificity > 1")
    return max(0.0, min(1.0, (observed_rate + specificity - 1) / denominator))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy.stats import bootstrap

    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or not len(x):
        raise ValueError("paired samples must be non-empty, equal-length vectors")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("paired samples must be finite")
    if not 0 < confidence < 1 or not isinstance(n_resamples, Integral) or n_resamples < 1:
        raise ValueError("invalid bootstrap configuration")
    difference = x - y
    if np.all(difference == difference[0]):
        delta = float(difference[0])
        return delta, delta, delta
    estimate = bootstrap((x, y), lambda p, q, axis: np.mean(p - q, axis=axis),
                         paired=True, method="percentile", n_resamples=n_resamples,
                         confidence_level=confidence, rng=np.random.default_rng(rng))
    return float(np.mean(difference)), float(estimate.confidence_interval.low), float(estimate.confidence_interval.high)


def _validate_trials(n: int, c: int, k: int) -> None:
    if any(isinstance(v, bool) or not isinstance(v, Integral) for v in (n, c, k)):
        raise ValueError("n, c, k must be integers")
    if n < 1 or not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError("require n >= 1, 0 <= c <= n, 1 <= k <= n")


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    _validate_trials(n, c, k)
    return 1.0 - comb(n - c, k) / comb(n, k) if n - c >= k else 1.0


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    _validate_trials(n, c, k)
    return comb(c, k) / comb(n, k) if c >= k else 0.0
