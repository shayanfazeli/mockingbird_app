from typing import Dict, Tuple, List
import os
import sys
import pandas
import numpy
import pickle, gzip
import torch
import torch.nn
from tqdm import tqdm
import itertools
import functools
import dateutil.parser as date_parser
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, Any
import hashlib
import json
from tqdm import tqdm
import pyLDAvis.gensim_models

from app.libraries.io.accounts_dataframe import read_accounts_df
from app.libraries.io.tweet_filepaths import get_tweet_filepaths
from app.libraries.randomization.hashing import dict_hash
from app import cache_folderpath


def get_timespan_partition_for_trajectory(
        trajectory: Dict[str, Any],
        convert_to_str: bool = True
) -> List[Tuple[str, str]]:
    """
    Parameters
    ----------
    trajectory: `Dict[str, Any]`, required
        The trajectory, as an example:
        ```python
        trajectory=dict(
            state=None,
            institution_type=['television broadcast network'],
            dates=(start_date, end_date, dict(years=5, months=0, days=0)))
        ```

    convert_to_str: `bool`, optional (default=True)
        Whether to convert the dates to strings.

    Returns
    -------
    `List[Tuple[str, str]]`: The timespan partition, as an ordered list of start and end dates.
    """
    # - the dates
    start_date, end_date, step = trajectory['dates']
    step = relativedelta(**step)
    start_date = date_parser.parse(start_date).date()
    end_date = date_parser.parse(end_date).date()

    if convert_to_str:
        partition_timespans = [(str(start_date), str(min(end_date, start_date + step)))]
    else:
        partition_timespans = [(start_date, min(end_date, start_date + step))]
    start_date += step

    while start_date < end_date:
        if convert_to_str:
            partition_timespans += [(str(start_date), str(min(end_date, start_date + step)))]
        else:
            partition_timespans += [(start_date, min(end_date, start_date + step))]
        start_date += step

    return partition_timespans


def filter_per_trajectory(
    df: pandas.DataFrame,
    trajectory: Dict[str, Any],
) -> List[pandas.DataFrame]:
    """
    Given a trajectory and a full dataframe, this method
    will split the dataframe into an ordered list of dataframes associated with the given trajectory.

    Parameters
    ----------
    df: `pandas.DataFrame`, required
        The input dataframe.

    trajectory: `Dict[str, Any]`, required
        The trajectory, as an example:
        ```python
        trajectory=dict(
            state=None,
            institution_type=['television broadcast network'],
            dates=(start_date, end_date, dict(years=5, months=0, days=0)))
        ```
    """
    df = df.copy()
    timespans = get_timespan_partition_for_trajectory(trajectory=trajectory, convert_to_str=True)
    df.sort_values(by='date', ascending=True, inplace=True)
    output_dfs = [df[(df.date >= ts[0]) & (df.date < ts[1])].copy() for ts in timespans]
    return output_dfs


def get_filtered_twitter_handles(trajectory: Dict[str, Any]) -> List[str]:
    """
    Parameters
    ----------
    trajectory: `Dict[str, Any]`, required
        The trajectory, as an example:
        ```python
        trajectory=dict(
            state=None,
            institution_type=['television broadcast network'],
            dates=(start_date, end_date, dict(years=5, months=0, days=0)))
        ```

    Returns
    -------
    `List[str]`: The list of tweet handles that have data for the trajectory.
    """
    tmp_df = read_accounts_df()
    if trajectory['state'] is not None:
        if not isinstance(trajectory['state'], list):
            trajectory['state'] = [trajectory['state']]
        tmp_df = tmp_df[tmp_df.state.isin(trajectory['state'])]

    if trajectory['institution_type'] is not None:
        if not isinstance(trajectory['institution_type'], list):
            trajectory['institution_type'] = [trajectory['institution_type']]
        tmp_df = tmp_df[tmp_df.institution_type.isin(trajectory['institution_type'])]
    return tmp_df.twitter_handle.unique().tolist()


def prepare_trajectory_dataset(
    trajectory: Dict[str, Any],
    tweet_filepaths: List[str],
    overwrite: bool = False
) -> Tuple[List[pandas.DataFrame], Dict[str, Any]]:
    """
    Parameters
    ----------
    trajectory: `Dict[str, Any]`, required
        The trajectory, as an example:
        ```python
        trajectory=dict(
            state=None,
            institution_type=['television broadcast network'],
            dates=(start_date, end_date, dict(years=5, months=0, days=0)))
        ```

    tweet_filepaths: `List[str]`, required
        The list of tweet filepaths.

    overwrite: `bool`, optional (default=False)
        Whether to overwrite the cached data.

    Returns
    -------
    `Tuple[List[pandas.DataFrame], Dict[str, Any]]`: The ordered list of associated segment dataframes as well as the
    metadata, including the details of the trajectory and the full filepaths to the considered tweet corpora.
    """

    # - preparing the metadata
    meta = dict(
        tweet_filepaths=tweet_filepaths,
        trajectory=trajectory
    )

    # - reading from cache if needed
    final_filename = os.path.join(cache_folderpath, 'trajectory', dict_hash(meta) + '.pkl.gz')
    if os.path.exists(final_filename) and not overwrite:
        with gzip.open(final_filename, 'rb') as handle:
            data_dict = pickle.load(handle)
            return data_dict['data'], data_dict['meta']

    # - filtering the allowed accounts
    allowed_handles = [e.lower() for e in get_filtered_twitter_handles(trajectory=trajectory)]

    # - reading all the tweet files associated with the allowed handles and filtering them based on trajectory
    outputs = []
    for tweet_filepath in tweet_filepaths:
        if os.path.basename(tweet_filepath)[:-4].lower() not in allowed_handles:
            continue
        tmp_df = pandas.read_csv(tweet_filepath, on_bad_lines='skip', delimiter='\t')
        outputs += [filter_per_trajectory(tmp_df, trajectory)]

    # - concatenating the results across the time-segment
    results = []
    for i in range(len(outputs[0])):
        results += [pandas.concat([e for e in zip(*outputs)][i], axis=0)]

    # - caching the result
    with gzip.open(final_filename, 'wb') as handle:
        pickle.dump(dict(meta=meta, data=results), handle)

    return results, meta
