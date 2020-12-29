# EEG Semester Project

The goal of this project is to analyse and document a EEG dataset using MNE-Python.

How I will grade the projects can be seen in [grading](grading.md). I value line of thinking and documented motivation higher than results. I want to see that you understand, what you are doing.

## Which Dataset?
You can choose one of three datasets from the ERP-CORE [download from here]( https://figshare.com/s/5dcdc5388d4b3f37296d):

- P300: A visual oddball experiment with a prolonged effect at 300ms.
- N170: A face-viewing experiments, with an effect of faces at 170ms
- N400: A language experiment featuring a prolonged negativity at 400ms around central electrodes

You can find further information on the respective tasks in the [ERP-Core manuscript](https://doi.org/10.1016/j.neuroimage.2020.117465)

**Important**: There is no need to preprocess / clean all subjects. I provide ICA, cleaning times and bad channels for subjects all subjects [here (bundled with raw data)]( https://figshare.com/s/5dcdc5388d4b3f37296d) find scripts to easily load those in ../exercises/ccs_eeg_semesterproject.py). You should preprocess & clean **3** subjects yourself and provide/document the cleaning times / bad channels for me. As long as you document the bad components of the ICA, I see no need to send me the ICA-decomposition.

## What should the project contain?
- Preprocessing
        Filtering, re-referencening, ICA
- Data cleaning:
        Time, channel and subjects
- ERP peak analysis
        Extract the study-relevant ERP peak subjectwise (e.g. one value per subject) and statistically test them. *RQ: On which ERP-peaks do we find major difference between the conditions?*

Choose 2 out of 4 (including statistics):
- Mass Univariate
        Use a multiple regression of the main experimental contrast, controlling for reaction time (you need to calculate RT yourself). *RQ: When/Where do we find differences between our conditions? Is there an influence of reaction time?*
- Decoding analysis
        Decode the main contrast of the experiment across time *RQ: When is information about the conditions in our data available?*
- Source space
        Use source localization to visualize the source of the main experimental contrast *RQ: Where does our effect come from?*
- Time Frequency analysis
        Calculate an induced time-frequency analysis of the main experimental contrast *RQ: What oscillations underley our effect of interest?*


## Where do I get the data?
You can make use of scripts from the github.
For this you need to install the python package: osfclient
```python
import download_CORE
download_CORE.download_erpcore(task="MMN",subject=1,localpath="local/bids/")
```

## How can I get help / advice?
- I highly recommend watching the first talk in this session: https://www.crowdcast.io/e/live-meeg-2020/7 by Marijn van Vliet for an fitting introduction of analysing multiple subjects with MNE in a reproducible and documented way.
- If you prefer reading, the accompanying paper should work for you: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007358#sec017

- The MNE-documentation is quite extensive. It is worth looking into. You can also try **stackexchange** or **neurostar** for help.
- Write in the ILIAS Forum. Either others will help, or I myself will answer questions.

## FAQ (will be updated)
- *Q: The tasks are not described well enough, what exactly am I supposed to do?* - A: This is up to you. The tasks are written as if they are scientific questions that you want to answer them. This also gives you personal freedom to dive into analyses that you find most interesting.
- *Q: * - A:

## Format of report
Please share a git of your project and a report. The git can be on github or on the university gitlab. The report can be a jupyter notebook if you prefer to intermingle code and documentation. The report is there to document your decisions and thoughts along the pipeline. I am interested why you chose certain steps / parameters / analyses / visualizations.

## Deadline
Please hand in the documents until 31.03.2021
