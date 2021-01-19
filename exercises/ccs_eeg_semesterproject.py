
import os
import mne
import numpy as np
import pandas as pd
from mne_bids import (BIDSPath, read_raw_bids)

def _get_filepath(bids_root,subject_id,task):
    bids_path = BIDSPath(subject=subject_id,task=task,session=task,
                     datatype='eeg', suffix='eeg',
                     root=bids_root)
    # this is not a bids-conform file format, but a derivate/extension. Therefore we have to hack a bit
    # Depending on path structure, this might push a warning.
    fn = os.path.splitext(bids_path.fpath.__str__())[0]
    assert(fn[-3:]=="eeg")
    fn = fn[0:-3]
    return fn

def load_precomputed_ica(bids_root,subject_id,task):
    # returns ICA and badComponents (starting at component = 0).
    # Note the existance of add_ica_info in case you want to plot something.
    fn = _get_filepath(bids_root,subject_id,task)+'ica'

    # import the eeglab ICA. I used eeglab because the "amica" ICA is a bit more powerful than runica
    ica = mne.preprocessing.read_ica_eeglab(fn+'.set')
    #ica = custom_read_eeglab_ica(fn+'.set')
    # Potentially for plotting one might want to copy over the raw.info, but in this function we dont have access / dont want to load it
    #ica.info = raw.info
    ica._update_ica_names()
    badComps = np.loadtxt(fn+'.tsv',delimiter="\t")
    badComps -= 1 # start counting at 0
    
    # if only a single component is in the file, we get an error here because it is an ndarray with n-dim = 0.
    if len(badComps.shape) == 0:
        badComps = [float(badComps)]
    return ica,badComps
def add_ica_info(raw,ica):
    # This function exists due to a MNE bug: https://github.com/mne-tools/mne-python/issues/8581
    # In case you want to plot your ICA components, this function will generate a ica.info
    ch_raw = raw.info['ch_names']
    ch_ica = ica.ch_names

    ix = [k for k,c in enumerate(ch_raw) if c in ch_ica and not c in raw.info['bads']]
    info = raw.info.copy()
    mne.io.pick.pick_info(info, ix, copy=False)
    ica.info = info

    return ica
def load_precomputed_badData(bids_root,subject_id,task):
    # return precomputed annotations and bad channels (first channel = 0)

    fn = _get_filepath(bids_root,subject_id,task)
    print(fn)

    tmp = pd.read_csv(fn+'badSegments.csv')
    #print(tmp)
    annotations = mne.Annotations(tmp.onset,tmp.duration,tmp.description)
    # Unfortunately MNE assumes that csv files are in milliseconds and only txt files in seconds.. wth?
    #annotations = mne.read_annotations(fn+'badSegments.csv')
    badChannels = np.loadtxt(fn+'badChannels.tsv',delimiter='\t')
    badChannels = badChannels.astype(int)
    badChannels -= 1 # start counting at 0

    #badChannels = [int(b) for b in badChannels]
    return annotations,badChannels


