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

from app.libraries.io.tweet_filepaths import get_tweet_filepaths
from app.libraries.randomization.hashing import dict_hash
from app.libraries.trajectory.utilities import prepare_trajectory_dataset, get_timespan_partition_for_trajectory

from app import cache_folderpath
from app.libraries.utilities.logging import get_logger
logger = get_logger(__name__)


def is_request_processed(
        query_institutions: List[str],
        query_step_in_days: int,
        query_min_date: str,
        query_max_date: str,
        query_terms: List[str]
) -> bool:
    """
    Parameters
    ----------
    query_institutions: `List[str]`, required
        The institutions to query.

    query_step_in_days: `int`, required
        The length of the time-step in days.

    query_min_date: `str`, required
        The minimum date to query.

    query_max_date: `str`, required
        The maximum date to query.

    query_terms: `List[str]`, required
        The terms to query.

    Returns
    -------
    Whether or not the request has been processed.
    """
    logger.info("1) getting filepaths...")
    tweet_filepaths = get_tweet_filepaths()
    trajectory = dict(
        state=None,
        institution_type=query_institutions,
        dates=(query_min_date, query_max_date, dict(years=0, months=0, days=query_step_in_days)))

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

    # - preparing the metadata
    meta = dict(
        tweet_filepaths=tweet_filepaths,
        trajectory=trajectory
    )

    # - reading from cache if needed
    final_filename = os.path.join(cache_folderpath, 'trajectory', dict_hash(meta) + '.pkl.gz')
    # if not os.path.exists(final_filename):
    #     return False

    preprocessed_text_and_tokens_filepath = os.path.join(
        cache_folderpath,
        'text_and_token',
        f"{trajectory_hash}-preprocessed_text_and_tokens.pkl.gz"
    )

    logger.info("3) preparing query trajectory data (processing)...")
    # if not os.path.exists(preprocessed_text_and_tokens_filepath):
    #     return False

    logger.info("4) checking word frequencies...")
    word_frequency_filepath = os.path.join(cache_folderpath, 'word_frequencies',
                                           f"{trajectory_hash}-word_frequency.pkl.gz")
    if not os.path.exists(word_frequency_filepath):
        return False
    return True


def get_word_frequency_data(
        query_institutions: List[str],
        query_step_in_days: int,
        query_min_date: str,
        query_max_date: str,
        query_terms: List[str]
) -> Any:
    """
    Parameters
    ----------
    query_institutions: `List[str]`, required
        The institutions to query.

    query_step_in_days: `int`, required
        The length of the time-step in days.

    query_min_date: `str`, required
        The minimum date to query.

    query_max_date: `str`, required
        The maximum date to query.

    query_terms: `List[str]`, required
        The terms to query.

    Returns
    -------
    The plotly figure data for the word frequency plot.
    """
    logger.info("1) getting filepaths...")
    tweet_filepaths = get_tweet_filepaths()
    trajectory = dict(
            state=None,
            institution_type=query_institutions,
            dates=(query_min_date, query_max_date, dict(years=0, months=0, days=query_step_in_days)))

    trajectory_hash = dict_hash(dict(
        tweet_filepaths=tweet_filepaths,
        trajectory=trajectory,
    ))

    word_frequency_filepath = os.path.join(cache_folderpath, 'word_frequencies',
                                           f"{trajectory_hash}-word_frequency.pkl.gz")
    if os.path.exists(word_frequency_filepath):
        try:
            with gzip.open(word_frequency_filepath, 'rb') as handle:
                word_freqs = pickle.load(handle)
            logger.info("2) processings are done already, preparing plotting info...")
            df_dict = {'count': [numpy.sum([word_freq[e] for e in query_terms]) for word_freq in word_freqs]}
            df_dict['x'] = [
                date_parser.parse(trajectory['dates'][0]).date() + e * relativedelta(**trajectory['dates'][2]) for e
                in range(len(df_dict['count']))]

            df = pandas.DataFrame(df_dict)
            fig = px.line(df, x='x', y='count', markers=True, template='plotly_white')
            fig.update_layout(title=f"Word-group occurrence through time: {query_terms}", xaxis_title="Date",
                              yaxis_title="Word Counts", )

            return fig
        except Exception as e:
            logger.error(f"failed to load the file located in {word_frequency_filepath}, re-creating it...\n\terror: {e}")

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

    pipeline_args_to_hash = dict(
        number_of_topics_for_lda=2,
        autoencoder=None,
        representation_clustering=None,
        use_transformer=False,
        use_lda=True,
        use_tfidf=False,
        device='cpu',
        transformer_modelname='paraphrase-mpnet-base-v2',
        text_processor=dict(
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
        token_processor_light=dict(
         methods=[
             'keep_alphabetics_only',
             # 'keep_nouns_only',
             # 'spell_check_and_typo_fix',
             # 'stem_words',
             # 'remove_stopwords'
         ]
        ),
        token_processor_heavy=dict(
         methods=[
             'keep_alphabetics_only',
             # 'keep_nouns_only',
             'spell_check_and_typo_fix',
             'stem_words',
             'remove_stopwords'
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
    preprocessed_text_and_tokens_filepath = os.path.join(
        cache_folderpath,
        'text_and_token',
        f"{trajectory_hash}-preprocessed_text_and_tokens.pkl.gz"
    )

    logger.info("3) preparing query trajectory data (processing)...")
    if os.path.exists(preprocessed_text_and_tokens_filepath):
        with gzip.open(preprocessed_text_and_tokens_filepath, 'rb') as handle:
            preprocessed_text_list, preprocessed_tokens_list, indices = pickle.load(handle)
    else:
        preprocessed_text_list, preprocessed_tokens_list, indices = pipeline.preprocess_and_get_text_and_tokens(
            text_list=[e for e in data[0].tweet.tolist() if isinstance(e, str)],
            verbose=1
        )
        with gzip.open(preprocessed_text_and_tokens_filepath, 'wb') as handle:
            pickle.dump((preprocessed_text_list, preprocessed_tokens_list, indices), handle)

    logger.info("4) finding word frequencies...")

    os.makedirs(os.path.join(cache_folderpath, 'word_frequencies'), exist_ok=True)
    # word_frequency_filepath = os.path.join(cache_folderpath, 'word_frequencies', f"{trajectory_hash}-word_frequency.pkl.gz")
    # if os.path.exists(word_frequency_filepath):
    #     with gzip.open(word_frequency_filepath, 'rb') as handle:
    #         word_freqs = pickle.load(handle)
    # else:
    word_freqs = []
    for tmp_query_data in tqdm(data):
        query_preprocessed_text_list, query_preprocessed_tokens_list, query_indices = pipeline.preprocess_and_get_text_and_tokens(
            text_list=[e for e in tmp_query_data.tweet.tolist() if isinstance(e, str)],
            verbose=0
        )

        if len(query_preprocessed_text_list) == 0:
            query_preprocessed_text_list = ['none']
        try:
            word_freqs.append(
                nltk.FreqDist(
                    [word for tweet_words in [e.split() for e in query_preprocessed_text_list] for word in tweet_words])
            )
        except:
            import pdb
            pdb.set_trace()
    with gzip.open(word_frequency_filepath, 'wb') as handle:
        pickle.dump(word_freqs, handle)

    logger.info("5) all done, preparing plotting info.")
    df_dict = {'count': [numpy.sum([word_freq[e] for e in query_terms]) for word_freq in word_freqs]}
    df_dict['x'] = [
        date_parser.parse(trajectory['dates'][0]).date() + e * relativedelta(**trajectory['dates'][2]) for e
        in range(len(df_dict['count']))]

    df = pandas.DataFrame(df_dict)
    fig = px.line(df, x='x', y='count', markers=True, template='plotly_white')
    fig.update_layout(title=f"Word-group occurrence through time: {query_terms}", xaxis_title="Date", yaxis_title="Word Counts",)

    return fig
