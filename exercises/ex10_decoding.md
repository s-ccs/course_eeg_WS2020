# Signal processing and analysis of human brain potentials (EEG) [Exercise 10]


### The EEG Motor Movement/Imagery Dataset
Information on the dataset at hand can be found [here](https://physionet.org/content/eegmmidb/1.0.0/) - a total of 109 subjects exist.

### Big picture:

Subjects imagine opening left & right hand or hand & feet. We want to decode which they do, in case they are doing that for real, or when they are just imagining it (brain reading 🤯!)

- We will use Common Spatial Patterns to get a good feature space and LinearDiscriminatAnalysis as a simple decoder. Of course you can always change things up and see how it changes.

- We will use cross-validation to preclude overfitting

- We will apply the weights over all timepoints to get a score across time

### Let's get started
Load the data using
```python
epochs = ccs_eeg_utils.get_classification_dataset()
```
Subjects imagine opening left & right hand or hand & feet (you could change the type of get_classification_dataset() to get e.g. trials for left/right decoding, have a look at the function). Our training data should exclude the evoked response, because it will not be sustained throughout the trial. We will make a copy of the epochs and crop it between 1 and 2 seconds (`epochs_train.crop(tmin=1.,tmax=2.)`)

**T:** To get a first look at the training data, 1) average the epochs_train over time and plot the channels C3 and C4 as x/y axis in a scatter plot. Color the datapoints according to the labels. Data you can get using `.get_data(picks=["C3","C4"])`, labels via `.events`

**Q:** Would this be easy or difficult to separate with a linear classifier?


### A quick note on statistics
In a real decoding study, you'd run the decoder for each subject. This would give you a mean accuracy value per subject, which you would put into a significance test (best in a permutation test, because accuracies don't follow a normal distribution).