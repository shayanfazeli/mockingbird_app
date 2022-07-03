import os
from typing import List
from app import tweets_repo


def get_tweet_filepaths() -> List[str]:
    root_dirs = [os.path.join(tweets_repo, e) for e in os.listdir(tweets_repo) if os.path.isdir(os.path.join(tweets_repo, e))]
    tweet_filepaths = [os.path.join(root_dir, e) for root_dir in root_dirs for e in os.listdir(root_dir) if os.path.exists(os.path.join(root_dir,  e)) and e.lower().endswith('.csv')]
    return tweet_filepaths
