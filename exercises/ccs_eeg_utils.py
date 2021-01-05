from osfclient import cli
import os
from mne_bids.read import _from_tsv,_drop
import mne
import numpy as np


def read_annotations_core(bids_path,raw):
    tsv=os.path.join(bids_path.directory,bids_path.update(suffix="events",extension=".tsv").basename)
    _handle_events_reading_core(tsv,raw)

def _handle_events_reading_core(events_fname, raw):
    """Read associated events.tsv and populate raw.
    Handle onset, duration, and description of each event.
    """
    events_dict = _from_tsv(events_fname)

    if ('value' in events_dict) and ('trial_type' in events_dict):
        events_dict = _drop(events_dict, 'n/a', 'trial_type')
        events_dict = _drop(events_dict, 'n/a', 'value')

        descriptions = np.asarray([a+':'+b for a,b in zip(events_dict["trial_type"],events_dict["value"])], dtype=str)  
        
    # Get the descriptions of the events
    elif 'trial_type' in events_dict:
          
        # Drop events unrelated to a trial type
        events_dict = _drop(events_dict, 'n/a', 'trial_type')
        descriptions = np.asarray(events_dict['trial_type'], dtype=str)
          
    # If we don't have a proper description of the events, perhaps we have
    # at least an event value?
    elif 'value' in events_dict:
        # Drop events unrelated to value
        events_dict = _drop(events_dict, 'n/a', 'value')
        descriptions = np.asarray(events_dict['value'], dtype=str)
    # Worst case, we go with 'n/a' for all events
    else:
        descriptions = 'n/a'
    # Deal with "n/a" strings before converting to float
    ons = [np.nan if on == 'n/a' else on for on in events_dict['onset']]
    dus = [0 if du == 'n/a' else du for du in events_dict['duration']]
    onsets = np.asarray(ons, dtype=float)
    durations = np.asarray(dus, dtype=float)
    # Keep only events where onset is known
    good_events_idx = ~np.isnan(onsets)
    onsets = onsets[good_events_idx]
    durations = durations[good_events_idx]
    descriptions = descriptions[good_events_idx]
    del good_events_idx
    # Add Events to raw as annotations
    annot_from_events = mne.Annotations(onset=onsets,
                                        duration=durations,
                                        description=descriptions,
                                        orig_time=None)
    raw.set_annotations(annot_from_events)
    return raw

# taken from the osfclient tutorial https://github.com/ubcbraincircuits/osfclienttutorial
class args:
    def __init__(self, project, username=None, update=True, force=False, destination=None, source=None, recursive=False, target=None, output=None, remote=None, local=None):
        self.project = project
        self.username = username
        self.update = update # applies to upload, clone, and fetch
        self.force = force # applies to fetch and upload 
        # upload arguments:
        self.destination = destination
        self.source = source
        self.recursive = recursive
        # remove argument:
        self.target = target
        # clone argument:
        self.output = output
        # fetch arguments:
        self.remote = remote
        self.local = local

def download_erpcore(task="MMN",subject=1,localpath="local/bids/"):
    project = "9f5w7" # after recent change they put everything as "sessions" in one big BIDS file
            
    arguments = args(project) # project ID
    for extension in ["channels.tsv","events.tsv","eeg.fdt","eeg.json","eeg.set"]:
        targetpath = '/sub-{:03d}/ses-{}/eeg/sub-{:03d}_ses-{}_task-{}_{}'.format(subject,task,subject,task,task,extension)
        print("Downloading {}".format(targetpath))
        arguments.remote = "\\ERP_CORE_BIDS_Raw_Files/"+targetpath
        arguments.local = localpath+targetpath
        cli.fetch(arguments)


def simulate_ICA(dims=4):
    
    A = [[-0.3,0.2],[.2,0.1]]
    sample_rate = 100.0
    nsamples = 1000
    t = np.arange(nsamples) / sample_rate

    s =[]

    
    # boxcars
    s.append(np.mod(np.array(range(0,nsamples)),250)>125)
    # a triangle staircase + trend
    s.append((np.mod(np.array(range(0,nsamples)),100) + np.array(range(0,nsamples))*0.05)/100)
    if dims == 4:
        A = np.array([[.7,0.3,0.2,-0.5],[0.2,-0.5,-0.2,0.3],[-.3,0.1,0,0.2],[-0.5,-0.3,-0.2,0.8]])
        
        # some sinosoids
        s.append(np.cos(2*np.pi*0.5*t) + 0.2*np.sin(2*np.pi*2.5*t+0.1) + 0.2*np.sin(2*np.pi*15.3*t) + 0.1*np.sin(2*np.pi*16.7*t + 0.1) + 0.1*np.sin(2*np.pi*23.45*t+.8))
        # uniform noise
        s.append(0.2*np.random.rand(nsamples))
    x = np.matmul(A,np.array(s))
    return x



def spline_matrix(x,knots):
    # bah, spline-matrices are a pain to implement. 
    # But package "patsy" with function "bs" crashed my notebook...
    # Anyway, knots define where the spline should be anchored. The default should work
    # X defines where the spline set should be evaluated.
    # e.g. call using: spline_matrix(np.linspace(0,0.95,num=100))
    import scipy.interpolate as si

    x_tup = si.splrep(knots, knots, k=3)
    nknots = len(x_tup[0])
    x_i = np.empty((len(x),nknots-4))
    for i in range(nknots-4):
        vec = np.zeros(nknots)
        vec[i] = 1.0
        x_list = list(x_tup)
        x_list[1] = vec.tolist()
        x_i[:,i] = si.splev(x, x_list)
    return x_i


def ex8_simulateData(width=40,n_subjects=15,signal_mean=100,noise_between = 30,noise_within=10,smooth_sd=4,rng_seed=43):
    # adapted and extended from https://mne.tools/dev/auto_tutorials/discussions/plot_background_statistics.html#sphx-glr-auto-tutorials-discussions-plot-background-statistics-py
    rng = np.random.RandomState(rng_seed)
        # For each "subject", make a smoothed noisy signal with a centered peak
    
    X = noise_within * rng.randn(n_subjects, width, width)
    # Add three signals
    X[:, width // 6 * 2, width // 6*2] -= signal_mean/3*3 + rng.randn(n_subjects) * noise_between
    X[:, width // 6 * 4, width // 6*4] += signal_mean/3*2 + rng.randn(n_subjects) * noise_between
    X[:, width // 6 * 5, width // 6*5] += signal_mean/3*2 + rng.randn(n_subjects) * noise_between
    # Spatially smooth with a 2D Gaussian kernel
    size = width // 2 - 1
    gaussian = np.exp(-(np.arange(-size, size + 1) ** 2 / float(smooth_sd ** 2)))
    for si in range(X.shape[0]):
        for ri in range(X.shape[1]):
            X[si, ri, :] = np.convolve(X[si, ri, :], gaussian, 'same')
        for ci in range(X.shape[2]):
            X[si, :, ci] = np.convolve(X[si, :, ci], gaussian, 'same')
    #X += 10 * rng.randn(n_subjects, width, width)            
    return X