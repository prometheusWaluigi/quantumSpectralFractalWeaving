import importlib
import pytest

# Test create_lab_notebook.py

def test_create_lab_notebook():
    mod = importlib.import_module('create_lab_notebook')
    param_set = {"ALPHA": 1.0, "GAMMA": 0.01, "G0": 0.5}
    results_summary = {"mean_coherence": 0.7, "fractal_dimension": 1.5}
    notebook = mod.create_lab_notebook(param_set, results_summary)
    assert isinstance(notebook, dict)
    assert "parameters" in notebook
    assert "results" in notebook

# Test find_critical_ridge.py

def test_find_critical_ridge():
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # For headless testing
    mod = importlib.import_module('find_critical_ridge')
    # Fake sweep_results structure
    sweep_results = {
        'alpha_gamma': {
            'coherence': np.ones((3,3)),
            'integration': np.ones((3,3)),
            'params': {'alphas': np.array([1,2,3]), 'gammas': np.array([0.1,0.2,0.3])}
        }
    }
    ridge = mod.find_critical_ridge(sweep_results)
    assert isinstance(ridge, list)
    assert len(ridge) == 3

# Test generate_simulated_eeg.py

def test_generate_simulated_eeg():
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    mod = importlib.import_module('generate_simulated_eeg')
    # Fake optimal_params
    optimal_params = [(1, 0.1, 1.0), (2, 0.2, 1.0), (3, 0.3, 1.0)]
    # Patch run_simulation and extract_neural_series
    mod.run_simulation = lambda T=1000: np.column_stack([np.arange(100), np.random.randn(100, 3)])
    mod.extract_neural_series = lambda results: np.random.randn(100, 5)
    mod.dt_N = 0.1
    eeg_data, freqs, psds = mod.generate_simulated_eeg(optimal_params, duration=100)
    assert eeg_data.shape[0] == 10
    assert freqs is not None and psds is not None

# Test parameter_sweep.py

def test_parameter_sweep():
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    mod = importlib.import_module('parameter_sweep')
    # Patch run_simulation, extract_neural_series, compute_fractal_dimension, calculate_integration
    mod.run_simulation = lambda T=100: np.column_stack([np.arange(100), np.random.randn(100, 3)])
    mod.extract_neural_series = lambda results: np.random.randn(100, 5)
    mod.compute_fractal_dimension = lambda series: 1.5
    mod.calculate_integration = lambda results: 0.5
    results = mod.parameter_sweep()
    assert 'alpha_gamma' in results
    assert 'coherence' in results['alpha_gamma']

# Test qsfw_simulation.py (import and main smoke_test)

def test_qsfw_simulation_import():
    mod = importlib.import_module('qsfw_simulation')
    assert hasattr(mod, 'smoke_test')
    # Run smoke_test with minimal T for speed
    mod.smoke_test(T=1, dt_N=0.1, dt_q=0.01, q_steps=1, dim=2)

# Test smoke_test.py (empty or placeholder)

def test_smoke_test_py():
    # Just check import (file may be empty)
    importlib.import_module('smoke_test')
