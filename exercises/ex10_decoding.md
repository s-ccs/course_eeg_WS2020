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


### CSP Feature Selection
We can define a CommonSpatialPatterns object using `csp = mne.decoding.CSP(n_components=2)`

To fit the CSP we have to give it the data and the labels. For now we just want to look at the CSP, not run a classifier for it, so we dont worry about any overfit etc.

**T:** `csp.fit_transform(epochs_data, labels)` will fit it and `csp.plot_filters(epochs.info)` and `csp.plot_patterns(epochs.info)` will plot filter and activation. 

**Q:** Let's say you invite a subject again, but are allowed to only measure 5 channels not the 64. Which of the two plots would you choose to inform which channels to measure? In other words, does any of the plot tell you where the information to decode is strongest?

**T:** Finally, let's weight/transform the data to the fitted CSP components using `csp_data = csp.transform(data)`. Note that because `csp(...,transform_into="average_power")` is set by default, we will get data without a time-dimension, thus already aggregated. Plot the datapoints against each other, how easy is it now to define a classifier?

### LDA Classification
Let's use the LDA classifier (you could use any other if you fancy, up to you - LDA is a fast and simple one).

You need to:
1. Construct the classifier  via 
```python
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

lda = LinearDiscriminantAnalysis()
``` 
2. Reshape the csp_data to conform to labels x features (2D instead of 3D) e.g. using `flattenData = csp_data.reshape(csp_data.shape[0],-1)`

3. Fit the LDA using `lda.fit(data,labels)`

4. Score it using `lda.score(data,labels)`

*Note: we are doing a cardinal sin: Training and testing on the same data. How to fix that is next.*

**T:** How well can you classify?

### Crossvalidation
To work against overfitting, we use crossvalidate and use some functions from sklearn for it.
We will use a stratifiedShuffleSplit, which will split our data in training and test sets, but in a stratified way. Thus we dont have to worry about under/oversampling between our classes for now.

```python
cv = sklearn.model_selection.StratifiedShuffleSplit(10, test_size=0.2, random_state=42)
cv_split = cv.split(epochs_train.get_data(),labels)
```

Next we can walk though each test/train, fit CSP, fit LDA and evaluate. I will give you the skeleton and you only have to fill in the XXX to speed up programming :).

```python
score_list = []
for train_idx, test_idx in cv_split:
    y_train, y_test = labels[train_idx], labels[test_idx]

    csp.fit_transform(epochs_train.get_data()[XXX_idx], y_XXX)
    X_train = csp.transform(epochs_train.get_data()[XXX_idx])
    X_test  = csp.transform(epochs_train.get_data()[XXX_idx])

    lda.fit(X_XXX, y_XXX) 
    score = lda.score(X_XXX,y_XXX)
    score_list.append(score)
```
### Decoding via Pipeline
Typically you would like to use a pipeline-system to easily exchange components. We are using the scikit pipeline
We need several incredients: 

1. Training-Data & labels
2. Pipeline with feature selection (CSP) & Classifier (LDA)
3. Cross-Validation scheme
 
#### Implementation

2. CSP and LDA & pipeline
 ```python
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import mne.decoding
lda = LinearDiscriminantAnalysis()
csp = mne.decoding.CSP(n_components=2) # default is 4, typically youd like to do a nested cross-val hyperparam search. 2 is likely too low
% and the pipeline simply:
pipe = sklearn.pipeline.Pipeline([('CSP', csp), ('LDA', lda)])
 ```


3. The sklearn Cross-validation pipeline is run like this
 ```python
import sklearn.model_selection
cv = sklearn.model_selection.StratifiedShuffleSplit(10, test_size=0.2, random_state=0)
scores = sklearn.model_selection.cross_val_score(pipe, trainingData, labels, cv=cv, n_jobs=1)
 ```

**Q:** What is the accuracy of the classifier? What is the chance level?

## Extensions 
This formulations with the pipelines etc. is neat, because we can simply exchange parts of the pipeline and see what happens.
Note though, that you are performing multiple testing and are very easily overfitting to your dataset.

Thus in principle, you would like to explore some options with one set of subjects, then test the pipeline on another set of subjects. But this is a bit too involved for the homework.

### Remove CSP
Instead of applying a feature selection, maybe we can learn from the "raw" data? 
**T:** Replace the "csd" in the pipeline with `mne.decoding.Vectorizer()`, this will ensure the reshaping of the features we performed earlier.

**Q:** What is the accuracy now?

### Classify over time
Next we will fit a classifier for each timepoint and test it on that timepoint (you have to use the simple pipeline, see below)
For this the convenience function `timeDecode = mne.decoding.SlidingEstimator(pipe)` exists. This function performs the pipeline on the last dimension (which is currently time).

Because we will get multiple scores per cross-val, we also have to switch our scorer to `mne.decoding.cross_val_multiscore(timeDecode,...)`.

**T:** Plot the performance against time
**Bonus T:* You can also use `mne.decoding.GeneralizingEstimator(...)` to get the temporal decoding matrix (increased runtime warning)

You might be surprised - or not - by the performance you observed. Applying this to a dataset with actual evoked responses, will likely be much more satisfactory.

The reason seems clear, we would need CSP in between. But CSP needs multiple timepoints and doesn't work with SlidingEstimator. We'd have to do it manually.

### A quick note on statistics
In a real decoding study, you'd run the decoder for each subject. This would give you a mean accuracy value per subject, which you would put into a significance test (best in a permutation test, because accuracies don't follow a normal distribution).