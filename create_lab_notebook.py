def create_lab_notebook(param_set, results_summary):
    """Generate a structured lab notebook entry"""
    notebook = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": param_set,
        "hypothesized_state": classify_conscious_state(param_set),
        "results": results_summary,
        "observations": [],
        "conclusions": ""
    }
    
    return notebook

def classify_conscious_state(params):
    """Map parameter set to hypothesized conscious state"""
    alpha, gamma, g0 = params.get('ALPHA', None), params.get('GAMMA', None), params.get('G0', None)
    
    # Simple classifier based on parameter regions
    if gamma is not None:
        if gamma > 0.1:
            return "UNCONSCIOUS - High decoherence"
        elif gamma < 0.001:
            return "UNSTABLE QUANTUM - Too little decoherence"
    
    if alpha is not None:
        if alpha > 2.0:
            return "FRAGMENTED - Scales too disconnected"
        elif alpha < 0.8:
            return "OVER-INTEGRATED - Scales too coupled"
    
    # If in good ranges for both params
    if (gamma is not None and alpha is not None and
        0.001 <= gamma <= 0.1 and 0.8 <= alpha <= 2.0):
        return "CONSCIOUS CANDIDATE - Balanced coherence/decoherence"
    
    return "UNDEFINED STATE"

# Example usage
example_notebook = create_lab_notebook(
    {"ALPHA": 1.2, "GAMMA": 0.01, "G0": 0.5},
    {
        "mean_coherence": 0.78,
        "fractal_dimension": 1.52,
        "integration_measure": 0.65,
        "stability_time": 120
    }
)

example_notebook["observations"] = [
    "Golden-ratio frequency peaks clearly visible in PSD",
    "Cross-scale correlation maintains steady value ~0.4",
    "Neural fractal dimension stays in critical range 1.4-1.6"
]

example_notebook["conclusions"] = """
This parameter set shows many properties expected of a conscious state.
The balance between coupling (α=1.2) and decoherence (Γ=0.01) allows
quantum influence to propagate upward while maintaining stability.
The fractal dimension of neural activity (D_f=1.52) indicates
critical dynamics, supporting integrated information flow.
"""

print(json.dumps(example_notebook, indent=2))