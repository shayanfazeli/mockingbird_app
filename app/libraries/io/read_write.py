import gzip
import pickle


def write_pkl_gz(data, filepath):
    with gzip.open(filepath, 'wb') as handle:
        pickle.dump(data, handle)


def read_pkl_gz(filepath):
    with gzip.open(filepath, 'rb') as handle:
        return pickle.load(handle)
