# Signal processing and analysis of human brain potentials (EEG) [Exercise 3]
## Cleaning Data
**T:** Download the `P3` dataset for Subject `30` (before 2020-11-20 12.53 this stated subject 9, sorry!) from the [ERPcore](https://osf.io/thsqg/).

**T:** Go through the dataset using the MNE explorer and clean it. You can use `raw.plot()` for this. If you are working from a jupyter notebook, try to use `%matplotlib qt` for better support of the cleaning window. To get an understanding how the tool works, press `help` or type `?` in the window. (Hint: You first have to add a new annotation by pressing `a`)

**T:** While going through the dataset, mark what you observe as bad electrodes. Those are saved in `raw.info['bads']`. The channels can be interpolated with `raw.interpolate_bads()` or `epoch.interpolate_bads()`. Compare the channel + neighbours before and after. Did the interpolation succeed? (If you are interested in the mathematical details of spline interpolation, checkout this https://mne.tools/dev/overview/implementation.html#id26)
Hint: You need channel locations to run the interpolation which you can get by using the default-standardized channel locations `raw.set_montage('standard_1020',match_case=False)`

**T:** Save the annotations to a file. Best practice is to use a csv file of sorts e.g. using `raw.annotations.save(filename)`. Try to subsetting for `BAD_` first. Bonus: Save it in a BIDS derivate folder according to the BIDS guidelines.

**T:** In MNE, if annotations with `BAD_` exist, the epoching function automatically removes them. We are now ready to compare ERP results with and without removal of bad segments. Epoch the data, the respective bad segments will be removed automatically. Compare the two ERPs for the channel `Cz`

**T:** In the epoching step, we can also specify rejection criterion for a peak-to-peak rejection method

```python
reject_criteria = dict(eeg=100e-6,       # 100 µV
                       eog=200e-6)       # 200 µV
epochs = mne.Epochs(raw, events, reject=reject_criteria,reject_by_annotation=False)
```

Compare these epochs with your manual rejection and with the ERPs without rejection. Plot a single channel `Cz` overlaying all three "solutions".

**Bonus:** We are going to add to our comparison by using **autoreject** in MNE python. Have a look at https://autoreject.github.io/ for installation and usage examples. Hint: You need channel locations to run autoreject which you can get by using the default-standardized channel locations `raw.set_montage('standard_1020',match_case=False)`

**Bonus:** We can also try to circumvent cleaning by using trimmed / winsorized means. For this, the `epochs.average(method=X)` function can be exchanged with a averaging callback. Scipy has comparable functions that you can try out and compare.
