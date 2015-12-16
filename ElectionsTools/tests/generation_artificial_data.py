
"""
Generation artificial data
--------------------------
This module groups all the functions related to generate different votes
artificial data.

"""

import numpy as np
import pandas as pd


class Generator_votes:
    """Generation of artificial data of votes object.
    """
    n_circuns = 0
    censo = np.zeros(1)
    type_votes = ['partido', 'blancos', 'nulos', 'abstencion']
    w_type_vts = np.array([.55, .05, .05, .35])
    n_parties = 0
    abstention = False

    def __init__(self, n_circuns, censo, type_votes=None, w_type_vts=None,
                 abstention=None):
        ## 0. Compute variables needed
        censo = formatting_censo(censo, n_circuns)
        self.n_circuns = n_circuns
        self.censo = censo
        self.type_votes = self.type_votes if type_votes is None else type_votes
        self.w_type_vts = self.w_type_vts if w_type_vts is None else w_type_vts
        self.abstention = self.abstention if abstention is None else abstention

    def generate(self, parties_info):
        """Generate random correlation between parties.

        Parameters
        ----------
        parties_info: numpy.ndarray or int
            the weights of the parties or the number of them.

        Returns
        -------
        votes: pandas.DataFrame
            the votes data.

        """
        ## 0. Generate needed variables
        n_parties, corr_parties = formatting_parties_info(parties_info,
                                                          self.n_circuns)
        corr_options = build_corr_options(corr_parties, self.w_type_vts)

        ## 1. Votes creation
        votes = distributing_votes(corr_options, self.censo)
        votes = building_votes(votes, n_parties, self.type_votes,
                               self.abstention)

        return votes


def building_votes(votes, n_parties, type_votes, abstention=False):
    """Buiding the vote data.
    """

    ## 0. Variable needed
    name_parties = [type_votes[0]+'_'+str(i) for i in range(n_parties)]
    if abstention:
        columns = name_parties + type_votes[1:]
    else:
        columns = name_parties + type_votes[1:-1]
        votes = votes[:, :-1]
    ## 1. Dataframe
    votes = pd.DataFrame(votes, columns=columns)
    return votes


def build_corr_options(corr_parties, w_type_vts):
    """Build the correlation weights for all the options of voting.

    Parameters
    ----------
    corr_parties: numpy.ndarray
        the correlation between votes of parties.
    w_type_vts: numpy.ndarray
        the weights between the options in a poll.

    Returns
    -------
    corr_options: numpy.ndarray
        the correlation options weights.

    """
    ## 0. Corr
    n_circuns = corr_parties.shape[0]
    ## 1. Weighting parties
    corr_parties = corr_parties * w_type_vts[0]
    ## 2. Building extensions
    extension = np.ones((n_circuns, 3))
    extension[:, 0] = extension[:, 0]*w_type_vts[1]
    extension[:, 1] = extension[:, 1]*w_type_vts[2]
    extension[:, 2] = extension[:, 2]*w_type_vts[3]
    corr_options = np.hstack([corr_parties, extension])
    ## 3. Normalization
    for i in range(n_circuns):
        corr_options[i, :] = corr_options[i, :]/np.sum(corr_options[i, :])
    return corr_options


def generate_random_corrparties(n_circuns, parties_info):
    """Generate random correlation between parties.

    Parameters
    ----------
    n_circuns: int
        the number of circunscriptions we want to consider.
    parties_info: numpy.ndarray or int
        the weights of the parties or the number of them.

    Returns
    -------
    prop_votes: numpy.ndarray
        the correlation weights of votes of the candidatures.

    """
    ## 0. Prepare parties information
    if type(parties_info) == int:
        n_parties = parties_info
        big_parties = np.random.random(n_parties)
    elif type(parties_info) in [np.ndarray, list]:
        big_parties = parties_info
        n_parties = big_parties.shape[0]

    ## 1. Generate random correlations
    corr_parties = np.random.random((n_circuns, n_parties))
    prop_votes = np.zeros((n_circuns, n_parties))
    for i in range(n_circuns):
        aux = big_parties * corr_parties[i, :]
        # Normalization
        prop_votes[i, :] = aux/np.sum(aux)
    return prop_votes


def formatting_parties_info(parties_info, n_circuns):
    """Correct the format of parties_info and return the number of parties
    and the correlation of vote weights between them.

    Parameters
    ----------
    parties_info: numpy.ndarray or int
        the weights of the parties or the number of them.
    n_circuns: int
        the number of circunscriptions we want to consider.

    Returns
    -------
    n_parties: int
        the number of parties.
    corr_parties: numpy.ndarray
        the correlation weights of votes of the candidatures.

    """
    if type(parties_info) in [int, list]:
        corr_parties = generate_random_corrparties(n_circuns, parties_info)
        n_parties = parties_info
    elif type(parties_info) == np.ndarray:
        if len(parties_info.shape) == 1:
            corr_parties = generate_random_corrparties(n_circuns, parties_info)
            n_parties = parties_info.shape[0]
        elif len(parties_info.shape) == 2:
            corr_parties = parties_info
            n_parties = parties_info.shape[1]

    return n_parties, corr_parties


def formatting_censo(censo, n_circuns):
    if type(censo) == int:
        censo = np.ones(n_circuns) * censo
        censo = censo.astype(int)
    assert censo.shape[0] == n_circuns
    return censo


def distributing_votes(prop_votes, censo):
    ## 0. Compute needed variables
    n_circuns, n_options = prop_votes.shape
    ## 1. Distribution of votes
    votes = np.zeros((n_circuns, n_options))
    for i in range(n_circuns):
        for j in range(censo[i]):
            r = np.random.random()
            k = wheeler_assignation(prop_votes[i, :], r)
            votes[i, k] += 1
    return votes


def generate_artificial_votes(n_circuns, n_parties, censo):
    """Generate artificial data of votes.

    TODO
    ----
    Pass the censo, the w_type_vts proportion.
    Convert to a macrofunction which is able to handle different cases.
    """

    ## 0. Compute variables needed
    censo = formatting_censo(censo, n_circuns)

    ## 1. Proportion of votes for each party
    w_type_vts = np.random.random(3)
    big_parties = np.random.random(n_parties)
    corr_parties = np.random.random((n_circuns, n_parties))
    prop_votes = np.zeros((n_circuns, n_parties))
    for i in range(n_circuns):
        prop_votes[i, :] = big_parties * corr_parties[i, :] * w_type_vts[0]

    ## 2. Extension
    extension = np.ones((n_circuns, 2))
    extension[:, 0]*w_type_vts[1]
    extension[:, 1]*w_type_vts[2]
    prop_votes = np.hstack([prop_votes, extension])
    # Normalization
    for i in range(n_circuns):
        prop_votes[i, :] = prop_votes[i, :]/np.sum(prop_votes[i, :])

    ## 3. Distribution of votes
    votes = distributing_votes(prop_votes, censo)

    ## 4. Build the dataframe
    columns = list(range(n_parties)) + ['blancos', 'nulos']
    votes = pd.DataFrame(votes, columns=columns)

    return votes


def wheeler_assignation(prop, r):
    """Assign the vote to the box who contains r. TODO: move to pythonTools"""

    prop2 = np.cumsum(prop)
    for i in range(prop.shape[0]):
        if prop2[i] >= r:
            break
    return i
