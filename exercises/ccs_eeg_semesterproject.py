
import os
import mne
import numpy as np
from mne_bids import (BIDSPath, read_raw_bids)

def _get_filepath(bids_root,subject_id):
    bids_path = BIDSPath(subject=subject_id,task="P3",session="P3",
                     datatype='eeg', suffix='eeg',
                     root=bids_root)
    # this is not a bids-conform file format, but a derivate/extension. Therefore we have to hack a bit
    fn = bids_path.fpath.__str__()[0:-3]
    return fn

def load_precomputed_ica(bids_root,subject_id):
    fn = _get_filepath(bids_root,subject_id)+'ica'

    # import the eeglab ICA. I used eeglab because the "amica" ICA is a bit more powerful than runica
    ica = mne.preprocessing.read_ica_eeglab(fn+'.set')
    
    # Potentially for plotting one might want to copy over the raw.info, but in this function we dont have access / dont want to load it
    #ica.info = raw.info
    ica._update_ica_names()
    badComps = np.loadtxt(fn+'.tsv',delimiter="\t")
    return ica,badComps

def load_precomputed_badData(bids_root,subject_id):
    fn = _get_filepath(bids_root,subject_id)
    annotations = mne.read_annotations(fn+'badSegments.csv')
    badChannels = np.loadtxt(fn+'badChannels.tsv',delimiter='\t')
    return annotations,badChannels