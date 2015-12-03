
"""
Generation artificial data
--------------------------
This module groups all the functions related to generate different votes
artificial data.

"""

import numpy as np
import pandas as pd


class Generator_votes:

    def __init__(self, n_circuns, censo):
        pass

    def generate(self, n_parties):
        pass


def generate_artificial_votes(n_circuns, n_parties, censo):
    """Generate artificial data of votes.

    TODO
    ----
    Pass the censo, the type_votes proportion.
    Convert to a macrofunction which is able to handle different cases.
    """

    ## 0. Compute variables needed
    if type(censo) == int:
        censo = np.ones(n_circuns) * censo
        censo = censo.astype(int)

    ## 1. Proportion of votes for each party
    type_votes = np.random.random(3)
    big_parties = np.random.random(n_parties)
    corr_parties = np.random.random((n_circuns, n_parties))
    prop_votes = np.zeros((n_circuns, n_parties))
    for i in range(n_circuns):
        prop_votes[i, :] = big_parties * corr_parties[i, :] * type_votes[0]

    ## 2. Extension
    extension = np.ones((n_circuns, 2))
    extension[:, 0]*type_votes[1]
    extension[:, 1]*type_votes[2]
    prop_votes = np.hstack([prop_votes, extension])
    # Normalization
    for i in range(n_circuns):
        prop_votes[i, :] = prop_votes[i, :]/np.sum(prop_votes[i, :])

    ## 3. Distribution of votes
    votes = np.zeros((n_circuns, n_parties+2))
    for i in range(n_circuns):
        for j in range(censo[i]):
            r = np.random.random()
            k = wheeler_distribution(prop_votes[i, :], r)
            votes[i, k] += 1

    ## 4. Build the dataframe
    columns = list(range(n_parties)) + ['blancos', 'nulos']
    votes = pd.DataFrame(votes, columns=columns)

    return votes


def wheeler_distribution(prop, r):
    """Assign the vote to the box who contains r. TODO: move to pythonTools"""

    prop2 = np.cumsum(prop)
    for i in range(prop.shape[0]):
        if prop2[i] >= r:
            break
    return i
