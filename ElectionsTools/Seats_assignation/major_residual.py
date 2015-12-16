
"""
Major_residual
--------------
Assignation of seats using major residual.


TODO
----
"""

import numpy as np
from seats_assignation import Seat_assignator, recalibrate_cutoff,\
    prepare_votetypes


class MResidual_assignation(Seat_assignator):
    """Major residual assignation of seats from votes.
    """

    def __init__(self, n_seats, votetypes={}):
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
        self.votetypes = prepare_votetypes(votes, self.votetypes)
        ## 1. Compute assignation
        seats, prices = transform_votes2seats_mresidual(votes, self.votetypes,
                                                        self.n_seats, cutoff)
        return seats, prices

    def compute_unused_votes(self, votes, residuals):
        """Compute the votes which are not used to assign seats.

        Parameters
        ----------
        votes: numpy.ndarray
            the votes of the seatable votes.
        residuals: numpy.ndarray
            the residuals fractions.

        Returns
        -------
        rest_votes: numpy.ndarray
            the residual votes not used to pay seats and above the cutoff.

        """
        seatable_votes = votes[self.votetypes['seatable']].as_matrix()
        rest_votes = (seatable_votes * residuals).astype(int)
        return rest_votes


def mresidual_method(votes, n_seats, cutoff=0):
    """Proportional assignation using major residual assignation.

    Parameters
    ----------
    votes: numpy.ndarray
        the votes of the computable votes.
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

    ## 0. Compute needed variables
    n_total_votes = votes.sum()
    abs_cutoff = cutoff*n_total_votes
    ## 1. Filter computable votes
    computable_votes = np.zeros(votes.shape)
    computable_votes[votes >= abs_cutoff] = votes[votes >= abs_cutoff]
    ## 2. Direct assignation seats
    n_comp_votes = computable_votes.sum()
    ratio = computable_votes/n_comp_votes
    seats = np.floor(ratio*n_seats)
    residuals = ratio*n_seats-seats

    ## 3. Assignation of the residual seats
    rest = int(n_seats-np.sum(seats))
    idxs = np.argsort(residuals)[:rest]
    residuals[idxs] = 0
    seats[idxs] += 1

    seats = seats.astype(int)

    return seats, residuals


def transform_votes2seats_mresidual(votes, votetypes, n_seats, cutoff):
    """The general method to transform the different circunscriptions votes
    into seats using major residual method.

    Parameters
    ----------
    votes: pandas.DataFrame
        the votes of the computable votes.
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
    n_seats = n_seats.astype(int)
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
    seats = seats.astype(int)

    return seats, residuals
