# coding=utf-8
import numpy as np

from evolutron.tools import io_tools as io

file_db = {
    'random': 'random_aa.fasta',
    'type2p': 'type2p_ps_aa.fasta',
    'hsapiens': 'sprot_hsapiens_pfam.tsv',
    'ecoli': 'sprot_ecoli_pfam.tsv',
    'zinc': 'sprot_znf_prot_pfam.tsv',
    'homeo': 'sprot_homeo_pfam.tsv',
    'crispr': 'sprot_crispr_pfam.tsv',
    'cas9': 'sprot_cas9_pfam.tsv',
    'cd4': 'sprot_cd4_pfam.tsv',
    'dnabind': 'sprot_dna_tf_pfam.tsv',
    'SecS': 'SecS.sec',
    'smallSecS': 'smallSecS.sec',
    'tinySecS': 'tinySecS.sec',
    'cullPDB': 'cullpdb+profile_6133_filtered.npy.gz',
    'cb513': 'cb513+profile_split1.npy.gz',
    'human_ors': 'uniprot_human_ors.tsv',
    'casp10': 'casp10.sec',
    'casp11': 'casp11.sec'
}


def data_it(dataset, block_size):
    """ Iterates through a large array, yielding chunks of block_size.
    """
    size = len(dataset)

    for start_idx in range(0, size, block_size):
        excerpt = slice(start_idx, min(start_idx + block_size, size))
        yield dataset[excerpt]


def pad_or_clip(x, n):
    if n >= x.shape[0]:
        return np.concatenate((x[:n, :], np.zeros((n - x.shape[0], x.shape[1]))))
    else:
        return x[:n, :]


def load_dataset(data_id, padded=True, min_aa=None, max_aa=None, i_am_kfir=False, **parser_options):
    """Fetches the correct dataset from database based on data_id.
    """
    try:
        filename = file_db[data_id]
        filetype = filename.split('.')[-1]
    except KeyError:
        raise IOError('Dataset id not in file database.')

    if filetype == 'tsv':
        x_data, y_data = io.tab_parser('datasets/' + filename, **parser_options)
    elif filetype == 'fasta':
        x_data, y_data = io.fasta_parser('datasets/' + filename, **parser_options)
    elif filetype == 'sec':
        x_data, y_data = io.SecS_parser('datasets/' + filename, **parser_options)
    elif filetype == 'gz':
        x_data, y_data = io.npz_parser('datasets/' + filename, **parser_options)
    else:
        raise NotImplementedError('There is no parser for current file type.')

    if padded:
        if not max_aa:
            max_aa = int(np.percentile([len(x) for x in x_data], 99))  # pad so that 99% of datapoints are complete
        else:
            # ToDo: I changed the min to max (seems to make sense), check if that's good for you!
            if i_am_kfir:
                max_aa = max(max_aa, np.max([len(x) for x in x_data]))
            else:
                max_aa = min(max_aa, np.max([len(x) for x in x_data]))

        x_data = np.asarray([pad_or_clip(x, max_aa) for x in x_data])

        if i_am_kfir:
            try:
                y_data = np.asarray([pad_or_clip(y, max_aa) for y in y_data])
                return x_data, y_data
            except:
                pass

    data_size = len(x_data)

    if not y_data:
        # Unsupervised Learning
        # x_data: observations

        print('Dataset size: {0}'.format(data_size))
        return x_data
    else:
        # Supervised Learning
        # x_data: observations
        # y_data: class labels
        try:
            assert (len(x_data) == len(y_data))
        except AssertionError:
            raise IOError('Unequal lengths for X ({0}) and y ({1})'.format(len(x_data), len(y_data)))

        print('Dataset size: {0}'.format(data_size))
        return x_data, np.asarray(y_data, dtype=np.int32)

