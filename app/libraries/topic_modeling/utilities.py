from typing import List
import os
import pickle
import gzip
import numpy
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
from app.libraries.trajectory.utilities import prepare_trajectory_dataset

from app import cache_folderpath
from app.libraries.utilities.logging import get_logger
logger = get_logger(__name__)


def get_topic_modeling_data(
        support_institutions: List[str],
        query_institutions: List[str],
        topic_counts: int,
        support_min_date: str,
        support_max_date: str,
        query_step_in_days: int,
        query_min_date: str,
        query_max_date: str
) -> dict:
    logger.info("1) getting filepaths...")
    tweet_filepaths = get_tweet_filepaths()
    trajectories = dict(
        support=dict(
            state=None,
            institution_type=support_institutions,
            dates=(support_min_date, support_max_date, dict(years=10, months=0, days=0))),
        query=dict(
            state=None,
            institution_type=query_institutions,
            dates=(query_min_date, query_max_date, dict(years=0, months=0, days=query_step_in_days))))

    trajectory_hashes = dict(
        support=dict_hash(dict(
            tweet_filepaths=tweet_filepaths,
            trajectory=trajectories['support'],
        )),
        query=dict_hash(dict(
            tweet_filepaths=tweet_filepaths,
            trajectory=trajectories['query'],
        )))

    # - preparing the topic models based on support
    pipeline_args = dict(
        number_of_topics_for_lda=topic_counts,
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
                                 'spell_check_and_typo_fix',
                                 'stem_words',
                                 'remove_stopwords'
                             ]
                         ))

    pipeline_args_to_hash = dict(
        number_of_topics_for_lda=topic_counts,
        autoencoder=None,
        representation_clustering=None,
        use_transformer=False,
        use_lda=True,
        use_tfidf=False,
        device='cuda:0',
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

    pipeline_hash = dict_hash(pipeline_args_to_hash)
    exp_id = f"{pipeline_hash}_{trajectory_hashes['support']}"
    pipeline_filepath = os.path.join(cache_folderpath, 'topic_model', f"{exp_id}_ckpt.pkl.gz")
    pipeline_vis_filepath = os.path.join(cache_folderpath, 'lda_visualization', f'{exp_id}.pkl.gz')

    logger.info("2) preparing support trajectory dataset...")
    data, meta = prepare_trajectory_dataset(
        trajectory=trajectories['support'],
        tweet_filepaths=tweet_filepaths,
        overwrite=False
    )

    pipeline = TransformerLDATopicModelingPipeline(
        **pipeline_args
    )
    preprocessed_text_and_tokens_filepath = os.path.join(
        cache_folderpath,
        'text_and_token'
        f"{trajectory_hashes['support']}-preprocessed_text_and_tokens.pkl.gz"
    )

    logger.info("3) preparing support trajectory data (processing)...")
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

    logger.info("4) fitting support topic model...")
    if os.path.exists(pipeline_filepath):
        print(f"loading (already fitted) [exp id: {exp_id}]...")
        with gzip.open(pipeline_filepath, 'rb') as handle:
            pipeline = pickle.load(handle)

        with gzip.open(pipeline_vis_filepath, 'rb') as handle:
            vis = pickle.load(handle)
    else:
        print(f"fitting [exp id: {exp_id}]...")
        pipeline.prepare_lda_model(
            tokens_list=preprocessed_tokens_list,
            lda_worker_count=20)
        vis = pyLDAvis.gensim_models.prepare(
            pipeline.lda_model,
            pipeline.corpus,
            pipeline.vocabulary,
            mds='mmds')
        with gzip.open(pipeline_filepath, 'wb') as handle:
            pickle.dump(pipeline, handle)
        with gzip.open(pipeline_vis_filepath, 'wb') as handle:
            pickle.dump(vis, handle)

    logger.info("5) preparing query trajectory data...")
    # - computing the topic trajectories
    data, meta = prepare_trajectory_dataset(
        trajectory=trajectories['query'],
        tweet_filepaths=tweet_filepaths,
        overwrite=False
    )

    logger.info("6) preparing query trajectory  trends...")

    trajectory_trends_filepath = os.path.join(cache_folderpath, 'trends', f"{trajectory_hashes['query']}_{exp_id}-trends.pkl.gz")

    if os.path.exists(trajectory_trends_filepath):
        with gzip.open(trajectory_trends_filepath, 'rb') as handle:
            df, topic_probabilities = pickle.load(handle)
    else:
        topic_probabilities = []

        for tmp_query_data in tqdm(data):
            query_preprocessed_text_list, query_preprocessed_tokens_list, query_indices = pipeline.preprocess_and_get_text_and_tokens(
                text_list=[e for e in tmp_query_data.tweet.tolist() if isinstance(e, str)],
                verbose=1
            )
            res = pipeline.get_lda_representations(query_preprocessed_tokens_list)
            topic_probabilities += [res.mean(axis=0)]

        topic_probabilities = numpy.stack(topic_probabilities, axis=0)
        df_dict = {f't{i}': topic_probabilities[:, i - 1] for i in range(1, 1 + topic_probabilities.shape[1])}
        df_dict['x'] = [
            date_parser.parse(trajectories['query']['dates'][0]).date() + e * relativedelta(**trajectories['query']['dates'][2]) for e
            in range(df_dict['t1'].shape[0])]

        df = pandas.DataFrame(df_dict)
        with gzip.open(trajectory_trends_filepath, 'wb') as handle:
            pickle.dump((df, topic_probabilities), handle)

    fig = px.line(df, x='x', y=[f't{i}' for i in range(1, 1+topic_probabilities.shape[1])], markers=True,
                  template='plotly_dark')
    fig.update_layout(title="Topic trajectories through time")
    return vis, fig
