# Signal processing and analysis of human brain potentials (EEG) [Exercise 9]
In this exercise we will start with running STFT's semi-manually using the scipy implementation. Then we will explore TimeFrequency utilities of the MNE toolbox

## Time Frequency Analysis
Get the first signal using `sig = ccs_eeg_utils.simulate_TF(signal=1)`.  For now we will analyze a single trial, typically you'd run the STFT on each run and then average, as we will do later. The sampling rate is 500Hz

**T:** Plot the signal, it is hard to recognize anything!

**T:** Apply the stft using `scipy.signal.stft` . Systematically vary the `nperseg` from 32 to 256 in ~5 steps. Choose an `noverlap` of `0.9*nperseg`.

**T:** Plot the resulting STFTs as a colorcoded 2D plot. If you use `plt.imshow`, be sure to use `interpolation='None'`. Furthermore, `aspect="auto"` may be helpful to fixate the sizes of the plot axes and `origin='lower'` will prevent the y-axis from being inverted.

**Q:** What do you observe? Which `nperseg` is ideal for frequency-resolution, which for time-resolution? Do the oscillations overlap in time?

**T:** Change the noverlap to `0.3*n`. What changes?

## Morlet Wavelet Analysis
As discussed in the lecture, sometimes you want high temporal resolution in high frequencies and low temporal resolution in low frequencies. Wavelet transform is one way to achieve that.


**T:** Run `mne.time_frequency.tfr_array_morlet(sig.reshape(1,1,-1), sfreq=500,freqs=freqs, n_cycles=cyc)` with an appropriate set of freqs. Vary the amount of cycles (e.g `[3,4,8,16]`). Plot the results.

**Q:** Do the expected results occur?


**Bonus T:** You can also run the same scripts on other signals, e.g. `sig = ccs_eeg_utils.simulate_TF(signal=2)` or `signal =3`. Do your conclusions hold?


## Time Frequency of an EEG Dataset
Get a partially preprocessed P3 Dataset from the ERP-Core:
```
epochs = ccs_eeg_utils.get_TF_dataset(subject_id = '002',bids_root = "../local/bids")
```
We are looking only at epochs relative to the responses, which have been already extracted by the helper function. 


We want to get an overview of the power. So for starters we choose bad frequency resolution but good time resolution with a wavelet transform.

We will evaluate the TF at `freqs = np.logspace(*np.log10([5, 80]), num=25)` with 1 cycle. 
 
**T:**Run:
``` 
power_total = mne.time_frequency.tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles, return_itc=False,n_jobs=4,average=True) # ITC, inter-trial-coherence is quite similar to evoked power, it is a measure of phase consistency over trials but we havent discussed it in the lecture.
``` 


Next we will visualize all TFs at all electrodes and get an overview whats going on. If you use `%matplotlib qt` the plot will be interactive.
Choose a baseline of -.5 to 0 using the command `power.plot_topo()` 


**T:** Plot the power at electrode Cz using power.plot():
    1. Without any baseline
    2. With a baseline of your choice

**T:** Explain the general pattern you see. Can you spot differences betweem with and withot baseline?


**T:** Now lets improve upon our frequency resolution nz increasing the number of cycles to 3. Plot channel Cz with BSL correction
(-0.5,0). Tipp: you can speed up the calculation by specifying `picks="Cz"`



**T:** We also want to calculate the induced and evoked TF. For this we first calculate the induced spectrum, then subtract the total from the induced.

1. `epochs.subtract_evoked()` is a function that removes the ERP from each trial. It is a mne-consistent function that practically does:
`epochs_induced._data = epochs._data  - epochs.average().data`. Run the tfr analysis again on the induced dataset, remember that if you dont make a copy of your epochs (via `epochs.copy()`) the dataset will be overwritten in memory

2. In order to get epochs_evoked, we have to subtract total and induced. We cand do this via 
```python
power_evoked = mne.combine_evoked([power_total,power_induced],weights=[1,-1])
```
Note: you could use this function also to combine/subtract condition effects!

**T:** Visualize evoked, total & induced for electrode Cz
