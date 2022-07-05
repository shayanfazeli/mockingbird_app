import argparse
import os
import pandas
from tqdm import tqdm
from app import accounts_df_filepath

if __name__ == "__main__":
    # - parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_time', type=str, required=True, help="""
    example use: --start_time="2022-05-21 16:30:00"
    """)
    parser.add_argument('--end_time', type=str, required=True, help="""
    example use: --end_time="2022-05-21 16:30:00"
    """)
    parser.add_argument('--output_repo', type=str, required=True, help="""
    the output repository, that must NOT exist in advance.
    """)
    args = parser.parse_args()
    assert not os.path.isdir(args.output_repo), f"the output repository {args.output_repo} must NOT exist in advance."
    os.makedirs(args.output_repo)

    # - reading the metadata
    df = pandas.read_csv(accounts_df_filepath)

    # - reading the handles
    user_handles = sorted(list(set(df['Twitter handle'].tolist())))

    for user_handle in tqdm(user_handles):
        os.system(f'twint -u {user_handle}  --since "{args.start_time}" --until "{args.end_time}" -o {os.path.join(args.output_repo, user_handle)}.csv --csv -ho')
        print(f"\n{user_handle} tweets are fetched.")
