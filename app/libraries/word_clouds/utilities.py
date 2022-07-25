from typing import List, Any
import os
import pickle
import gzip
import numpy
import nltk
from tqdm import tqdm
import pyLDAvis
import torch
import dateutil.parser as date_parser
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pandas
import plotly_express as px
from fame.text_processing.text_processor import TextProcessor
from fame.text_processing.token_processor import TokenProcessor
from fame.topic_modeling.cortex.pipeline.bert_lda import TransformerLDATopicModelingPipeline
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go
from app.libraries.io.tweet_filepaths import get_tweet_filepaths
from app.libraries.randomization.hashing import dict_hash
from app.libraries.trajectory.utilities import prepare_trajectory_dataset, get_timespan_partition_for_trajectory

from app import cache_folderpath
from app.libraries.utilities.logging import get_logger
logger = get_logger(__name__)


# - from the github repository: https://raw.githubusercontent.com/PrashantSaikia/Wordcloud-in-Plotly/master/plotly_wordcloud.py
def plotly_wordcloud(text, max_words):
    wc = WordCloud(stopwords=set(STOPWORDS),
                   max_words=max_words,
                   max_font_size=20)
    wc.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x = []
    y = []
    for i in position_list:
        x.append(i[0])
        y.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 100)
    new_freq_list

    trace = go.Scatter(x=x,
                       y=y,
                       textfont=dict(size=new_freq_list,
                                     color=color_list),
                       hoverinfo='text',
                       hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                       mode='text',
                       text=word_list
                       )

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})
    fig = go.Figure(data=[trace], layout=layout)
    fig.update_layout(template='plotly_white')

    return fig


def is_request_processed(query_institutions: List[str],
        query_step_in_days: int,
        query_min_date: str,
        query_max_date: str,
        max_word_count: int) -> bool:
    """
    Parameters
    ----------
    query_institutions: `List[str]`, required
        The institutions to query

    query_step_in_days: `int`, required
        The step in days to query

    query_min_date: `str`, required
        The minimum date to query

    query_max_date: `str`, required
        The maximum date to query

    max_word_count: `int`, required
        The maximum number of words to include in the word cloud

    Returns
    -------
    whether the request is already processed
    """
    logger.info("1) getting filepaths...")
    tweet_filepaths = get_tweet_filepaths()
    trajectory = dict(
        state=None,
        institution_type=query_institutions,
        dates=(query_min_date, query_max_date, dict(years=0, months=0, days=query_step_in_days)))

    timespans = [f'{e[0]} -> {e[1]}' for e in get_timespan_partition_for_trajectory(trajectory)]

    trajectory_hash = dict_hash(dict(
        tweet_filepaths=tweet_filepaths,
        trajectory=trajectory,
    ))

    # - preparing the topic models based on support
    pipeline_args = dict(
        number_of_topics_for_lda=2,
        autoencoder=None,
        representation_clustering=None,
        use_transformer=False,
        use_lda=True,
        use_tfidf=False,
        device=torch.device('cpu'),
        transformer_modelname='paraphrase-mpnet-base-v2',
        text_processor=TextProcessor(
            methods=[
                'remove_url',
                'convert_to_lowercase',
                'uppercase_based_missing_delimiter_fix',
                # 'gtlt_normalize',
                # 'substitute_more_than_two_letter_repetition_with_one',
                'non_character_repetition_elimination',
                # 'use_star_as_delimiter',
                # 'remove_parantheses_and_their_contents',
                'remove_questionexlamation_in_brackets',
                'eliminate_phrase_repetition',
                'strip'
            ]
        ),
        token_processor_light=TokenProcessor(
            methods=[
                'keep_alphabetics_only',
                # 'keep_nouns_only',
                # 'spell_check_and_typo_fix',
                # 'stem_words',
                # 'remove_stopwords'
            ]
        ),
        token_processor_heavy=TokenProcessor(
            methods=[
                'keep_alphabetics_only',
                # 'keep_nouns_only',
                # 'spell_check_and_typo_fix',
                # 'stem_words',
                # 'remove_stopwords'
            ]
        ))

    logger.info("2) preparing query trajectory dataset...")
    # - preparing the metadata
    meta = dict(
        tweet_filepaths=tweet_filepaths,
        trajectory=trajectory
    )

    # - reading from cache if needed
    final_filename = os.path.join(cache_folderpath, 'trajectory', dict_hash(meta) + '.pkl.gz')
    if not os.path.exists(final_filename):
        return False

    logger.info("3) finding word clouds...")
    word_clouds_filepath = os.path.join(cache_folderpath, 'word_clouds', f"{trajectory_hash}-word_clouds.pkl.gz")
    if not os.path.exists(word_clouds_filepath):
        return False

    return True


def get_word_cloud_data(
        query_institutions: List[str],
        query_step_in_days: int,
        query_min_date: str,
        query_max_date: str,
        max_word_count: int
) -> Any:
    """
    Parameters
    ----------
    query_institutions: `List[str]`, required
        The institutions to query

    query_step_in_days: `int`, required
        The step in days to query

    query_min_date: `str`, required
        The minimum date to query

    query_max_date: `str`, required
        The maximum date to query

    max_word_count: `int`, required
        The maximum number of words to include in the word cloud

    Returns
    -------
    The data for the plot
    """
    logger.info("1) getting filepaths...")
    tweet_filepaths = get_tweet_filepaths()
    trajectory = dict(
            state=None,
            institution_type=query_institutions,
            dates=(query_min_date, query_max_date, dict(years=0, months=0, days=query_step_in_days)))

    timespans = [f'{e[0]} -> {e[1]}' for e in get_timespan_partition_for_trajectory(trajectory)]

    trajectory_hash = dict_hash(dict(
        tweet_filepaths=tweet_filepaths,
        trajectory=trajectory,
    ))

    word_clouds_filepath = os.path.join(cache_folderpath, 'word_clouds', f"{trajectory_hash}-word_clouds.pkl.gz")
    if os.path.exists(word_clouds_filepath):
        with gzip.open(word_clouds_filepath, 'rb') as handle:
            word_clouds = pickle.load(handle)
        return word_clouds, timespans

    # - preparing the topic models based on support
    pipeline_args = dict(
        number_of_topics_for_lda=2,
                         autoencoder=None,
        representation_clustering=None,
        use_transformer=False,
        use_lda=True,
        use_tfidf=False,
        device=torch.device('cpu'),
        transformer_modelname='paraphrase-mpnet-base-v2',
        text_processor=TextProcessor(
         methods=[
             'remove_url',
             'convert_to_lowercase',
             'uppercase_based_missing_delimiter_fix',
             # 'gtlt_normalize',
             # 'substitute_more_than_two_letter_repetition_with_one',
             'non_character_repetition_elimination',
             # 'use_star_as_delimiter',
             # 'remove_parantheses_and_their_contents',
             'remove_questionexlamation_in_brackets',
             'eliminate_phrase_repetition',
             'strip'
         ]
        ),
        token_processor_light=TokenProcessor(
         methods=[
             'keep_alphabetics_only',
             # 'keep_nouns_only',
             # 'spell_check_and_typo_fix',
             # 'stem_words',
             # 'remove_stopwords'
         ]
        ),
        token_processor_heavy=TokenProcessor(
         methods=[
             'keep_alphabetics_only',
             # 'keep_nouns_only',
             # 'spell_check_and_typo_fix',
             # 'stem_words',
             # 'remove_stopwords'
         ]
    ))

    logger.info("2) preparing query trajectory dataset...")
    data, meta = prepare_trajectory_dataset(
        trajectory=trajectory,
        tweet_filepaths=tweet_filepaths,
        overwrite=False
    )

    pipeline = TransformerLDATopicModelingPipeline(
        **pipeline_args
    )

    logger.info("3) finding word clouds...")
    word_clouds_filepath = os.path.join(cache_folderpath, 'word_clouds', f"{trajectory_hash}-word_clouds.pkl.gz")
    # if os.path.exists(word_clouds_filepath):
    #     with gzip.open(word_clouds_filepath, 'rb') as handle:
    #         word_clouds = pickle.load(handle)
    # else:
    word_clouds = []
    for tmp_query_data in tqdm(data):
        query_preprocessed_text_list, query_preprocessed_tokens_list, query_indices = pipeline.preprocess_and_get_text_and_tokens(
            text_list=[e for e in tmp_query_data.tweet.tolist() if isinstance(e, str)],
            verbose=0
        )
        if len(query_preprocessed_text_list) == 0:
            word_clouds.append(
                plotly_wordcloud(' '.join(['NONE']), max_words=max_word_count)
            )
        else:
            word_clouds.append(
                plotly_wordcloud(' '.join(query_preprocessed_text_list), max_words=max_word_count)
            )
    with gzip.open(word_clouds_filepath, 'wb') as handle:
        pickle.dump(word_clouds, handle)

    return word_clouds, timespans
