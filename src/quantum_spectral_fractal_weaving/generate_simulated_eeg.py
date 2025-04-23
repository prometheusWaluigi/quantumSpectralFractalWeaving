import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

from .qsfw_simulation import run_simulation, extract_neural_series, dt_N

def generate_simulated_eeg(optimal_params, duration=1000):
    """Generate simulated EEG-like signals at optimal parameters"""
    global ALPHA, GAMMA, dt_N
    ALPHA, GAMMA = optimal_params[len(optimal_params)//2][:2]
    results = run_simulation(T=duration)
    neural_series = extract_neural_series(results)
    eeg_channels = []
    for i in range(10):
        weights = np.random.normal(0, 1, neural_series.shape[1])
        channel = np.dot(neural_series, weights)
        b, a = signal.butter(3, 0.2, 'lowpass')
        channel = signal.filtfilt(b, a, channel)
        eeg_channels.append(channel)
    eeg_data = np.array(eeg_channels)
    fs = 1/dt_N
    freqs, psds = signal.welch(eeg_data, fs=fs, nperseg=512, axis=1)
    plt.figure(figsize=(15, 10))
    plt.subplot(211)
    for i, channel in enumerate(eeg_channels[:5]):
        plt.plot(results[:, 0], channel + i*3, label=f'Ch {i+1}')
    plt.xlabel('Time')
    plt.ylabel('EEG Amplitude')
    plt.title('Simulated EEG Time Series')
    plt.xlim(results[0, 0], results[100, 0])
    plt.legend()
    plt.subplot(212)
    for i, psd in enumerate(psds[:5]):
        plt.loglog(freqs, psd, label=f'Ch {i+1}')
    band_freqs = [4, 8, 13, 30]
    for f in band_freqs:
        plt.axvline(x=f, color='k', linestyle='--', alpha=0.3)
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
