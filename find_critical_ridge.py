def find_critical_ridge(sweep_results):
    """Locate the critical ridge where consciousness measures peak"""
    coherence = sweep_results['alpha_gamma']['coherence']
    integration = sweep_results['alpha_gamma']['integration']
    
    # Combine metrics (could use different weightings)
    combined_metric = coherence * integration
    
    # Find ridge in parameter space
    alphas = sweep_results['alpha_gamma']['params']['alphas']
    gammas = sweep_results['alpha_gamma']['params']['gammas']
    
    # For each alpha, find optimal gamma
    optimal_params = []
    for i, alpha in enumerate(alphas):
        j_max = np.argmax(combined_metric[i, :])
        gamma_max = gammas[j_max]
        optimal_params.append((alpha, gamma_max, combined_metric[i, j_max]))
    
    # Plot the ridge
    plt.figure(figsize=(10, 6))
    
    # Heatmap with ridge overlaid
    plt.imshow(combined_metric, origin='lower', aspect='auto',
              extent=[np.log10(gammas[0]), np.log10(gammas[-1]), 
                      alphas[0], alphas[-1]])
    plt.colorbar(label='Combined Consciousness Metric')
    
    # Mark the ridge
    ridge_alphas = [p[0] for p in optimal_params]
    ridge_log_gammas = [np.log10(p[1]) for p in optimal_params]
    plt.plot(ridge_log_gammas, ridge_alphas, 'r-o', linewidth=2, 
             label='Consciousness Ridge')
    
    plt.title('Critical Consciousness Ridge in Parameter Space')
    plt.xlabel('Log Decoherence Rate (Γ)')
    plt.ylabel('Coupling Exponent (α)')
    plt.legend()
    plt.savefig('consciousness_ridge.png')
    
    return optimal_params