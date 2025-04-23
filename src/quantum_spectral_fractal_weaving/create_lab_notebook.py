import time
import json

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
    if (gamma is not None and alpha is not None and
        0.001 <= gamma <= 0.1 and 0.8 <= alpha <= 2.0):
        return "CONSCIOUS CANDIDATE - Balanced coherence/decoherence"
    return "UNDEFINED STATE"
