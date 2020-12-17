# Signal processing and analysis of human brain potentials (EEG) [Exercise 4]
## Overview
**T:** Load simulation dataset by `x = ccs_eeg_utils.simulate_ICA(dims=2)` and plot it. We will write simple ICA algorithm to try to return the original signals

Remember that for ICA we have to undo a scaling and a rotation. The scaling we can do by whitening our signal `x`. The sphering (=whitening) matrix is the inverse of the matrix-squareroot of the covariance matrix of x.

In order to whiten (`x_white`), we have to remove the mean of `x` and then calculate the matrix product with the sphering matrix `sph*x`.
Now we are ready to try a extermely simple, naive, restricted and stupid ICA algorithm:

We simply rotate the signal using a 2D rotation matrix and for each rotatio calculate the kurtosis

```python
turn =lambda k: np.reshape(np.array([np.cos(k), np.sin(k), -np.sin(k), np.cos(k)]),(2,2))
```

(pseudocode)

```
for t in 0:pi
    x_bar = turn(t) * x_white
    abs(kurtosis(x_bar))
```

The solution to ICA would be then `argmax(kurtosis_list)`.

**T:** Plot the solution! 

**Bonus** If you want to be fancy, you can also generate an animation linking kurtosis +  rotating the datapoints + marginal histograms together

**T:** Next we will use the infomax algorithm implemented in `mne` (you could try implementing it yourself, but I found an effective adjustment of learning rate quite tricky).
you can call the infomax algorithm using `mne.preprocessing.infomax(x.T,verbose=True)`. Run it on `x = ccs_eeg_utils.simulate_ICA(dims=4)` and plot the signals before and after.


## ICA on EEG data
**T:** Now we are ready to run ICA on real EEG data. Select a dataset from a previous exercise and start the ICA (you can downsample the data to speed up ICA calculation
`raw.resample(100)`).
```python
from mne_bids import (BIDSPath,read_raw_bids)
import mne_bids
bids_root = "../local/bids"
subject_id = '002'


bids_path = BIDSPath(subject=subject_id,task="P3",session="P3",
                     datatype='eeg', suffix='eeg',
                     root=bids_root)

raw = read_raw_bids(bids_path)
ccs_eeg_utils.read_annotations_core(bids_path,raw)
raw.load_data()
raw.filter(0.5,50, fir_design='firwin')
raw.set_montage('standard_1020',match_case=False)

```

Generate an ICA object
`ica= mne.preprocessing.ICA(method="fastica")`

fit the ICA on the data.
`ica.fit(raw,verbose=True)`

After the fit (can take some minutes) you can plot the component using `ica.plot_components()`

If you want to inspect a specific component, you can select it using `ica.plot_properties(raw,picks=[3])`. 

In order to exclude components, write: ica.exclude = [3,4,16]

You can then compare the EEG before & after using:
```python
# ica.apply() changes the Raw object in-place, so let's make a copy first:
reconst_raw = raw.copy()
ica.apply(reconst_raw)

raw.plot()
reconst_raw.plot()  
```
Or use one of MNEs functionalities: ```ica.plot_overlay(raw,exclude=[1,8,9])`` 
