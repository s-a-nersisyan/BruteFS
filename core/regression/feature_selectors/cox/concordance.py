from core.regression.feature_selectors.utils import save_sorted_features
from core.regression.models import CoxRegression

from core.utils import get_datasets


def cox_concordance(df, ann, n, datasets=None, is_save=True):
    """Select n features with the highest concordance index on one-factor Cox regression.

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas DataFrame whose rows represent samples
        and columns represent features.
    ann : pandas.DataFrame
        DataFrame with annotation of samples. Three columns are mandatory:
        Class (binary labels), Dataset (dataset identifiers) and
        Dataset type (Training, Filtration, Validation).
    n : int
        Number of features to select.
    datasets : array-like
        List of dataset identifiers which should be used to calculate
        local statistic. By default (None), union of all non-validation
        datasets will be used.
    Returns
    -------
    list
        List of n features associated with the highest c-index.
    """
    datasets = get_datasets(ann, datasets)

    samples = ann.loc[ann['Dataset'].isin(datasets)].index
    df_subset = df.loc[samples]
    ann_subset = ann.loc[samples, ['Event', 'Time to event']]
    columns = df_subset.columns

    scores = []
    for j, column in enumerate(columns):
        df_j = df_subset[[column]]
        model = CoxRegression()
        model.fit(df_j, ann_subset)
        score = model.concordance_index_

        scores.append(score)

    scores, features = zip(*sorted(zip(scores, columns), key=lambda x: x[0], reverse=True))

    if is_save:
        save_sorted_features(scores, features)

    return features[:n]
