
"""
artificial data creation
------------------------
Functions to create artificial data.

"""

import numpy as np


def run_vots1(n_parties, n_vots):
    """Random creation of transition of votes.

    Parameters
    ----------
    n_parties: int
        the number of parties.
    n_vots: int
        the number of votes.

    Returns
    -------
    corr: np.ndarray
        the transition between one to other.

    """
    v = np.random.randint(1, 3, (n_vots, n_parties)).astype(int)
    corr, v[:, 0] = np.zeros((n_parties, n_parties)), 0
    for i in xrange(n_vots):
        for j in range(n_parties):
            corr[j, v[i, j] == v[i, :]] += 1
    return corr


def run_vots2(n_parties, n_vots):
    """Random creation of transition of votes.

    Parameters
    ----------
    n_parties: int
        the number of parties.
    n_vots: int
        the number of votes.

    Returns
    -------
    corr: np.ndarray
        the transition between one to other.

    """
    v = np.ones((n_vots, n_parties))*np.random.randint(0, 3, n_parties)
    v = v.astype(int)
    corr, v[:, 0] = np.zeros((n_parties, n_parties)), 0
    for i in xrange(n_vots):
        for j in range(n_parties):
            corr[j, v[i, j] == v[i, :]] += 1
    return corr
