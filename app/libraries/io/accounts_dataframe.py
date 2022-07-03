import os
import pandas
from app import accounts_df_filepath
from app.libraries.meta.us import us_state_abbrs


def read_accounts_df() -> pandas.DataFrame:
    accounts_df = pandas.read_csv(accounts_df_filepath)
    accounts_df.rename({
        'Organization type': 'institution_type',
        'Organization name': 'institution_name',
        'Twitter handle': 'twitter_handle',
        'County': 'county',
        'State': 'state'
    }, inplace=True, errors='raise', axis=1)
    accounts_df.state = accounts_df.state.apply(lambda x: 'none' if pandas.isna(x) else us_state_abbrs[x])

    return accounts_df
