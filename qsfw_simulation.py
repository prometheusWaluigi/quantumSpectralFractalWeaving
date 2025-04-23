# Quantum Spectral Fractal Weaving Simulation Engine
# Core architecture for recursive multi-scale coupling, smoke test, and debug logs

import numpy as np
import qutip as qt
from scipy import signal

# Optional: fix randomness for reproducibility during debugging
# np.random.seed(42)


def init_quantum_state(dim=4):
    """
    Initialize the quantum subsystem (Level 0).
    Returns a random ket of dimension 'dim'.
    """
    state = qt.rand_ket(dim)
    print(f"[init_quantum_state] Initialized quantum state with dimension={dim}")
    return state


def init_neural_net(size=100, phi=1.618, alpha=1.2):
    """
    Initialize the neural network (Level 2) as a set of Kuramoto oscillators.
    - 'size' is the number of oscillators.
    - 'phi' and 'alpha' determine intrinsic frequency scaling.
    Returns a dict with phases, natural frequencies, and coupling.
    """
    # Random initial phases uniformly in [0, 2π)
    phases = np.random.uniform(0, 2*np.pi, size)
    # Frequencies drawn from normal distribution, scaled by φ^{-2α}
    freqs = np.random.normal(1.0, 0.1, size) / (phi**(2*alpha))
    coupling = 0.6  # Base coupling strength among oscillators
    print(f"[init_neural_net] size={size}, phi={phi}, alpha={alpha}, coupling={coupling}")
    return {'phases': phases, 'freqs': freqs, 'coupling': coupling}


# Cache destroy operators by dimension to avoid repeated construction overhead
_q_destroy_cache = {}
def get_destroy(dim):
    """
    Retrieve or cache the annihilation operator for dimension 'dim'.
    Caches result in _q_destroy_cache.
    """
    if dim not in _q_destroy_cache:
        _q_destroy_cache[dim] = qt.destroy(dim)
        print(f"[get_destroy] Created and cached destroy operator for dim={dim}")
    return _q_destroy_cache[dim]


def build_H0(state_net, dim=4):
    """
    Build the quantum Hamiltonian H0 with feedback from neural level.
    - Base term: harmonic oscillator 2 a†a
    - Drive term: proportional to mean neural phase (couples neural ↔ quantum)
    """
    a = get_destroy(dim)                      # Retrieve annihilation operator
    H_base = 2.0 * a.dag() * a                # Base harmonic term
    # Feedback: mean sine of neural phases modulates the quantum drive
    neural_field = np.mean(np.sin(state_net['phases']))
    H_drive = 0.1 * neural_field * (a + a.dag())
    print(f"[build_H0] neural_field={neural_field:.4f}")
    return H_base + H_drive


def measure_field(state_q):
    """
    Measure a quantum field observable (a + a†) expectation.
    Returns a float to drive the neural level.
    """
    a = get_destroy(state_q.dims[0][0])       # Use cached destroy operator
    val = qt.expect(a + a.dag(), state_q)     # Compute expectation value
    print(f"[measure_field] field expectation={val:.4f}")
    return val


def apply_drive(state_net, quantum_field):
    """
    Apply quantum feedback to neural phases.
    - Each neural phase incremented by a noisy term ∝ quantum_field.
    """
    old = state_net['phases'].copy()
    # Vectorized noise-modulated update
    state_net['phases'] = (
        state_net['phases'] + 0.1 * quantum_field *
        np.random.normal(1, 0.1, len(state_net['phases']))
    )
    # Log change of first oscillator as a debug sample
    delta0 = state_net['phases'][0] - old[0]
    print(f"[apply_drive] quantum_field={quantum_field:.4f}, phase0 Δ={delta0:.4f}")
    return state_net


def update_neural_net(state_net, dt):
    """
    Perform one integration step for the Kuramoto network:
    θ̇_i = ω_i + (K/N) Σ_j sin(θ_j - θ_i)
    Returns updated state_net with new phases.
    """
    phases, freqs, K = (state_net['phases'], state_net['freqs'],
                        state_net['coupling'])
    # Compute pairwise phase differences matrix
    phase_diff = phases[:, None] - phases[None, :]
    # Sum of sine of differences = interaction term for each oscillator
    interaction = np.sum(np.sin(phase_diff), axis=1)
    # Euler integration with modulo for phase wrap
    new_phases = (phases + dt * (freqs + (K/len(phases)) * interaction)) % (2*np.pi)
    state_net['phases'] = new_phases
    print(f"[update_neural_net] dt={dt}, mean interaction={np.mean(interaction):.4f}")
    return state_net


def smoke_test(T=50, dt_N=0.1, dt_q=0.01, q_steps=5, dim=4):
    """
    Run the smoke test:
    - Initialize quantum and neural subsystems
    - Loop: micro-steps for quantum evolution, measure-field, drive neural, update neural
    - Collect time series, compute and plot spectra
    """
    print(f"[smoke_test] Starting: T={T}, dt_N={dt_N}, dt_q={dt_q}, q_steps={q_steps}, dim={dim}")
    # Initialize states
    qm_state = init_quantum_state(dim)
    nn_state = init_neural_net()
    # Decoherence operator for quantum amplitude damping
    L_decohere = np.sqrt(0.01) * get_destroy(dim)
    print(f"[smoke_test] Using decoherence rate=0.01")

    q_series, n_series = [], []
    times = np.arange(0, T, dt_N)
    for t in times:
        print(f"[smoke_test] t={t:.2f}")
        # Quantum micro-iterations
        for step in range(q_steps):
            H0 = build_H0(nn_state, dim)
            result = qt.mesolve(H0, qm_state, [0, dt_q], c_ops=[L_decohere])
            qm_state = result.states[-1]
            print(f"  [quantum] step {step+1}/{q_steps}")
        # Measure and store
        q_val = measure_field(qm_state)
        q_series.append(q_val)

        # Apply quantum feedback to neural network
        apply_drive(nn_state, q_val)
        nn_state = update_neural_net(nn_state, dt_N)
        n_val = np.mean(np.sin(nn_state['phases']))  # global sync metric
        n_series.append(n_val)
        print(f"  [neural] sync={n_val:.4f}")

    print("[smoke_test] Finished simulation, computing spectra...")
    # Compute power spectral densities for both series
    fq, Pq = signal.welch(q_series, fs=1/dt_q)
    fn, Pn = signal.welch(n_series, fs=1/dt_N)

    # Plot spectra: log-log for clear power-law and golden-ratio markers
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,6))
    plt.loglog(fq, Pq, label='Quantum')
    plt.loglog(fn, Pn, label='Neural')
    # Mark base frequency and φ-scaled frequency for visual check
    plt.axvline(1.0, linestyle='--', color='gray')
    plt.axvline(1/1.618, linestyle='--', color='gray')
    plt.legend(); plt.title('Smoke Test Spectra')
    plt.show()


# Entry point for direct execution
if __name__ == '__main__':
    smoke_test()
