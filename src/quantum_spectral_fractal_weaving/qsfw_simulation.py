import numpy as np
import qutip as qt
from scipy import signal
import matplotlib.pyplot as plt

# --- QuTiP/SciPy int32 indices compatibility patch ---
def _force_int32_indices(mat):
    if hasattr(mat, 'indices') and mat.indices.dtype != np.int32:
        mat.indices = mat.indices.astype(np.int32)
    if hasattr(mat, 'indptr') and mat.indptr.dtype != np.int32:
        mat.indptr = mat.indptr.astype(np.int32)
    return mat

_original_destroy = qt.destroy
def destroy_int32(dim, *args, **kwargs):
    mat = _original_destroy(dim, *args, **kwargs)
    if hasattr(mat, 'data'):
        mat.data = _force_int32_indices(mat.data)
    return mat
qt.destroy = destroy_int32
# ----------------------------------------------------

def run_simulation(*args, **kwargs):
    """Stub for run_simulation. Should be implemented in the main simulation module."""
    raise NotImplementedError("run_simulation is not yet implemented.")

def extract_neural_series(*args, **kwargs):
    """Stub for extract_neural_series. Should be implemented in the main simulation module."""
    raise NotImplementedError("extract_neural_series is not yet implemented.")

dt_N = 0.1

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
    phases = np.random.uniform(0, 2*np.pi, size)
    freqs = np.random.normal(1.0, 0.1, size) / (phi**(2*alpha))
    coupling = 0.6
    print(f"[init_neural_net] size={size}, phi={phi}, alpha={alpha}, coupling={coupling}")
    return {'phases': phases, 'freqs': freqs, 'coupling': coupling}

_q_destroy_cache = {}
def get_destroy(dim):
    if dim not in _q_destroy_cache:
        _q_destroy_cache[dim] = qt.destroy(dim)
        print(f"[get_destroy] Created and cached destroy operator for dim={dim}")
    return _q_destroy_cache[dim]

def build_H0(state_net, dim=4):
    a = get_destroy(dim)
    H_base = 2.0 * a.dag() * a
    neural_field = np.mean(np.sin(state_net['phases']))
    H_drive = 0.1 * neural_field * (a + a.dag())
    print(f"[build_H0] neural_field={neural_field:.4f}")
    return H_base + H_drive

def measure_field(state_q):
    a = get_destroy(state_q.dims[0][0])
    val = qt.expect(a + a.dag(), state_q)
    print(f"[measure_field] field expectation={val:.4f}")
    return val

def apply_drive(state_net, quantum_field):
    old = state_net['phases'].copy()
    state_net['phases'] = (
        state_net['phases'] + 0.1 * quantum_field *
        np.random.normal(1, 0.1, len(state_net['phases']))
    )
    delta0 = state_net['phases'][0] - old[0]
    print(f"[apply_drive] quantum_field={quantum_field:.4f}, phase0 Δ={delta0:.4f}")
    return state_net

def update_neural_net(state_net, dt):
    phases, freqs, K = (state_net['phases'], state_net['freqs'],
                        state_net['coupling'])
    phase_diff = phases[:, None] - phases[None, :]
    interaction = np.sum(np.sin(phase_diff), axis=1)
    new_phases = (phases + dt * (freqs + (K/len(phases)) * interaction)) % (2*np.pi)
    state_net['phases'] = new_phases
    print(f"[update_neural_net] dt={dt}, mean interaction={np.mean(interaction):.4f}")
    return state_net

def smoke_test(T=50, dt_N=0.1, dt_q=0.01, q_steps=5, dim=4):
    print(f"[smoke_test] Starting: T={T}, dt_N={dt_N}, dt_q={dt_q}, q_steps={q_steps}, dim={dim}")
    qm_state = init_quantum_state(dim)
    nn_state = init_neural_net()
    L_decohere = np.sqrt(0.01) * get_destroy(dim)
    print(f"[smoke_test] Using decoherence rate=0.01")
    q_series, n_series = [], []
    times = np.arange(0, T, dt_N)
    for t in times:
        print(f"[smoke_test] t={t:.2f}")
        for step in range(q_steps):
            H0 = build_H0(nn_state, dim)
            result = qt.mesolve(H0, qm_state, [0, dt_q], c_ops=[L_decohere])
            qm_state = result.states[-1]
            print(f"  [quantum] step {step+1}/{q_steps}")
        q_val = measure_field(qm_state)
        q_series.append(q_val)
        apply_drive(nn_state, q_val)
        nn_state = update_neural_net(nn_state, dt_N)
        n_val = np.mean(np.sin(nn_state['phases']))
        n_series.append(n_val)
        print(f"  [neural] sync={n_val:.4f}")
    print("[smoke_test] Finished simulation, computing spectra...")
    fq, Pq = signal.welch(q_series, fs=1/dt_q)
    fn, Pn = signal.welch(n_series, fs=1/dt_N)
    plt.figure(figsize=(10,6))
    plt.loglog(fq, Pq, label='Quantum')
    plt.loglog(fn, Pn, label='Neural')
    plt.axvline(1.0, linestyle='--', color='gray')
    plt.axvline(1/1.618, linestyle='--', color='gray')
    plt.legend(); plt.title('Smoke Test Spectra')
    plt.show()
