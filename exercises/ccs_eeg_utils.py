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
    def __init__(self, project, username=None, update=False, force=True, destination=None, source=None, recursive=False, target=None, output=None, remote=None, local=None):
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
    if task == "MMN":
        project = "5q4xs"
    elif task == "P3":
        project = "etdkz"
    elif task == "N170":
        project = "pfde9"
    elif task == "N400":
        project = "29xpq"
    else:
        raise "Bad Taskinput, can only be MMN,P3,N170 or N400"
            
    arguments = args(project) # project ID
    for extension in ["channels.tsv","events.tsv","eeg.fdt","eeg.json","eeg.set"]:
        
        targetpath = 'sub-{:03d}/eeg/sub-{:03d}_task-{}_{}'.format(subject,subject,task,extension)
        print("Downloading {}".format(targetpath))
        arguments.remote = "\\"+task+" Raw Data BIDS-Compatible/"+targetpath
        arguments.local = localpath+targetpath
        cli.fetch(arguments)
