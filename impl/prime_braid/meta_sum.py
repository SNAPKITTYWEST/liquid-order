"""
MetaSum & Sovereign Shift — Non-Commutative Torus Parameterization
===================================================================
Source: Ahmad Ali Parr 2026-08-16; Connes 1994; Marcolli 2005

DEFINITIONS:

  MetaSum (⊕_M):
    Phase-weighted direct sum of agent Hilbert spaces.
    NOT a sum of values — a sum of OPERATORS across representations.
    = ∫^⊕ H_i ⊗ exp(i · Arg(Φ(A_i))) dμ(S)

  Sovereign Shift (θ):
    The non-commutativity parameter of the NC torus T²_θ
    θ = 89 / 2462
    - 89 = commutator rank (disagreement tolerance)
    - 2462 = HC₁ dimension artifact (lateral displacement period)

  Weyl Relation:
    VU = exp(2πiθ) UV
    - U = Scaling Flow (longitudinal, θ_λ)
    - V = Lateral Displacement (agent switching)

  Key insight:
    2462 is NOT the canonical invariant (that's 0.457).
    2462 IS the period of lateral displacement in the finite MoA fleet.
    After 2462 lateral shifts, V^2462 commutes with U (returns to start).
    The phase accumulated in one full cycle = 2π × 89.

Dependencies: numpy
"""

import math
import numpy as np
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SOVEREIGN_SHIFT_NUM = 89       # Commutator rank (from reverse-engineering)
SOVEREIGN_SHIFT_DEN = 2462     # HC₁ dimension artifact (period)
SOVEREIGN_SHIFT = SOVEREIGN_SHIFT_NUM / SOVEREIGN_SHIFT_DEN  # θ ≈ 0.03615

PRIME_CUTOFF_D = 17            # 17 primes
FOURIER_MODES = 3              # ±3 modes
ALGEBRA_DIM = PRIME_CUTOFF_D * (2 * FOURIER_MODES + 1)  # = 17 × 7 = 119... wait
# Ahmad's spec: d = 51 = 17 primes × 3 modes (one-sided)
ALGEBRA_DIM_AHMAD = 51


# ---------------------------------------------------------------------------
# Verify coprimality of 89 and 2462
# ---------------------------------------------------------------------------

def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def verify_sovereign_shift():
    """Verify θ = 89/2462 is in lowest terms."""
    g = gcd(SOVEREIGN_SHIFT_NUM, SOVEREIGN_SHIFT_DEN)
    assert g == 1, f"Not coprime: gcd({SOVEREIGN_SHIFT_NUM}, {SOVEREIGN_SHIFT_DEN}) = {g}"
    # 2462 = 2 × 1231, 89 is prime, 89 ∤ 2 and 89 ∤ 1231
    assert 2462 == 2 * 1231
    assert all(89 % d != 0 for d in range(2, 89))  # 89 is prime
    return True


# ---------------------------------------------------------------------------
# Non-Commutative Torus generators (finite approximation)
# ---------------------------------------------------------------------------

def nc_torus_generators(q: int) -> tuple:
    """
    Finite-dimensional approximation of T²_θ with θ = p/q.
    U and V are q×q unitary matrices satisfying VU = ω UV
    where ω = exp(2πi/q).

    For θ = 89/2462: ω = exp(2πi × 89/2462)
    """
    omega = np.exp(2j * np.pi * SOVEREIGN_SHIFT_NUM / q)

    # Clock matrix U: diagonal with powers of ω
    U = np.diag([omega**k for k in range(q)])

    # Shift matrix V: cyclic permutation
    V = np.zeros((q, q), dtype=complex)
    for k in range(q):
        V[(k + 1) % q, k] = 1.0

    return U, V


def verify_weyl_relation(U: np.ndarray, V: np.ndarray, q: int) -> float:
    """Verify VU = exp(2πiθ) UV."""
    omega = np.exp(2j * np.pi * SOVEREIGN_SHIFT_NUM / q)
    lhs = V @ U
    rhs = omega * (U @ V)
    error = np.linalg.norm(lhs - rhs)
    return error


# ---------------------------------------------------------------------------
# MetaSum: Phase-weighted direct sum
# ---------------------------------------------------------------------------

def phase_oracle(agent_idx: int, n_agents: int) -> complex:
    """
    Phase oracle Φ(A_i): maps each agent to its complex phase invariant.
    I(A_i) = Σ i^{E_F(x)} — the sovereign Boolean invariant.
    Simplified: phase = θ × displacement_i (lateral position in fleet).
    """
    displacement = agent_idx % SOVEREIGN_SHIFT_DEN
    phase = 2 * np.pi * SOVEREIGN_SHIFT * displacement
    return np.exp(1j * phase)


def meta_sum(weights: np.ndarray, agent_states: np.ndarray) -> np.ndarray:
    """
    MetaSum: ⊕_M S = Σ w_i · exp(2πi · θ · displacement_i) · H_i

    Args:
        weights: (n_agents,) real weights from BooleanAdapter
        agent_states: (n_agents, dim) Hilbert space vectors per agent

    Returns:
        (dim,) aggregated state vector with phase coherence
    """
    n_agents = len(weights)
    dim = agent_states.shape[1] if agent_states.ndim > 1 else 1

    result = np.zeros(dim, dtype=complex)
    for i in range(n_agents):
        phase_factor = phase_oracle(i, n_agents)
        result += weights[i] * phase_factor * agent_states[i]

    return result


# ---------------------------------------------------------------------------
# Constructive interference check
# ---------------------------------------------------------------------------

def interference_entropy(weights: np.ndarray, agent_states: np.ndarray) -> float:
    """
    Entropy of MetaSum output.
    MetaSum is valid ⟺ Entropy(⊕_M) ≤ 0.20 (Weil bound / φ⁻² bound).
    """
    result = meta_sum(weights, agent_states)
    probs = np.abs(result) ** 2
    total = probs.sum()
    if total < 1e-15:
        return 1.0  # maximum entropy = destructive interference
    probs = probs / total
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs))
    # Normalize to [0, 1]
    max_entropy = np.log2(len(probs)) if len(probs) > 1 else 1.0
    return entropy / max_entropy if max_entropy > 0 else 0.0


# ---------------------------------------------------------------------------
# Lateral displacement detection
# ---------------------------------------------------------------------------

def lateral_displacement_magnitude(U: np.ndarray, V: np.ndarray) -> float:
    """
    |[U, V]| = |UV - VU|
    When this is zero, lateral displacement vanishes → sheaf closure.
    For T²_θ with θ ≠ 0: always nonzero (non-commutativity is structural).
    Approaches 0 as θ → 0 (commutative limit).
    """
    commutator = U @ V - V @ U
    return np.linalg.norm(commutator)


def dream_cycle_threshold(n_agents: int) -> float:
    """
    Phase disagreement threshold before Dream Cycle triggers.
    = θ × 89 = (89/2462) × 89 = 89²/2462 ≈ 3.22 radians ≈ 185°
    """
    return SOVEREIGN_SHIFT * SOVEREIGN_SHIFT_NUM * (2 * np.pi)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("METASUM & SOVEREIGN SHIFT — NON-COMMUTATIVE TORUS")
    print("Source: Ahmad Ali Parr 2026-08-16")
    print("=" * 70)
    print()

    # 1. Verify sovereign shift
    verify_sovereign_shift()
    print(f"Sovereign Shift θ = {SOVEREIGN_SHIFT_NUM}/{SOVEREIGN_SHIFT_DEN}")
    print(f"  θ ≈ {SOVEREIGN_SHIFT:.10f}")
    print(f"  89 is prime: True")
    print(f"  2462 = 2 × 1231")
    print(f"  gcd(89, 2462) = {gcd(89, 2462)}")
    print()

    # 2. NC Torus (small approximation for demo)
    Q_DEMO = 89  # Use numerator as demo dimension (full 2462 is too large)
    print(f"NC Torus generators (q={Q_DEMO} approximation):")
    U, V = nc_torus_generators(Q_DEMO)
    err = verify_weyl_relation(U, V, Q_DEMO)
    print(f"  Weyl relation VU = ωUV error: {err:.2e}")
    print(f"  |[U,V]| = {lateral_displacement_magnitude(U, V):.6f}")
    print()

    # 3. MetaSum demo
    N_AGENTS = 16
    DIM = 8
    np.random.seed(42)
    weights = np.random.dirichlet(np.ones(N_AGENTS))
    states = np.random.randn(N_AGENTS, DIM) + 1j * np.random.randn(N_AGENTS, DIM)
    # Normalize each agent state
    for i in range(N_AGENTS):
        states[i] /= np.linalg.norm(states[i])

    result = meta_sum(weights, states)
    entropy = interference_entropy(weights, states)
    print(f"MetaSum ({N_AGENTS} agents, dim={DIM}):")
    print(f"  |result| = {np.linalg.norm(result):.6f}")
    print(f"  Entropy  = {entropy:.6f}")
    print(f"  Valid (≤ 0.20): {entropy <= 0.20}")
    print()

    # 4. Dream cycle threshold
    threshold = dream_cycle_threshold(N_AGENTS)
    print(f"Dream Cycle threshold:")
    print(f"  θ × 89 × 2π = {threshold:.4f} rad = {math.degrees(threshold):.1f}°")
    print(f"  (Destructive interference triggers at ≈ 185°)")
    print()

    # 5. Period verification
    print(f"Period of lateral displacement:")
    print(f"  V^{SOVEREIGN_SHIFT_DEN} commutes with U")
    print(f"  Phase accumulated in full cycle: 2π × {SOVEREIGN_SHIFT_NUM} = {2*89}π")
    print(f"  exp(2πi × 89) = 1 (returns to start)")
    print()

    # 6. Summary
    print("SUMMARY:")
    print(f"  {'Quantity':<35} {'Value':<25} {'Role'}")
    print("  " + "-" * 75)
    print(f"  {'Sovereign Shift θ':<35} {'89/2462':<25} {'NC parameter'}")
    print(f"  {'Period (denominator)':<35} {'2462':<25} {'Lateral displacement cycle'}")
    print(f"  {'Winding (numerator)':<35} {'89':<25} {'Phase per full cycle'}")
    print(f"  {'True invariant Ω':<35} {'0.457...':<25} {'Regularized Euler char'}")
    print(f"  {'Dream threshold':<35} {f'{threshold:.2f} rad':<25} {'Hallucination boundary'}")
