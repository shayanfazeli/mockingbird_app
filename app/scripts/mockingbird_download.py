import argparse
import os
import pandas
from tqdm import tqdm
# from app import accounts_df_filepath
accounts_df_filepath = "./warehouse/data/refocus/accounts.csv"
if __name__ == "__main__":
    # - parsing the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_time', type=str, required=True, help="""
    example use: --start_time="2022-10-10 16:30:00"
    """)
    parser.add_argument('--end_time', type=str, required=True, help="""
    example use: --end_time="2022-11-01 16:30:00"
    """)
    parser.add_argument('--output_repo', type=str, required=True, help="""
    the output repository, that must NOT exist in advance.
    """)
    parser.add_argument('--meta', type=str, default=None, required=False, help="""
        the output repository, that must NOT exist in advance.
        """)
    args = parser.parse_args()
    assert not os.path.isdir(args.output_repo), f"the output repository {args.output_repo} must NOT exist in advance."
    os.makedirs(args.output_repo)

    # - reading the metadata
    if args.meta is None:
        df = pandas.read_csv(accounts_df_filepath)
    else:
        df = pandas.read_csv(args.meta)

    # - reading the handles
    user_handles = sorted(list(set(df['Twitter handle'].tolist())))

    keep_going = True
    for user_handle in tqdm(user_handles):
        # if keep_going:
        #     if user_handle == 'CBP':  # last-fetched account~/
        #         keep_going = False
        #     continue
        os.system(f'twint -u {user_handle}  --since "{args.start_time}" --until "{args.end_time}" -o {os.path.join(args.output_repo, user_handle)}.csv --csv -ho')
        print(f"\n{user_handle} tweets are fetched.")
