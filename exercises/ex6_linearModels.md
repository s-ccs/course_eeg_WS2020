## Statistical Analysis of N170 area using Linear Regression
*T* Load the data into a pandas dataframe. A very useful concept here is the concept of a tidy dataframe. The idea is, that every observation is one row of a table, where columns are potential features / descriptors + the dependent variable (the average activity between 130 and 200ms at electrode PO8 here).

```python
import pandas as pd
d = pd.read_csv("ex6_N170.csv",delimiter=",")
```
**T:** Use a plottinglibrary of your choice to visualise the simple scatter plot between some/all variables. I recommend packages *seaborn* e.g. pairplot) or *plotnine* for this. They make it easy to split up plots of continuous variables (e.g. baseline vs. PO8) by a categorical variable, e.g. *cond* (scrambled/intact).

**Q:** Can you already guess what the relationships between the variables are, solely based on the plots?


### Do-It-Yourself Linear Models
We have to generate a DesignMatrix ($X$) in order to fit our model. The designmatrix has to reflect our study design. The simplest designmatrix consists only of "1", one for each data-point, which would mean that we fit only one parameter summarizing the whole dataset.

**T:** Generate this designmatrix and fit it using the pseudo-inverse: $(X^TX)^{-1}X^TY$. I recommend to generate a function similar to this:
```python
def solve(*args):
    # generate designmatrix by stacking
    X = np.stack(args).T
    return PSEUDOINVERSE
```
Because we will need it quite often.

**Q:** What does the resulting value *mean*? Note: The result is often called a "beta"

*Note: While the pseudoinverse is great because it is easy to understand what is going on, typically we would not directly use it but rather go over a Cholesky-Decomposition first. This will greatly increase numeric stability. But right now we do not care much about that*


**T:** Now we add the condition *cond* to the designmarix (thus `PO8 ~ intercept + cond`) which differentiates between intact and scrambled images. Because this is a categorical variable we have to encode it first. For that, we need a "1" when images are intact and a "0" if they were scrambled. Fit the model

**Q:** What do the outputs mean now?

**T:** Next add a predictor for stimulus (`PO8 ~ intercept + cond + stim`) and fit it.

**Q:** What changed to the previous modelfit - *Bonus*: An idea why the size of the change is the size it is? Hint: It has to do with correlations


**T:** And an interaction (column of stimulus * column of cond)

**Q:** What do the betas/results/parameters mean now? (You might want to do the plotting of the next step to help your interpretation)


Now we have what we call a 2x2 design. Two categorical factors (often only "factor") with two levels each + the interaction. 

**T:** It is about time to plot our results! Put cond on the x, and use color for stimulus. We will reconstruct our original data first:

You should reconstruct 4 values, one for **intact faces**, one for **scrambled faces**, one for **intact cars** and one for **scrambled cars**. It migt be helpful to explicitly write down the models ($y  = 1*\beta_0 + ...$ )


## Changing Bases
We discussed in the lecture that it is possible to change the bases. We will go back to the simple example of of `Intercept + cond`. But in addition of *dummy coding* (intact == 1, scrambled == 0), we will fit a second model with *effect-coding* (intact == 0.5, scrambled = -0.5). 

**Q:** How do the betas compare of the two models? How does the interpretation change?

**Hint** If you need more you can read two of my tutorial-blogposts on this topic  [here](https://benediktehinger.de/blog/science/dummy-coding-and-effects-coding/) and [here :)](https://benediktehinger.de/blog/science/interaction-and-effect-sum-coding/) 


**T:** Now we run the full 2x2 model once with dummy and once with effect-coding. The interaction of an effect-coded model is still just the designmatrix columns multiplied with eachother

**Q:** Can you put the results together, why do they have the results they have?




### Continuous Regressors

Now it is time to involve our continuous regressor. In this case it is the baseline-value. We are following here the relatively new approach of [Alday 2019](https://onlinelibrary.wiley.com/doi/full/10.1111/psyp.13451) and instead of subtracting a baseline, we will regress it out. We did not talk about baseline correction in the lecture, this is something I will talk about at the end of the course.

In theory baseline corrections are not needed, the baseline (i.e. what happens before stimulus onset, thus "negative" time in an ERP) should be flat / noise around 0, because stimulus order is random. But in practice, we only have limited number of trials and limited randomization. Thus it might be, that we have a bias with in one condition more residual drift / low-frequency activity than in the other. This will "move" the whole ERP curve up/down and bias results later in the epoch.

Classically, baselines are simply subtracted. Thus every point of an ERP recieves the "same" baseline correction. This is equivalent to adding a known parameter to our model: `y ~ b0 * constant + b1 * cond + -1*BSL`. What we will do instead is the 2020-version, we regress the baseline. This allows us to remove less of the baseline activity (or more, but rarely happens).

**T:** Plot the PO8 actiity against the baseline (you might have done this plot at the beginning of the exercise). Split it up by cond & stim



**T:** Add the baseline as a predictor to your 2x2 model. 

**Q:** What is the resulting beta?


Typically we do not only remove the overall baseline, but condition-indivudal baselines. 

**T:** Thus we have to generate interactions with all predictors & interaction of the interactions too

**Q:** What is your interpretation of the resulting betas? For which conditions do we really need a baseline correction and how strong should it be?



## Bonus: Uncertainty & Standard Errors
This was not part of the lecture, but might be interesting nonetheless. In this exercise we talk about how we can generate errorbars to add to our 2x2 plot.

We can not only estimate the $\hat{\beta}$, our estimated parameters, but also the variance of them, giving us a handle of uncertainty. We just need some additional assumptions (normal residuals). For a derivation see [this](https://stats.stackexchange.com/questions/390836/standard-error-and-confidence-interval-for-multiple-linear-regression-in-matrix). 

It turns out, that $Var(\beta) = \sigma^2 (X^TX)^{-1}$

**T:** Implement this formula. The sqrt of the diagonal elements are your Standard-Errors, which we can use as error-bars. The $\sigma^2$ is the variance of the residuals


Now we have to apply it including our contrast vectors e.g. c = [1 0 0 0*0], or c=[1 0 1 1*0]

$$se_c = \sigma^2 c^T (X^TX)^{-1} c$$
