def generate_simulated_eeg(optimal_params, duration=1000):
    """Generate simulated EEG-like signals at optimal parameters"""
    # Select parameters from critical ridge
    global ALPHA, GAMMA
    ALPHA, GAMMA = optimal_params[len(optimal_params)//2][:2]  # Mid-point of ridge
    
    # Run longer simulation
    results = run_simulation(T=duration)
    
    # Extract neural population activity
    neural_series = extract_neural_series(results)
    
    # Generate simulated EEG by filtering neural activity
    # (in reality, would use forward model from neurons to scalp)
    eeg_channels = []
    
    # Generate 10 EEG channels with different spatial weightings
    for i in range(10):
        weights = np.random.normal(0, 1, neural_series.shape[1])
        channel = np.dot(neural_series, weights)
        
        # Apply basic filtering to simulate skull & scalp effects
        b, a = signal.butter(3, 0.2, 'lowpass')
        channel = signal.filtfilt(b, a, channel)
        
        eeg_channels.append(channel)
    
    eeg_data = np.array(eeg_channels)
    
    # Calculate power spectral densities
    fs = 1/dt_N  # Sampling frequency
    freqs, psds = signal.welch(eeg_data, fs=fs, nperseg=512, axis=1)
    
    # Plot simulated EEG and spectra
    plt.figure(figsize=(15, 10))
    
    # Time series
    plt.subplot(211)
    for i, channel in enumerate(eeg_channels[:5]):  # Plot first 5 channels
        plt.plot(results[:, 0], channel + i*3, label=f'Ch {i+1}')
    plt.xlabel('Time')
    plt.ylabel('EEG Amplitude')
    plt.title('Simulated EEG Time Series')
    plt.xlim(results[0, 0], results[100, 0])  # First 100 time points
    plt.legend()
    
    # Power spectra (log-log)
    plt.subplot(212)
    for i, psd in enumerate(psds[:5]):  # Plot first 5 channels
        plt.loglog(freqs, psd, label=f'Ch {i+1}')
    
    # Mark frequency bands
    band_freqs = [4, 8, 13, 30]  # Delta, theta, alpha, beta boundaries
    for f in band_freqs:
        plt.axvline(x=f, color='k', linestyle='--', alpha=0.3)
    
    # Fit 1/f^β line to middle portion
    mask = (freqs > 5) & (freqs < 30)
    slope, intercept = np.polyfit(np.log10(freqs[mask]), 
                                  np.log10(np.mean(psds, axis=0)[mask]), 1)
    plt.loglog(freqs[mask], 10**(intercept) * freqs[mask]**slope, 'r--', 
              linewidth=2, label=f'1/f^{-slope:.2f}')
    
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density')
    plt.title(f'EEG Power Spectra (Fractal Dimension ~{(5-slope)/2:.2f})')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('simulated_eeg.png')
    
    return eeg_data, freqs, psds