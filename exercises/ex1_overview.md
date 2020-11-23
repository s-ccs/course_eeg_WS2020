# Signal processing and analysis of human brain potentials (EEG) [Exercise 1]
## General remarks to exercises
These exercises are comparatively easy and not very involved - this is by design. They are designed to help you think in different ways about the lecture material. The exercises are highly recommended but not mandatory. It is best if you generate a jupyter notebook for each exercise and upload it every week until Wednesday 18.00 (some exercises are over two weeks and specified as such in the course-overview table in Ilias).

You are encouraged to work in groups of 2. 

Exercises are only graded pass/failed and if requested I will try to provide feedback. Again: Exercises are not mandatory to pass the course. The course-grade is solely based on the semesterproject.

## Overview
In this exercise we will install the mne-python toolbox, download a example dataset, make some basic visualizations and epoch, average and visualize the resulting ERPs.

## Install MNE toolbox
run `pip install mne`
or if you like conda:
`conda install -c conda-forge mne`

Test the installation by
`import mne`

## Load data & plot continuous EEG
We will be using a typical P3 oddball dataset. We expect a positive response over parietal/central electrodes (Cz/Pz) starting at 300-400ms. Something like this: https://www.neurobs.com/manager/content/docs/psychlab101_experiments/Oddball%20Task%20(Visual)/description.html
If you want to read the details you can find it here (the dataset is also part of the semester project): https://psyarxiv.com/4azqm/. You can also investigate the `sub-002_task-P3_eeg.json` for a task description which is automatically downloaded.


```
pip install osfclient
pip install mne-bids
```

### Update 2020-11-04
Unfortunately, the osf-repo was recently moved and all tasks were put together. Due to a quirky implementation of osfclient, it blindly (recursively) iterates over all files and checks each against the to-be-fetched one. Thus it can take minutes for a single file to be downloaded (and we run into API-timeouts etc.). Therefore the following code will likely not work
```python
import ccs_eeg_utils
ccs_eeg_utils.download_erpcore(task="P3",subject=2,localpath="../local/bids/")

```
And you have to download the following files manually (for now, I will provide better links soon) from osf.io/
`["channels.tsv","events.tsv","eeg.fdt","eeg.json","eeg.set"]`
and put them into `../local/bids/sub-002/ses-P3/eeg/sub-002_ses-P3_task-P3_XYZ` with `XZY` being the filename.

```python
# Load the data
from mne_bids import (BIDSPath,read_raw_bids)

# path where to save the datasets.
bids_root = "../local/bids"
subject_id = '002' # recommend subject 2 for now


bids_path = BIDSPath(subject=subject_id,task="P3",session="P3",
                     datatype='eeg', suffix='eeg',
                     root=bids_root)

# read the file
raw = read_raw_bids(bids_path)
# fix the annotations readin
ccs_eeg_utils.read_annotations_core(bids_path,raw)

```

**T:** Extract a single channel and plot the whole timeseries. You can directly interact with the `raw` object, e.g. `raw[1:10,1:5000]` extracts the first 10 channels and 2000 samples.
**Q:** What is the unit/scale of the data (in sense of "range" of data)?

**T:** Have a look at `raw.info` and note down what the sampling frequency is (how many EEG-samples per second)

## Epoching 

**T:** We will epoch the data now. Formost we will cut the raw data to one channel using `raw.pick_channels(["Cz"])` - note that this will permanently change the "raw" object and "deletes" alle other channels from memory. If you want rather a copy you could use `raw_subselect = raw.copy().pick_channels(["Cz"]))`.


**T** Let's investigate the annotation markers. Have a look at raw.annotations. These values reflect the values in the bids `*_events.tsv`  file (have a look at the files in `../local/bids/sub-002/sub-002_task-P3_events.tsv`). BIDS is a new standard to share neuroimaging and other physiological data. It is not really a fileformat, but more of a folder & filename structure with some additional json files. I highly recommend to put your data into bids-format as soon as possible. It helps you stay organized and on top of things!


**T** MNE-speciality: We have to convert annotations to events with `evts,evts_dict = mne.events_from_annotations(raw)`. Have a look at evts - it shows you the sample, the duration and event-id (with the look-up table evts_dict). In this case we only want to look at stimulus evoked responses, so we subset the event table (note: this could be done after epoching too)

```python
# get all keys which contain "stimulus"
wanted_keys = [e for e in evts_dict.keys() if "stimulus" in e]
# subset the large event-dictionairy
evts_dict_stim=dict((k, evts_dict[k]) for k in wanted_keys if k in evts_dict)
```

**T** Epoch the data with `epochs = mne.Epochs(raw,evts,evts_dict_stim,tmin=-0.1,tmax=1)`

**T** Now that we have the epochs we should plot them. Plot all trials 'manually', (without using mne's functionality) (`epochs.get_data()`).
**Q** What is the unit/scale of the data now?

## My first ERP

**T** But which epochs belong to targets and which to distractors? This is hidden in the event-description. Using the following lines you can find out which indices belong to which trial-types
```python
target = ["stimulus:{}{}".format(k,k) for k in [1,2,3,4,5]]
distractor = ["stimulus:{}{}".format(k,j) for k in [1,2,3,4,5] for j in [1,2,3,4,5] if k!=j]
```
Now index the epochs `evoked = epochs[index].average()` and average them. You can then plot them either via `evoked.plot()` or with `mne.viz.plot_compare_evokeds([evokedA,evokedB])`.

**Q** What is the unit/scale of the data now? Set it into context to the other two scales you reported (**Q**'s higher up).

