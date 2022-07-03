import os
from dotenv import load_dotenv

# preparing some inner variables
base_directory = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_directory, '.env'))


class Configurations(object):
    """
    The :class:`Configurations` holds the main configuration parameters used in `Mockingbird`.
    """
    mockingbird_core_folder = os.environ.get('MOCKINGBIRD_CORE')
    accounts_df_filepath = os.environ.get('ACCOUNTS_DF_FILEPATH')
    tweets_root = os.environ.get('TWEETS_ROOT')
    cache_folderpath = os.environ.get('CACHE_FOLDERPATH')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key2'
    ADMINS = ['shayan@cs.ucla.edu']
    LANGUAGES = ['en']
