
"""
Major_residual
--------------
Assignation of seats using major residual.


TODO
----
Compute properly residuals
compute unused votes
"""

import numpy as np
from seats_assignation import Seat_assignator, recalibrate_cutoff,\
    prepare_votetypes


class MResidual_assignation(Seat_assignator):
    """Major residual assignation of seats from votes.
    """

    def __init__(self, n_seats, votetypes):
        "Initialization of the parameters of the specific assignation."
        self.votetypes, self.n_seats = votetypes, n_seats

    def assignation(self, votes, cutoff=0):
        """Major residual assignation.

        Parameters
        ----------
        votes: numpy.ndarray
            the votes of the seatable votes.
        cutoff: numpy.ndarray or float [0, 1)
            the proportion of votes required to get a seat.

        Returns
        -------
        seats: numpy.ndarray
            the seats assigned to each party.
        prices: float
            the prices payed (in votes) for each seat for each circunscription.

        """
        ## 0. Prepare variable needed
        self.votetypes = prepare_votetypes(self.votetypes)
        ## 1. Compute assignation
        seats, prices = transform_votes2seats_mresidual(votes, self.votetypes,
                                                        self.n_seats, cutoff)
        return seats, prices


def mresidual_method(votes, n_seats, cutoff=0):
    """Proportional assignation using major residual assignation.

    Parameters
    ----------
    votes: pandas.DataFrame
        the votes of the seatable votes.
    n_seats: int
        the number of the seats to assign.
    cutoff: float [0, 1)
        the proportion of votes required to get a seat.

    Returns
    -------
    seats: numpy.ndarray
        the seats assigned to each party.
    residuals: numpy.ndarray
        the residuals fractions.

    """

    n_total_votes = votes.sum()
    abs_cutoff = cutoff*n_total_votes

    computable_votes = np.zeros(votes.shape)
    computable_votes[votes >= abs_cutoff] = votes[votes >= abs_cutoff]

    n_comp_votes = computable_votes.sum()
    ratio = computable_votes/n_comp_votes
    seats = np.floor(ratio*n_seats)
    residuals = ratio*n_seats-seats

    rest = int(n_seats-np.sum(seats))
    for i in range(rest):
        s = np.argmax(residuals)
        residuals[s] = 0
        seats[s] += 1

    seats = seats.astype(int)

    return seats, residuals


def transform_votes2seats_mresidual(votes, votetypes, n_seats, cutoff):
    """The general method to transform the different circunscriptions votes
    into seats using major residual method.

    Parameters
    ----------
    votes: pandas.DataFrame
        the votes of the seatable votes.
    votetypes: dict
        the information of the different types of vote variables.
    n_seats: int
        the number of the seats to assign.
    cutoff: float [0, 1)
        the proportion of votes required to get a seat.

    Returns
    -------
    seats: numpy.ndarray
        the seats assigned to each party.
    residuals: numpy.ndarray
        the residuals fractions for each circunscription.

    """

    ## 0. Compute needed variables
    n, m_v = votes.shape[0], len(votetypes['seatable'])
    n_seats = np.ones(n)*n_seats if type(n_seats) == int else n_seats
    cutoff = np.ones(n)*cutoff if type(cutoff) == int else cutoff

    ## 1. Recompute cutoff only for seatable votes
    seatable_votes = np.sum(votes[votetypes['seatable']].as_matrix(), axis=1)
    computable_votes = np.sum(votes[votetypes['computable']].as_matrix(),
                              axis=1)
    cutoff = recalibrate_cutoff(seatable_votes, computable_votes, cutoff)
    seatable_votes = votes[votetypes['seatable']].as_matrix()

    ## 2. Major residual assignation
    seats, residuals = np.zeros((n, m_v)), np.zeros((n, m_v))
    for i in range(n):
        seats[i, :], residuals[i, :] = mresidual_method(seatable_votes[i, :],
                                                        n_seats[i], cutoff[i])

    return seats, residuals
