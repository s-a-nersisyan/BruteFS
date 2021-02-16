import sys
import os
import json

import pandas as pd

from core import classification  
from core import feature_pre_selectors
from core import feature_selectors
from core import preprocessors
from core import classifiers
from core import accuracy_scores

def classifiers_num (df, scoring, threshold, datasets):
    """Get number of classifiers that have scoring greater than threshold in given datasets
    
    Parameters
    ----------
    df : pandas.DataFrame
        A pandas DataFrame whose rows represent classifiers
        and columns represent their quality scores.
    scoring : str
        Key from scoring_functions dict defining the scoring function.
    threshold : float
        A number defining threshold for classifier filtering.
    datasets : list
        List of dataset identifiers.
    
    Returns
    -------
    int
        Number of classifiers
    """
    queries = [ "(out['{}'] > {})".format(f"{ds};{scoring}", threshold) for ds in datasets ]
    return df[eval(" & ".join(queries))].shape[0]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify configuration file", file=sys.stderr)
        sys.exit(1)
    
    config_path = sys.argv[1]
    try:
        config_file = open(config_path, "r")
    except:
        print("Cannot open configuration file", file=sys.stderr)
        sys.exit(1)

    try:
        config = json.load(config_file)
    except:
        print("Please specify valid json configuration file", file=sys.stderr)
        sys.exit(1)

    # Paths are absolute or relative to config file
    # TODO: add some checks (files can be opened, indices are the same, columns names are here etc)
    config_dirname = os.path.dirname(config_path)
    df = pd.read_csv(os.path.join(config_dirname, config["data_path"]), index_col=0)
    ann = pd.read_csv(os.path.join(config_dirname, config["annotation_path"]), index_col=0)
    n_k = pd.read_csv(os.path.join(config_dirname, config["n_k_path"]))
    main_scoring_function = config["main_scoring_function"]
    main_scoring_threshold = config["main_scoring_threshold"]

    model = classification.ExhaustiveClassification(
        df, ann, n_k,
        getattr(feature_pre_selectors, config["feature_pre_selector"] or "", None),
        config["feature_pre_selector_kwargs"],
        getattr(feature_selectors, config["feature_selector"]),
        config["feature_selector_kwargs"],
        getattr(preprocessors, config["preprocessor"] or "", None),
        config["preprocessor_kwargs"],
        getattr(classifiers, config["classifier"]), 
        config["classifier_kwargs"],
        config["classifier_CV_ranges"], config["classifier_CV_folds"],
        {s: getattr(accuracy_scores, s) for s in config["scoring_functions"]},
        config["main_scoring_function"], config["main_scoring_threshold"],
        n_processes=config["n_processes"], 
        random_state=config["random_state"],
        verbose=config["verbose"]
    )
    out = model.exhaustive_run()
    print(out)

    table = pd.DataFrame(columns=['n','k','train_filtr','train_filtr_valid','percent'])
    for n, k in zip(n_k["n"], n_k["k"]):

        tf_datasets = ann.loc[ann["Dataset type"].isin(["Training", "Filtration"]), "Dataset"].unique()
        tf_num = classifiers_num(out, main_scoring_function, main_scoring_threshold, tf_datasets)

        tfv_datasets = ann.loc[ann["Dataset type"].isin(["Training", "Filtration", "Validation"]), "Dataset"].unique()
        tfv_num = classifiers_num(out, main_scoring_function, main_scoring_threshold, tfv_datasets)

        table = table.append( { 'n'                 : n, 
                                'k'                 : k, 
                                'train_filtr'       : tf_num,
                                'train_filtr_valid' : tfv_num,
                                'percent'           : 100 * tfv_num / tf_num }, ignore_index=True)
    print(table)

    table = pd.DataFrame(columns=['gene','percent'])
    clsfs_num = out.shape[0]
    genes_to_clsfs_num = {}
    for clsf in out.index:
        for g in clsf.split(';'):
            if g in genes_to_clsfs_num:
                genes_to_clsfs_num[g] += 1
            else:
                genes_to_clsfs_num[g] = 1
    for g in genes_to_clsfs_num:
        table = table.append( { 'gene'    : g, 
                                'percent' : 100 * genes_to_clsfs_num[g] / clsfs_num }, ignore_index=True)
    table.sort_values(by=['percent'])
    print(table)