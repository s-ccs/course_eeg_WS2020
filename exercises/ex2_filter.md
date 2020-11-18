# Signal processing and analysis of human brain potentials (EEG) [Exercise 2]
## Overview
In this exercise we will learn a lot about filters.

## Simulate a simple EEG signal
We start out with a simple signal:

```python
from numpy import cos, sin, pi,  arange

sample_rate = 100.0
nsamples = 400 # fixed at 11.11.2020
t = arange(nsamples) / sample_rate
x = cos(2*pi*0.5*t) + 0.2*sin(2*pi*2.5*t+0.1) + \
        0.2*sin(2*pi*15.3*t) + 0.1*sin(2*pi*16.7*t + 0.1) + \
            0.1*sin(2*pi*23.45*t+.8)
```   
Plot the signal against time.

## Transform to fourier space
We will run the FFT algorithm and plot the magnitude response ($log10(abs(fft(x))))$).

## A simple filter
a very simple frequency filter is to set the unwanted amplitude of the fourier components to something close to zero.  We have to be a tad careful not to remove the phase information though.
Your task is therefore:
    - split the complex fourier result into *angle* and *magnitude* 
    - set the respective magnitudes to zero (we start with a lowpass filter: `magnitude[30:370] = 0`)
    - combine angle and magnitude back to a complex fourier coefficient ($m*e^(1j*ang)$)
    - apply the inverse FFT
    - plot the signal with what you started out

## Highpass instead of lowpass
Repeat the steps from above, but this time, remove the low frequency components


## What happens to the frequency and time response if we add "artefacts"?
 Add a DC-offset (a step-function) starting from `x[200:]` and investigate the fourier space. Filter it again (low or high pass) and transfer it back to the time domain and investigate the signal around the spike.

 ## Impulse Response Function
 To get a bit deeper understanding of what is going on, have a look at the fourier transform of a new impulse signal (e.g. 1:400 => 0. and 200 => 1.). What do you observe?
 Why would we see ringing if we put most of the coefficients to 0?

 ## Filtering EEG data
Usually we would not built our own filters - but understanding the properties is still very important! We will load our data from last time again:
```python
from mne_bids import (BIDSPath,read_raw_bids)
import mne_bids
import importlib
import ccs_eeg_utils

bids_root = "../local/bids"
subject_id = '002'


bids_path = BIDSPath(subject=subject_id,task="P3",session="P3",
                     datatype='eeg', suffix='eeg',
                     root=bids_root)
raw = read_raw_bids(bids_path)
ccs_eeg_utils.read_annotations_core(bids_path,raw)
raw.load_data()
```


**T:** Choose the channel "Pz", plot the channel (previous HW it was "Cz")

**T:** Plot the fourier space using `raw.plot_psd()`

**T:** Now we filter using `raw.filter()`, specify a highpass of 0.5Hz and a lowpass of 50Hz. Plot the fourier spectrum again.

**T:** Plot the channel again, did the filter work as indented?

**Bonus** If you want, you can compare the ERP with and without filtering. You can also use "invalid" filter settings - HP up to 2-5Hz, lowpass until 10-20Hz. I say invalid here, because usually with such ranges, you would filter out results that you are actually interested in.

## Bonus: Electrical Artefacts
Too late to fix the lecture, but instead of notch filtering 50/60Hz artefacts, one can also try to regress it out in smarter ways. A good tool for this is *Zap_Line* with a python implementation here: https://github.com/nbara/python-meegkit/. There are also several robust detrending methods, which could potentially replace highpass filters in the future. But more work needs to be invested to see how results compare. These methods are not (yet) common.
