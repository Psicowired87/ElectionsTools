
"""
First-past-the-post
-------------------
A method of assignament in which the winner takes all.
"""

import numpy as np
import pandas as pd
from seats_assignation import Seat_assignator, prepare_votetypes


class FPTP_assignation(Seat_assignator):
    """A winner takes all the seats.
    """

    def __init__(self, n_seats=1, votetypes={}, cutoff=0):
        "Initialization of the parameters of the specific assignation."
        self.votetypes, self.n_seats = votetypes, n_seats
        self.cutoff = cutoff

    def assignation(self, votes, pandas_out=True):
        """Major residual assignation.

        Parameters
        ----------
        votes: numpy.ndarray
            the votes of the seatable votes.

        Returns
        -------
        seats: numpy.ndarray
            the seats assigned to each party.
        prices: float
            the prices payed (in votes) for each seat for each circunscription.

        """
        ## 0. Prepare variable needed
        cutoff = self.cutoff if cutoff == 0 else cutoff
        self.votetypes = prepare_votetypes(votes, self.votetypes)
        ## 1. Compute assignation
        seats, prices = transform_votes2seats_FPTP(votes, self.votetypes,
                                                   self.n_seats)
        if pandas_out:
            ind = votes.index
            prices = pd.DataFrame(prices, index=ind)
            seats = pd.DataFrame(seats, columns=votes.columns, index=ind)

        return seats, prices

    def compute_unused_votes(self, votes, winners, cutoff=0, pandas_out=True):
        """Compute the votes which are not used to assign seats.

        Parameters
        ----------
        votes: numpy.ndarray
            the votes of the seatable votes.
        winners: numpy.ndarray
            the winner parties in each possible region.
        cutoff: numpy.ndarray or float [0, 1)
            the proportion of votes required to get a seat.

        Returns
        -------
        rest_votes: numpy.ndarray
            the residual votes not used to pay seats and above the cutoff.

        """
        mask_cutoff = self.compute_mask_cutoff(votes, cutoff)
        rest_votes = self.compute_seatable_votes(votes)
        rest_votes = rest_votes * mask_cutoff
        rest_votes[np.arange(rest_votes.shape[0]), winners] = 0
        if pandas_out:
            rest_votes = pd.DataFrame(rest_votes, columns=votes.columns,
                                      index=votes.index)
        return rest_votes


def FPTP_assignation_method(votes, n_seats):
    """Assignation of first take all.

    Parameters
    ----------
    votes: numpy.ndarray
        the votes of the computable votes.
    n_seats: int
        the number of the seats to assign.

    Returns
    -------
    seats: numpy.ndarray
        the seats assigned to each party.
    winner: int
        the winner party.

    """
    seats = np.zeros(votes.shape[0]).astype(int)
    winner = np.argsort(votes)[-1]
    seats[winner] = n_seats
    seats = seats.astype(int)

    return seats, winner


def transform_votes2seats_FPTP(votes, votetypes, n_seats):
    """Method for assignation of seats using FPTP.

    Parameters
    ----------
    votes: numpy.ndarray
        the votes of the seatable votes.
    votetypes: dict
        the information of the different types of vote variables.
    n_seats: int
        the number of the seats to assign.

    Returns
    -------
    rest_votes: numpy.ndarray
        the residual votes not used to pay seats and above the cutoff.


    """
    ## 0. Compute needed variables
    seatable_votes = votes[votetypes['seatable']]
    n, m_v = seatable_votes.shape
    n_seats = np.ones(n)*n_seats if type(n_seats) == int else n_seats
    n_seats = n_seats.astype(int)

    ## 1. Assignation
    winners = np.argsort(seatable_votes, axis=1)[:, -1]
    idxs = np.arange(n)
    seats = np.zeros((n, m_v)).astype(int)
    seats[idxs, winners] = n_seats
    seats = seats.astype(int)

    return seats, winners
