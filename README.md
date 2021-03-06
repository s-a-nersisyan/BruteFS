# ExhaustiveFS
Exhaustive feature selection for classification and survival analysis.

## Table of Contents  
[Introduction](#introduction)  
[Installation](#installation)  
[Running ExhaustiveFS](#running-exhaustivefs)  
[Functions and classes](#functions-and-classes)  
[Tutorials](#tutorials)  
[etc](#etc)  

# Introduction
The main idea underlying ExhaustiveFS is the exhaustive search of feature subsets for constructing the most powerfull classification and survival regression models. Since computational complexity of such approach grows exponentially with respect to combination length, we first narrow down features list in order to make search practically feasible. Briefly, the following pipeline is implemented:
1. **Feature pre-selection:** select fixed number of features for the next steps.
2. **Feature selection:** select *n* features for exhaustive search.
3. **Exhaustive search:** iterate through all possible *k*-element feature subsets and fit classification/regression models.

Values of *n* and *k* actually define running time of the pipeline (there are *C<sub>n</sub><sup>k</sup>* feature subsets). For example, iterating through all 8-gene signatures composed of *n = 20* genes is possible (see example breast cancer data below), while search for over *n = 1000* genes will never end even on the most powerful supercomputer.

Input data can consist from different batches (datasets), and each dataset should be labeled by one of the following types:
1. **Training set:** samples from training datasets will be used for tuning classification/regression models. At least one such dataset is required; if multiple given, the union will be used.
2. **Filtration set:** all tuned models will be first evaluated on training and filtration sets. If specified thresholds for accuracy are reached, model will be evaluated on validation (test) sets. The use of filtration sets is optional.
3. **Validation (test) set:** performance of models which passed filtration thresholds are then evaluated on validation sets. At least one such dataset is required; if multiple given, model will be evaluated on all test sets independently.

**TODO:** add flowchart.

# Installation

### Prerequisites:
Make sure you have installed all of the following prerequisites on your development machine:
  - python3.6+  
  - pip3


### ExhauFS installation:  
`pip3 install exhaufs`  

# Running ExhaustiveFS

## Step 1: data preparation

Before running the tool, you should prepare three csv tables containing actual data, its annotation and *n* \ *k* grid. Both for classification and survival analysis data table should contain numerical values associated with samples (rows) and features (columns):

<details>
  <summary>Example</summary>
  
  |            | Feature 1 | Feature 2 |
  | ---------- | --------- | --------- |
  | Sample 1   | 17.17     | 365.1     |
  | Sample 2   | 56.99     | 123.9     |
  | ...        |           |           |
  | Sample 98  | 22.22     | 123.4     |
  | Sample 99  | 23.23     | 567.8     |
  | ...        |           |           |
  | Sample 511 | 10.82     | 665.8     |
  | Sample 512 | 11.11     | 200.2     |
</details>


Sample annotation table formats are different for classification and survival analysis. For classification it should contain binary indicator of sample class (e.g., 1 for recurrent tumor and 0 for non-recurrent), dataset (batch) label and dataset type (Training/Filtration/Validation).  
It is important that `Class = 1` represents "Positives" and `Class = 0` are "negatives", otherwise accuracy scores may be calculated incorrectly.   
Note that annotation should be present for each sample listed in the data table in the same order:

<details>
  <summary>Example</summary>
  
  |            | Class | Dataset  | Dataset type |
  | ---------- | ----- | -------- | ------------ |
  | Sample 1   | 1     | GSE3494  | Training     |
  | Sample 2   | 0     | GSE3494  | Training     |
  | ...        |       |          |              |
  | Sample 98  | 0     | GSE12093 | Filtration   |
  | Sample 99  | 0     | GSE12093 | Filtration   |
  | ...        |       |          |              |
  | Sample 511 | 1     | GSE1456  | Validation   |
  | Sample 512 | 1     | GSE1456  | Validation   |
</details>


For survival analysis, annotation table should contain binary event indicator and time to event:
<details>
  <summary>Example</summary>
  
  |            | Event | Time to event | Dataset  | Dataset type |
  | ---------- | ----- | ------------- | -------- | ------------ |
  | Sample 1   | 1     | 100.1         | GSE3494  | Training     |
  | Sample 2   | 0     | 500.2         | GSE3494  | Training     |
  | ...        |       |               |          |              |
  | Sample 98  | 0     | 623.9         | GSE12093 | Filtration   |
  | Sample 99  | 0     | 717.1         | GSE12093 | Filtration   |
  | ...        |       |               |          |              |
  | Sample 511 | 1     | 40.5          | GSE1456  | Validation   |
  | Sample 512 | 1     | 66.7          | GSE1456  | Validation   |
</details>


Table with *n* and *k* grid for exhaustive feature selection:  
*n* is a number of selected features, *k* is a length of each features subset.  

If you are not sure what values for *n* *k* to use, see [Step 3: defining a *n*, *k* grid](#step-3-defining-a-n-k-grid)  

<details>
  <summary>Example</summary> 
   
  | n   | k   |  
  | --- | --- |  
  | 100 | 1   |  
  | 100 | 2   |  
  | ... | ... |  
  | 20  | 5   |  
  | 20  | 10  |  
  | 20  | 15  |  
</details>


## Step 2: creating configuration file

Configuration file is a json file containing all customizable parameters for the model (classification and survival analysis)  

<details>
  <summary>Available parameters</summary> 

  🔴!NOTE! - All paths to files / directories should be relative to the configuration file directory  
  * `data_path`
      Path to csv table of the data.

  * `annotation_path`
      Path to csv table of the data annotation.

  * `n_k_path`
      Path to a *n*/*k* grid file.

  * `output_dir`
      Path to directory for output files. If not exist, it will be created.

  * `feature_pre_selector`  
      Name of feature pre-selection function from [feature pre-selectors section](#functions-and-classes).

  * `feature_pre_selector_kwargs`  
      Object/Dictionary of keyword arguments for feature pre-selector function.

  * `feature_selector`  
      Name of feature selection function from [feature selectors section](#functions-and-classes).

  * `feature_selector_kwargs`  
      Object/Dictionary of keyword arguments for feature selector function.

  * `preprocessor`
      Name of class for data preprocessing from [sklearn.preprocessing](#https://scikit-learn.org/stable/modules/preprocessing.html).

  * `preprocessor_kwargs`
      Object/Dictionary of keyword arguments for preprocessor class initialization.  
      If you are using `sklearn` model, use `kwargs` parameters from the documentation of the model.

  * `model`  
      Name of class for classification / survival analysis from [Classifiers / Regressors section](#functions-and-classes).

  * `model_kwargs`
      Object/Dictionary of keyword arguments for model initialization.  
      If you are using `sklearn` model, use `kwargs` parameters from the documentation of the model.

  * `model_CV_ranges`
      Object/Dictionary defining model parameters which should be cross-validated. Keys are parameter names, values are lists for grid search.

  * `model_CV_folds`
      Number of folds for K-Folds cross-validation.

  * `limit_feature_subsets`
      If *true*, limit the number of processed feature subsets.

  * `n_feature_subsets`
      Number of processed feature subsets.

  * `shuffle_feature_subsets`
      If *true*, processed feature subsets are selected randomly instead of alphabetical order.

  * `max_n`
      Maximal number of selected features.

  * `max_estimated_time`
      Maximal estimated pipeline running time.

  * `scoring_functions`
      List with names for scoring functions (from [Accuracy scores section](#functions-and-classes)) which will be calculated for each model.

  * `main_scoring_function`
      Key from scoring_functions dict defining the "main" scoring function which will be optimized during cross-validation and will be used for model filtering.

  * `main_scoring_threshold`
      A number defining threshold for model filtering: models with score below this threshold on training/filtration sets will not be further evaluated.

    * `n_processes`
      Number of processes / threads to run on.
  
  * `random_state`
      Random seed (set to an arbitrary integer for reproducibility).

  * `verbose`
      If *true*, print running time for each pair of *n*, *k*.
</details>


## Step 3: defining a *n*, *k* grid

To estimate running time of the exhaustive pipeline and define adequate *n* / *k* values you can run:  
```bash
exaufs estimate regressors|classifiers -c <config_file> --max_k <max_k> --max_estimated_time <max_estimated_time>
```
where
* `config_file` is the path to json configuration file.
* `max_k` is the maximal length of each features subset.
* `max_estimated_time` is the maximal estimated time (in hours) of single running of the exhaustive pipeline.
* `n_feature_subsets` is the number of feature subsets processed by the exhaustive pipeline (*100* is usually enough).
* `search_max_n` is *1* if you need to find the maximal number of selected features for which estimated run time of the exhaustive pipeline is less than `max_estimated_time`, and *0* otherwise.
* `is_regressor` is *1* if you the estimation is for the regression.

Above script calculates maximum possible values *n* / *k* for each *k*=`1...max_n` such that pipeline running time for each pair (*n*, *k*) is less then `max_estimated_time`

## Step 4: running the exhaustive pipeline

When input data, configuration file and *n*, *k* grid are ready,
the exhaustive pipeline could be executed -  
* __Classifiers__:
```bash
exhaufs build classifiers -c <config_file>
```
* __Regressions__:
```bash
exhaufs build regressors -c <config_file>
```

This will generate multiple files in the specified output folder:
* models.csv: this file contains all models (classifiers or regressors) which passed the filtration together with their quality metrics.
* summary_n_k.csv: for each pair of *n*, *k* three numbers are given: number of models which passed the filtration,
number of models which showed reliable performance (i.e., passed quality thresholds) on the validation set and
their ratio (in %). Low percentage of validation-reliable models together with high number of 
filtration-reliable models is usually associated with overfitting.
* summary_features.csv: for each feature percentage of models carrying this feature 
is listed (models which passed the filtration are considered).

## Step 5: generating report for a single model
To get detailed report on the specific model (== specific set of features): 
* Create configuration file (use ./examples/make_<u>(classifier | regressor)</u>_summary/config.json as
   template) and set following key parameters:
    * `data_path` - path to dataset used for search of classifiers
  (relative to directory with configuration file);
    * "annotation_path" - path to annotation file (relative to directory 
      with configuration file);
    * `output_dir` - path to output directory for detailed report 
      (relative to directory with configuration file);
    * `features_subset` - set of features belonging to the classifier of interest;
* * For classifier run `exhaufs summary classifiers -c <config_file>`   
  * For regressor run `exhaufs summary regressors -c <config_file>`    
* Check the detailed report in `output_dir`

# Functions ans classes
<details>
  <summary>Feature pre-selectors</summary>
  
  - <details>
    <summary>from_file</summary> 
    
    Pre-select features from a given file
    
    __name__: from_file     
    __kwargs__:   
    ```json
    {
      "sep": " "
    }
    ```
    </details>
</details>
</a> 
 
<details>
  <summary>Feature selectors</summary>
  
  - <details>
    <summary>t_test</summary> 
    
    Select n features with the lowest p-values according to t-test
    
    __name__: t_test    
    __kwargs__:   
    ```json
    {
      "datasets": ["Training", "Filtration"]
    }
    ```
    </details>
  - <details>
    <summary>spearman_correlation</summary> 
    
    Select n features with the highest correlation with target label
    
    __name__: spearman_correlation   
    __kwargs__:   
    ```json
    {
      "datasets": ["Training", "Filtration"]
    }
    ```
    </details>
  - <details>
    <summary>from_file</summary> 
     
    Select first n features from a given file
    
    __name__: spearman_correlation   
    __kwargs__:   
    ```json
    {
      "sep": " "
    }
    ```
    </details>
  - <details>
    <summary>median</summary> 
    
    Select n features with the highest median value  
    __name__: median  
    __kwargs__:   
    ```json
    {}
    ```
    </details>
    
  ##### Regression specific selectors:
  - <details>
    <summary>cox_concordance</summary> 
       
    Select n features with the highest concordance index on one-factor Cox regression.
    
    __name__: cox_concordance  
    __kwargs__:  
    ```json
    {
      "datasets": ["Training", "Filtration"]
    }
    ```
    </details>
  - <details>
    <summary>cox_dynamic_auc</summary> 
    
    Select n features with the highest time-dependent auc on one-factor Cox regression.
  
    __name__: cox_dynamic_auc   
    __kwargs__: 
    ```json
    {
      "year": 3, // time at which to calculate auc
      "datasets": ["Training", "Filtration"]
    }
    ```
    </details>
  - <details>
    <summary>cox_hazard_ratio</summary> 
    
    Select n features with the highest hazard ratio on one-factor Cox regression.
    
    __name__: cox_hazard_ratio   
    __kwargs__:   
    ```json
    {
      "datasets": ["Training", "Filtration"]
    }
    ```
    </details>
    <details>
    <summary>cox_likelihood</summary> 
    
    Select n features with the highest log-likelihood on one-factor Cox regression.
    
    __name__: cox_likelihood  
    __kwargs__:  
    ```json
    {
      "datasets": ["Training", "Filtration"]
    }
    ```
    </details>
</details>

<details>
  <summary>Classifiers</summary>
  
  - [SVC](#https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html)
  - [KNeighborsClassifier](#https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html)
  - [RandomForestClassifier](#https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
  - [XGBClassifier](#https://xgboost.readthedocs.io/en/latest/python/python_api.html)
  
  As a `model_kwargs` value - use parameters from the documentation of chosen model.
  
  #### Accuracy scores
  - TPR
  - FPR
  - TNR
  - min_TPR_TNR
</details>
<details>
  <summary>Regressors</summary>
  
  - CoxRegression
  
  #### Accuracy scores
  - concordance_index
  - dynamic_auc
  - hazard_ratio
  - logrank
</details>

# Tutorials
<details>
  <summary>Toy example</summary>
  
  As a toy example of how the ExhauFS works we used a small [cervical cancer dataset](https://archive.ics.uci.edu/ml/datasets/Cervical+Cancer+Behavior+Risk) with 19 features and 72 samples.  
  
  Transformed data and config used for pipeline can be found in [OneDrive](https://eduhseru-my.sharepoint.com/:f:/g/personal/snersisyan_hse_ru/EpJztBwnLENPuLU8r0fA0awB1mBsck15t2zs7-aG4FXKNw).  

  The purpose of the toy example is to show that exhaustive search over all triples of features  
  can yield better results than by using a standard approach of training classifier on all the features  
  and then select the most important ones.  
  
  By executing `exhaufs build classifiers -c <config path>` command we are getting results files in the specified output directory:  
  - `models.csv`
  
  In this file, by ranking all models by their performance on the "Training" set, we can see that almost all models have accuracy score of 1.0.  
  And among these models there are multiple cases with particularly high accuracy on "Validation" set:    
  
  | features  | Validation;min_TPR_TNR | Training;min_TPR_TNR   | n   | k   |
  | ---       |  ---                   | ---                    | --- | --- |
  | ... | ... | ... | ... | ... |
  | behavior_eating;norm_fulfillment;empowerment_knowledge      | 0.9 | 1.0 | 19 | 3 |
  | ... | ... | ... | ... | ... |
  
  
  To get a full summary of a particular model (in our case - constructed on above three features),  
  we need to add `features_subset` with those features to the config file and run `exhaufs summary classifiers -c <config path>`  
  which will, again, produce multiple files in the specified output directory, the most important of which are:
  - `report.txt` (contains detailed accuracy scores for all datasets)
  - `ROC_Training.pdf` (contains roc-auc curve for training set)
  - `ROC_Validation.pdf` (contains roc-auc curve for validation set)
  
</details>

<details>
  <summary>Breast cancer classification</summary>
  
  TODO: add correct links  
  As a real-life example of the classification part of the tool we used [breast cancer dataset](https://archive.ics.uci.edu/ml/datasets/Cervical+Cancer+Behavior+Risk).  
  
  Transformed data and config used for pipeline can be found in [OneDrive](https://eduhseru-my.sharepoint.com/:f:/g/personal/snersisyan_hse_ru/EpJztBwnLENPuLU8r0fA0awB1mBsck15t2zs7-aG4FXKNw).  

  The main objective was to analyse contribution of different pre-processing and feature [pre]selection techniques.  
  By using `z-score` as a normalization, `t-test` as a feature selector and `KBinsDiscretizer`(binarization) as a pre-processor we achieved good results in terms of number of models passing threshold on validation set relative to the number of models passing threshold on training and filtration sets which indicates that there is no randomness and all of the models are actually "good".   
  
  First of all, we need to calculate appropriate grid for `n/k` values, so the pipeline knows what features and their subsets to use.  
  To do so, we need to define the maximum time we want for the pipeline to work for a single pair of (n, k).  
  In our case, we chose 12 hours. And since we don't want to analyse classifiers with more than 20 features, we set `max_k` as 20.  
  By executing `exhaufs estimate classifiers -c <config path> --max_estimated_time 12 --max_k 20` we are getting `n/k` grid table in the output directory, which looks like this:  
  
  | n   | k   | Estimated time     |
  | --- | --- | ---                |
  | ... | ... | ...                |
  | 59  | 4   | 2.9192129150403865 |
  | 37  | 5   | 2.8854977554500105 |
  | 28  | 6   | 2.5242263025045393 |
  | 24  | 7   | 2.3660491471767426 |
  
  We can use path to the above file as a `n_k_path` value in the config and then by executing `exhaufs build classifiers -c <config path>` command we get pipeline results files in the specified output directory:  
  - `summary_n_k.csv`
  
  Shows that above certain values of `k`, almost 100% of the classifiers passed the threshold of *0.65* for minimum of TPR and TNR.
  TODO: add real table
  | n   | k   |  num_training_reliable | num_validation_reliable | percentage_reliable |
  | --- | --- |  ---                   | ---                     | ---                 |
  | 19 | 2    |  137                   | 41                      | 29.927007299270077  |
  | 19 | 3    |  925                   | 258                     | 29.927007299270077  |
  | 19 | 4    |  3859                  | 1252                    | 32.44363824825084   |
  
  - `models.csv`
  
  In this file, by ranking all models by their performance on the "Training" set we can see that almost all models have accuracy score of 1.0  
  And among these models there are multiple cases with particularly high accuracy on "Validation" set  
  
  | features  | Validation;min_TPR_TNR | Training;min_TPR_TNR   | n   | k   |
  | ---       |  ---                   | ---                    | --- | --- |
  | ... | ... | ... | ... | ... |
  | behavior_eating;norm_fulfillment;empowerment_knowledge      | 0.9 | 1.0 | 19 | 3 |
  | ... | ... | ... | ... | ... |
  
  Then, to get a full summary of a particular model (in our case - constructed on above three features),  
  we need to add `features_subset` with those features to the config file and run `exhaufs summary classifiers -c <config path>`  
  which will, again, produce multiple files in the specified output directory, the most important of which are:
  - `report.txt` (contains detailed accuracy scores for all datasets)
  - `ROC_Training.pdf` (contains roc-auc curve for training set)
  - `ROC_Validation.pdf` (contains roc-auc curve for validation set)
  
</details>

<details>
  <summary>Colorectal cancer survival regression</summary>
  
 TODO: add correct links
  As a real-life example of the regression part of the tool we used [colorectal cancer dataset](https://archive.ics.uci.edu/ml/datasets/Cervical+Cancer+Behavior+Risk).  
  
  Transformed data and config used for pipeline can be found in [OneDrive](https://eduhseru-my.sharepoint.com/:f:/g/personal/snersisyan_hse_ru/EpJztBwnLENPuLU8r0fA0awB1mBsck15t2zs7-aG4FXKNw).  

  Same with classification, the main objective was to analyse contribution of different feature [pre]selection techniques and accuracy scores using Cox Regression as a main model.  
  We achieved best results using `concordance_index` as a feature selector and as a main scoring function.  
  
  Again, same with classification, firstly we need to make `n/k` grid table for the pipeline.  
  After choosing maximum time and k values (in this case - maximum time is 3 hours and maximum k is 20) we can run `exhaufs estimate regressors -c <config path> --max_estimated_time 3 --max_k 20` and use the resulting table as a `n/k` grid for the pipeline.  
  
  By executing `exhaufs build regressors -c <config path>` command we are getting results files in the specified output directory:  
  - `summary_n_k.csv`
  
  Shows that above certain values of `k`, close to 95% of the regressors passed the threshold of *0.6* for concordance index.
  
  | n   | k   | ...  | percentage_reliable |
  | --- | --- | ---  | ---                 |
  | ... | ... | ...  | ...                 |
  | 21  | 9   | ...  | 79.94548176605181   |
  | 20  | 10  | ...  | 88.44062562932133   |
  | 20  | 11  | ...  | 93.06034157506852   |
  | 20  | 12  | ...  | 96.4579532546212    |
  | 20  | 13  | ...  | 98.52712732293884   |
  | 21  | 14  | ...  | 98.68958543983824   |
  | 22  | 15  | ...  | 98.8608905764584    |
  | 22  | 16  | ...  | 99.55598455598457   |
  | ... | ... | ...  | ...                 |

  - `models.csv`
  
  If we take only models with k=7 and sort them by average between concordance index on training and filtration sets  
  we find one model with quite high scores: concordance index = 0.71, hazard ratio = 3, 3-year AUC = 0.67, logrank = 3.1.  
  TODO: add features  
  
  Then, to get a full summary of this model, we need to add `features_subset` with those features to the config file and run `exhaufs summary regressors -c <config path>` which will, again, produce multiple files in the specified output directory, the most important of which are:
  - `report.txt` (contains detailed accuracy scores for all datasets)
  - `KM_Training.pdf` (contains Kaplan-Meier curve for training set)
  - `KM_Filtration.pdf` (contains Kaplan-Meier curve for filtration set)
  - `KM_Validation.pdf` (contains Kaplan-Meier curve for validation set)
  
</details>

# etc
Breast and colorectal cancer microarray datasets: [OneDrive](https://eduhseru-my.sharepoint.com/:f:/g/personal/snersisyan_hse_ru/EpJztBwnLENPuLU8r0fA0awB1mBsck15t2zs7-aG4FXKNw).
