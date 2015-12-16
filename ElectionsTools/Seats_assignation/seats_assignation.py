
"""
TODO
----
implement checkers of the properties described in
http://blog.pseudolog.com/article/la-ley-d-hont

collapser
check votes in the next step have nulos and blancos included.
"""


import pandas as pd
import numpy as np


noncomputable = ['nulos', 'abstencion']
nonseatable = ['blancos', 'nulos', 'abstencion']


class Seat_assignator:

    def compute_seatable_votes(self, votes):
        """Compute the seatable votes.

        Parameters
        ----------
        votes: pandas.DataFrame
            the votes of the seatable votes.
        votetypes: dict
            the information of the different types of vote variables.

        Returns
        -------
        seatable_votes: numpy.ndarray
            the variables which have votes which can be transformed into seats.
        """
        seatable_votes = compute_seatable_votes(votes, self.votetypes)
        return seatable_votes

    def compute_computable_votes(self, votes):
        """Compute the seatable votes.

        Parameters
        ----------
        votes: pandas.DataFrame
            the votes of the seatable votes.

        Returns
        -------
        computable_votes: numpy.ndarray
            the variables which have votes which can be computed in order to
            use the cutoff.

        """
        computable_votes = compute_computable_votes(votes, self.votetypes)
        return computable_votes

    def compute_mask_cutoff(self, votes, cutoff=0):
        """Compute the mask of the votes who are over cutoff.

        Parameters
        ----------
        votes: pandas.DataFrame
            the votes of the seatable votes.
        cutoff: numpy.ndarray or float [0, 1)
            the proportion of votes required to get a seat.

        Returns
        -------
        computable_votes: numpy.ndarray
            the variables which have votes which can be computed in order to
            use the cutoff.

        """

        seatable_votes = self.compute_seatable_votes(votes)
        computable_votes = self.compute_computable_votes(votes)
        cutoff = recalibrate_cutoff(seatable_votes, computable_votes, cutoff)
        mask_cutoff = np.zeros(seatable_votes.shape).astype(bool)
        for i in range(votes.shape[1]):
            mask_cutoff = seatable_votes > cutoff * seatable_votes.sum(1)
        return mask_cutoff


class Mix_assignation(Seat_assignator):
    """The parameters needed is a list of seats (ns_seats) to apply the
    different methods.
    """

    def __init__(self, ns_seats, assignators, votetypes):
        """Initialization of the parameters of the specific assignation.

        Parameters
        ----------
        ns_seats: list
            the number of seats for each step of the process and each
            circunscription.
        assignators: list
            the assignators classes to compute the distribution of seats.
        votetypes: dict
            the type of votes for each column.

        """
        self.votetypes, self.ns_seats = votetypes, ns_seats
        self.assignators = assignators

    def assignation(self, votes, cutoff=0):
        ## 0. Compute variable needed (general vote info)
        for i in range(len(self.assignators)):
            ## 1. Inialize object method
            assignator_i = self.assignator[i](self.ns_seats[i], self.votetypes)
            ## 2. Assign seats
            seats, aux = assignator_i.assignation(votes, cutoff)
            ## 3. Compute residual votes
            votes = assignator_i.compute_unused_votes(seatable_votes, seats,
                                                      aux, cutoff)
            ## 4. Transform votes (collapsing)
        return seats


def transform_votes2seats_hondt(votes, votetypes, n_seats, cutoff=0):
    """
    """

    (n, m), m_v = votes.shape, len(votetypes['seatable'])

    n_seats = np.ones(n)*n_seats if type(n_seats) == int else n_seats
    cutoff = np.ones(n)*cutoff if type(cutoff) == int else cutoff
    seatable_votes = np.sum(votes[votetypes['seatable']].as_matrix(), axis=1)
    computable_votes = np.sum(votes[votetypes['computable']].as_matrix(),
                              axis=1)
    cutoff = recalibrate_cutoff(seatable_votes, computable_votes)
    seatable_votes = votes[votetypes['seatable']].as_matrix()

    seats, ps = np.zeros((n, m_v)), np.zeros(n)
    for i in range(n):
        seats[i, :], ps[i] = hondt_method(seatable_votes[i, :], n_seats[i],
                                          cutoff[i])


    v_restantes = computable_votes - np.multiply(ps, seats.T).T

    major_residual_method(v_restantes, n_seats, cutoff=0)

    return seats


def recalibrate_cutoff(seatable_votes, computable_votes, cutoff):
    """Recalibrate the cutoff in order to get rid of the "votos en blanco".

    Parameters
    ----------
    seatable_votes: numpy.ndarray
        the variables which have votes which can be transformed into seats.
    computable_votes: numpy.ndarray
        the computable votes in order to study proportion or threshold with the
        cutoff.
    cutoff: int or numpy.ndarray
        the ratio threshold of votes for adquiring a seat.

    Returns
    -------
    new_cutoff: numpy.ndarray
        recomputed cutoff in order to get rid of the "votos en blanco" and keep
        the proper threshold.

    """
    n_dim1, n_dim2 = len(computable_votes.shape), len(seatable_votes.shape)
    if type(cutoff) == int:
        cutoff = np.ones(seatable_votes.shape[0])*cutoff
    if n_dim1 == 2:
        computable_votes = np.sum(computable_votes, axis=1)
    if n_dim2 == 2:
        seatable_votes = np.sum(seatable_votes, axis=1)

    abs_cutoff = cutoff * computable_votes
    new_cutoff = abs_cutoff / seatable_votes
    return new_cutoff


def prepare_votetypes(votes, votetypes):
    """It completes the votetypes dictionary in order to include the
    computable and the seatable votes.

    Parameters
    ----------
    votes: pandas.DataFrame
        the votes of the seatable votes.
    votetypes: dict
        the information of the different types of vote variables.

    Returns
    -------
    votetypes: dict
        the information of the different types of vote variables.

    """
    cols = votes.columns
    votetypes['computable'] = [c for c in cols if c not in noncomputable]
    votetypes['seatable'] = [c for c in cols if c not in nonseatable]
    return votetypes


def compute_seatable_votes(votes, votetypes):
    """Compute the seatable votes.

    Parameters
    ----------
    votes: pandas.DataFrame
        the votes of the seatable votes.
    votetypes: dict
        the information of the different types of vote variables.

    Returns
    -------
    seatable_votes: numpy.ndarray
        the variables which have votes which can be transformed into seats.

    """
    votetypes = prepare_votetypes(votes, votetypes)
    seatable_votes = votes[votetypes['seatable']]
    return seatable_votes


def compute_computable_votes(votes, votetypes):
    """Compute the seatable votes.

    Parameters
    ----------
    votes: pandas.DataFrame
        the votes of the seatable votes.
    votetypes: dict
        the information of the different types of vote variables.

    Returns
    -------
    computable_votes: numpy.ndarray
        the variables which have votes which can be computed in order to use
        the cutoff.

    """
    votetypes = prepare_votetypes(votes, votetypes)
    computable_votes = votes[votetypes['computable']]
    return computable_votes
