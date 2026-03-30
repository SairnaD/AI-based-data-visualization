import pandas as pd
import numpy as np


def numeric_score(s):
    s = s.dropna()
    if len(s) < 5:
        return 0
    variance = s.var()
    iqr = s.quantile(0.75) - s.quantile(0.25)
    return float(variance + iqr)


def categorical_score(s):
    s = s.dropna()
    if len(s) < 5:
        return 0
    counts = s.value_counts(normalize=True)
    entropy = -(counts * np.log2(counts + 1e-9)).sum()
    return float(entropy)


def correlation_score(df, col1, col2):
    try:
        if df[col1].dtype in ["int64", "float64"] and df[col2].dtype in ["int64", "float64"]:
            corr = df[col1].corr(df[col2])
            if corr is not None and not np.isnan(corr):
                return abs(corr)
    except Exception:
        pass
    return 0.0


def is_non_informative(s):
    s = s.dropna()
    n = len(s)

    if n < 10:
        return True

    name = s.name.lower()

    if any(k in name for k in ["id", "index", "uuid", "nr", "no", "number"]):
        return True

    if pd.api.types.is_numeric_dtype(s):
        uniq_ratio = s.nunique() / n

        if uniq_ratio > 0.9:
            return True

        if s.var() == 0:
            return True

        try:
            corr = abs(np.corrcoef(s.values, np.arange(n))[0, 1])
            if corr > 0.98:
                return True
        except Exception:
            pass
    else:
        uniq_ratio = s.nunique() / n
        if uniq_ratio > 0.8:
            return True

    return False


def clean_df(df):
    return df[[c for c in df.columns if not is_non_informative(df[c])]]
