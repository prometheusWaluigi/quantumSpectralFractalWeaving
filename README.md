# Quantum Spectral Fractal Weaving Simulation Engine

[![CI](https://github.com/prometheusWaluigi/quantumSpectralFractalWeaving/actions/workflows/ci.yml/badge.svg)](https://github.com/prometheusWaluigi/quantumSpectralFractalWeaving/actions)

A multi-scale, modular, and extensible simulation framework for exploring quantum spectral fractal dynamics and consciousness hypotheses.

## Features
- Quantum-neural hybrid simulation engine
- Parameter sweeps and criticality analysis
- EEG-like signal generation
- Ridge finding and visualization tools
- Future-ready for DuckDB results storage
- Automated CI with Poetry and GitHub Actions

## Installation
```bash
git clone https://github.com/prometheusWaluigi/quantumSpectralFractalWeaving.git
cd quantumSpectralFractalWeaving
poetry install --with dev
```

## Usage
All core modules are available as a package:
```python
from quantum_spectral_fractal_weaving import qsfw_simulation, parameter_sweep, find_critical_ridge, generate_simulated_eeg, create_lab_notebook
```

Run tests:
```bash
poetry run pytest
```

## Project Structure
- `src/quantum_spectral_fractal_weaving/` — Main package modules
- `tests/` — Pytest test suite
- `.github/workflows/ci.yml` — GitHub Actions workflow

## Roadmap
- [x] Package structure and CI
- [x] Core simulation modules
- [x] Test suite
- [ ] DuckDB results storage & querying
- [ ] CLI tools

## License
MIT

---

_If you use this project, please cite or star the repo!_
