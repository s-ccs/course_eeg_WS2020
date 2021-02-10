# Signal processing and analysis of human brain potentials (EEG) [Exercise 9]
In this exercise we will learn how to move Sensor-Space data to Source-space.

# General remarks

Source localization is hard. There are numerous moving parts, many parameters and decisions, and a complex chain of tools. Especially the part named "structural information" makes use of the Freesurfer tool, which is a tool that needs quite some time to understand the underlying functionalities, intrications and output. This box depicts how to get from an MRI to a 3D-surface/headmodel & how to align this headmodel to the coordinate system of your electrode sensors. 


![MNE Flow](https://mne.tools/stable/_images/flow_diagram.svg)

We will skip these steps completly and start with an already-segment "default" MRI (called 'fsaverage'). 

### **Important:**
 Source-reconstructions with a default-MRI (opposite of a individual MRI) introduces even more noise (=uncertainty) than already existing in "optimal" source localization. Your source-localizations should therefore be interpreted even more carefully than with individual MRIs. Never let yourself be fooled by the apparent precision of source-localizations!!

# Setup
We first need to install the python packages "pysurfer" and "mayavi" - if mayavi doesnt work,you can also try pyvista & pyvistaqt

### !! 3D Frustration alert!! 
3D Plots are annoying. They crash your system, they are slow, they are unstable. The frustration is normal and unfortunately still to be expected.

### Actual start of exercise


Next we have to do some downloading, i.e. download the average-brain MRI and the pre-computed headmodel (BEM-method)

```python

import os.path as op

import mne
from mne.datasets import eegbci
from mne.datasets import fetch_fsaverage

# Download fsaverage files
fs_dir = fetch_fsaverage(verbose=True)
subjects_dir = op.dirname(fs_dir)

# The files live in:
subject = 'fsaverage'
trans = 'fsaverage'  # MNE has a built-in fsaverage transformation
src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')
```

Next we need a dataset that we want to source localize. We will use the LIMO dataset, which has lot's of trials, but unfortauntely neither individual headmodel, nor individual electrode-positions.

```python
from mne.datasets.limo import load_data
epochs = load_data(subject=3,path='../local/limo') #
epochs.set_eeg_reference(projection=True)  # needed for inverse modeling
```



### Alignment of brains and sensors
It is of outmost importance, to align sensors and brains. This can be a very tricky task if you have individual MRIs & headmodels, because brains are mirror-symmetric and electrode locations as well. Thus R/L Flips are common.

Typically we define 3 anatomical landmarks, the nasion (between your eyes) and the Auricular Points Left and Right, a point just infront of your ear-canals. These points can be defined in your electrode-locations (e.g. using a digitizer), and are visible in the MRI. 

Luckily, for us everything is alligned already and we can plot it using:
```python
# Check that the locations of EEG electrodes is correct with respect to MRI
%matplotlib qt
#%gui qt
p = mne.viz.plot_alignment(
    epochs.info, src=src, eeg=['original', 'projected'], trans=trans,
    show_axes=True, mri_fiducials=True, dig='fiducials')

p
```
**Hint:** You can close the 3D plots using `p.plotter.close()` and later plots using `b.close()`. At least on my machine I had many crashes if I kept them floating around...



# The forward model

The forward model translates source-activity to sensor-activity. We have to provide the sensor locations (`epochs.info`), the **trans**formations of sensorlocations to BEM model (`trans`) and the actual physical spheres (bem). The default conductivities for the BEM model are already saved in the pre-computed standard BEM model.


The standard-forward model can be calculated using `fwd = mne.make_forward_solution(epochs.info, trans=trans, src=src, bem=bem, eeg=True, mindist=5.0)`

The leadfield can be extracted by `fwd["sol"]["data"]`. 

**T:** What is the shape of the leadfield and what do the dimension refer to?

**T:** select a random source-point and plot its respective sensor-topoplot (`mne.viz.plot_topomap(vector,epochs.info)`)

**T:** Next plot three following source-points. Be sure to start with 0,3,6,9... (e.g. multiply your random "starting"-index by 3).What do you observe and what does it tell you about the structure of the forward model? (hint: you could also inspect `fwd["source_nn"]`) - `plot_topomap` has an "axes" option to specify subplot-axes, be sure to put `show=False` if you want to use that.



Now we will plot the reverse, choose one electrode and see which sources are most sensitive to that electrode. Note that you only need every third sample, i.e. we are looking for the activity at the cortex in only one dimension. It is a bit more involved to collapse over all source-orientations.

To plot the vector on a 3D brain, you can use this piece of code:

```python

from mne.datasets import fetch_fsaverage
from surfer import Brain
fs_dir = fetch_fsaverage(verbose=True)
subjects_dir = op.dirname(fs_dir)

# generate Brain Plot
b = Brain('fsaverage', "lh", "white", background='white',subjects_dir=subjects_dir)

# get the surface model, get the left-hemisphere (`0`), geht the vertice-indices
v = fwd["src"][0]['vertno']
nvert = len(v)

# x is the leadfield slice spanning both hemisphere, we going to take only the first half of it.
b.add_data(x[0:nvert],vertices=v,smoothing_steps='nearest')
```



# Inverse Solutions
### My first MNE

We learned in the lecture, that the Minimum Norm Solution, is simply the pseudo-inverse of the leadfield matrix. 

**T:** To get started, plot the evoked data once more to remember what the ERP looks like. We want to zoom in the component which has its strongest activity around 150ms.

**T:** Use `from scipy.linalg import pinv` on one orientation of the Leadfield (`fwd["sol"]["data"][:,::3]`) and `@`-multiply it on your `epochs.copy().crop(tmin=0.15,tmax=0.15).average().interpolate_bads().data[:,0]` - you need to interpolate the bad channels, else they will project noise to your source-space

**T:** Plot a histogram of your source values. Do negative values make sense (solution below, don't peak ;))?

**Bonus:** instead of cropping to around 150ms, you can also calculate all timepoints and later select a timepoint, but it is a bit more cumbersome to handle everything




Once we have the vector of source-activities, we want to plot it

```python
%gui qt
from surfer import Brain
import numpy as np

# generate brain
b = Brain('fsaverage', "lh", "white", background='white',subjects_dir=subjects_dir)

# which vertices to plot?
v = fwd["src"][0]['vertno']
nvert = len(v)

# add the data to the plot - note we are using np.abs here!
b.add_data(np.abs(s[0:nvert]),vertices=v,colormap="hot")

# use some kind of sensible colormap
lim = np.percentile(np.abs(s),[30,80,98])
b.scale_data_colormap(fmin=lim[0], fmid=lim[1], fmax=lim[2], transparent=True)
```

Note the usage of np.abs around the source activity. It is generally not really possible to interpret positive / negative source activity. if you are on one side of a gyrus, the activity might be positive, on the other side it might be negative - simply because of dipole orientation. We therefore often just look at the absolute value

**Bonus:** If you wanted to plot all time-points, you can use `b.set_time(200)` to set time, or  `from surfer import TimeViewer` and `viewer = TimeViewer(b)` to get a rudimentairy GUI


### Finishing words to the manual implementation
This toy-implementation has two serious limitations: 

    - no control over how much regularisation
    - only one orientation of the Leadfield was used
    
We will fix those using the MNE functionalities next.  




# Covariance Matrices
It turns out, calculating the MNE solution via pseudoinverse is not necessarily the most versatile approach. the MNE toolbox (this is b.t.w. where the name originally came from), decided that a different parameterization is useful.

They build everything around "noise-covariance" over channels. I.e. in a period of time where no systematic activity happens, how much do channels covary? 
Why is this useful? It is useful for regularisation. Naively we could regularize all activity, but it would be more effective, if we could regularize noise more than signal. Thus, if we know something about the structure of the noise (the channel noise-covariance), we can regularize more effectively.

*As a sidenote:* This is also convenient for the LCMV-beamformer: there we would need not the noise-covariance, but the data-covariances (how do channels covary if to-be-explained activity is present [per condition])

*Another sidenote:* In case we would want to recover the original MNE solution, we'd have to input a identity-matrix as the covariance matrix.

**T:** Calculate the covariance matrix for noise and plot it:
```python
noise_cov = mne.compute_covariance(epochs, tmax=0)
noise_cov.plot(epochs.info)
```

**Q:** What does the 2d-image plot tell you?



### Inverse Operator

Next, we need to specify the inverse operator, this is where Leadfield (forward model) and noise-covariance meet. This is also where we could constrict the orientations of our dipoles to be orthogonal to the cortex & where we could use depth-correction of the leadfield.

We generate an inverse operator like this:
```python
from mne.minimum_norm import make_inverse_operator, apply_inverse
inv_default = make_inverse_operator(epochs.info, fwd, noise_cov, loose=0.2, depth=0.8)
```
**T:** Generate three more operator, one with loose=1, allowing for all dipole orientations, one with loose=0, enforcing strict orthogonal orientation (don't do that) and one with loose=0.2, but depth=0. - deactivating depth weighting.



### Applying the inverse
Next, we have to apply the inverse operator.
For this, we still need to define how much regularisation we want to apply. If we expect noisy data, we should put lot's of regularisation. If we expect high SNR, there should be less regularisation. Here the MNE implementation really shines: We can easily define a Signal-To-Noise ratio and translate it to a regularisation parameter that will fit.
```python
snr = 10.0
lambda2 = 1.0 / snr ** 2
```

**T:** calculate the inverse solution and get the stc (source time course) for the `inv_default` - choose the MNE algorithm in the function `mne.minimum_norm.apply_inverse`
**T:** Plot it! `brain = stc.plot(time_viewer=True,hemi="both")`


**Bonus:** You can also plot the brain activity on a "inflated" or "flat" brain using `surface = "flat"` (or inflated respectively). This can be very helpful in comparing conditions etc. - but especially the flat map will be very hard to read for everyone who is not a brain-anatomy-expert



# Comparing Inverse Solutions
We will do a set of source-solution comparisons. Note that this is just one example, and just a subset of all possible parameters. It might give you a small glimpse, and maybe even only a missleading intuition. But still, at least it will give you a starting point for experience in source localization.

### Comparing our dipole-orientation & depth models
I feel like this exercise is already pretty long, so I will give you larger chunks of code.

```python
# plotting parameters
brain_kwargs = dict(views="lateral",hemi='split', size=(800, 400), initial_time=0.15,time_viewer=False,time_unit='s',show_traces=False)

# getting larger figures
plt.rcParams['figure.dpi'] = 100 
plt.rcParams["figure.figsize"] = (20,15)

# a list of all our inverse operators
sourceList = [inv_default,inv_loose0,inv_loose1,inv_depth0]

#loop over inverse operators
for (ix,inv) in enumerate(sourceList):

    # calculate the stc
    s = apply_inverse(epochs.average(), inv, lambda2, 'MNE', verbose=True)#, pick_ori='vector')
    
    # plot it
    h = s.plot(**brain_kwargs)

    # grab a png from it
    img = ccs_eeg_utils.stc_plot2img(h,closeAfterwards=False)

    # add the png to a subplot
    ax = plt.subplot(2,2,ix+1).imshow(img)
    plt.axis('off')

```

**Bonus-Q:** Why did MNE suddenly decide to plot pos/neg for the loose=0 (fixed orientation) instead of abs?

### Comparing algorithms
Next we will compare the four different minimum-norm algorithms implemented in MNE:
`['MNE','sLORETA','eLORETA','dSPM']`
adapt the previous script to use `inv_default` for all of them and plot the solutions again.


### Final exploration: Different regularisation
Adapt the above script once more, and apply different SNRs (e.g. `[0.1,2,10,50]`). What do you observe?
Make note of the MNE text-output, it tells you how much % of your actual observed data is explained by the solution. Do they roughly match your expectations?


# Some further notes:

- There are no ideal parameters or algorithms. Different combinations of parameters will introduce different assumptions will lead to potentially very different solutions. One conclusion from our exploration with a single subject might be: Activity comes from visual cortex, but maybe this is something we knew before. 

- So far, we were projecting ERPs conditionwise to the source space. But you can also plot subtractions of conditions, highlighting where the effects occured. Further, you could even directly project betas or difference-waves to source space.

- If you have multiple subjects, and you want to perform statistics, you need to match the head-models of subjects. Given that we do not have individual headmodels, this is no problem for us. All vertices / dipoles are at exactly the same position for all subjects - convenient!

- Performing statistics over subjects works [quite similarly (check out this tutorial)](https://mne.tools/dev/auto_tutorials/stats-source-space/plot_stats_cluster_spatio_temporal.html#sphx-glr-auto-tutorials-stats-source-space-plot-stats-cluster-spatio-temporal-py) to previous analysis. In case of cluster-permutation tests, adjacency/neighbourhood needs to be defined in 3D space on the surface. Computation time might be increased enourmously.

- All of our source-space analysis have been performed on the surface of the cortex. This is where the gray matter is, and where we hypothesize that our EEG signal is produced. But we might be wrong, there might be deep-sources, e.g. hippocampus or cerebellum also generating our potentials. Thus instead of restricting our source analysis to the surface, we could also make use of the whole 3D volume of the brain. This is less well documented in MNE, but also possible. In some sense it is a question of preference.

- Again my warning: Do not overinterpret your source analysis results! You might be centimeters away from your real activity.
