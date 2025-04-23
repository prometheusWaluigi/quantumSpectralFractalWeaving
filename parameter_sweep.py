def parameter_sweep():
    """Generate heatmaps of coherence vs parameters"""
    # Define parameter ranges
    alphas = np.linspace(0.5, 2.5, 8)  # Coupling decay exponent
    gammas = np.logspace(-4, 0, 8)     # Decoherence rate
    g0s = np.linspace(0.1, 1.0, 5)     # Base coupling strength
    
    results = {}
    
    # First sweep: Alpha vs Gamma (fixing g0)
    global ALPHA, GAMMA, G0
    G0 = 0.5  # Fixed for this sweep
    
    coherence_map = np.zeros((len(alphas), len(gammas)))
    fractal_dims = np.zeros((len(alphas), len(gammas)))
    info_integration = np.zeros((len(alphas), len(gammas)))
    
    for i, alpha in enumerate(alphas):
        for j, gamma in enumerate(gammas):
            ALPHA, GAMMA = alpha, gamma
            
            sim_results = run_simulation(T=100)
            
            # Calculate metrics
            coherence_map[i, j] = np.mean(sim_results[len(sim_results)//2:, 1])  # Avg purity
            
            # Neural time series for fractal analysis
            neural_series = extract_neural_series(sim_results)
            fractal_dims[i, j] = compute_fractal_dimension(neural_series)
            
            # Proxy for integrated information
            # (e.g., mutual info between quantum and neural)
            info_integration[i, j] = calculate_integration(sim_results)
    
    # Generate heatmaps
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    im0 = axes[0].imshow(coherence_map, origin='lower', aspect='auto',
                        extent=[np.log10(gammas[0]), np.log10(gammas[-1]), 
                                alphas[0], alphas[-1]])
    axes[0].set_title('Quantum Coherence')
    axes[0].set_xlabel('Log Decoherence Rate (Γ)')
    axes[0].set_ylabel('Coupling Exponent (α)')
    plt.colorbar(im0, ax=axes[0])
    
    im1 = axes[1].imshow(fractal_dims, origin='lower', aspect='auto',
                        extent=[np.log10(gammas[0]), np.log10(gammas[-1]), 
                                alphas[0], alphas[-1]])
    axes[1].set_title('Neural Fractal Dimension')
    axes[1].set_xlabel('Log Decoherence Rate (Γ)')
    axes[1].set_ylabel('Coupling Exponent (α)')
    plt.colorbar(im1, ax=axes[1])
    
    im2 = axes[2].imshow(info_integration, origin='lower', aspect='auto',
                        extent=[np.log10(gammas[0]), np.log10(gammas[-1]), 
                                alphas[0], alphas[-1]])
    axes[2].set_title('Integrated Information')
    axes[2].set_xlabel('Log Decoherence Rate (Γ)')
    axes[2].set_ylabel('Coupling Exponent (α)')
    plt.colorbar(im2, ax=axes[2])
    
    plt.tight_layout()
    plt.savefig('parameter_sweep.png')
    
    results['alpha_gamma'] = {
        'params': {'alphas': alphas, 'gammas': gammas, 'g0': G0},
        'coherence': coherence_map,
        'fractal_dims': fractal_dims,
        'integration': info_integration
    }
    
    return results