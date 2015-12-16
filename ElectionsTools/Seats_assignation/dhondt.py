
"""
DHondt
-----
Assignation of seats using DHondt.

TODO
----
check price
"""

import numpy as np
from seats_assignation import Seat_assignator, recalibrate_cutoff,\
    prepare_votetypes


class DHondt_assignation(Seat_assignator):
    """DHondt assignation of seats from votes.
    """

    def __init__(self, n_seats, votetypes={}):
        "Initialization of the parameters of the specific assignation."
        self.votetypes, self.n_seats = votetypes, n_seats

    def assignation(self, votes, cutoff=0):
        """DHondt assignation.

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
        seats, prices = transform_votes2seats_dhondt(votes, self.votetypes,
                                                     self.n_seats, cutoff)
        return seats, prices

    def compute_unused_votes(self, votes, seats, prices, cutoff=0):
        """Compute the residual votes not used to buy a seat.

        Parameters
        ----------
        votes: numpy.ndarray
            the votes of the seatable votes.
        seats: numpy.ndarray
            the assigned seats to the candidates
        prices: numpy.ndarray
            the prices payed in each circunscription for the seats.
        cutoff: numpy.ndarray or float [0,1)
            the threshold ratio of the total votes in order to get a seat.

        Returns
        -------
        rest_votes: numpy.ndarray
            the residual votes not used to pay seats and above the cutoff.

        """
        seatable_votes = votes[self.votetypes['seatable']].as_matrix()
        rest_votes = compute_residual_dhondt_votes(seatable_votes, seats,
                                                   prices, cutoff)
        return rest_votes


def dhondt_method(votes, n_seats, cutoff=0):
    """DHondt method to assign seats from votes.

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
    price: float
        the price payed (in votes) for each seat.

    """

    n_total_votes = votes.sum()
    abs_cutoff = cutoff*n_total_votes

    computable_votes = np.zeros(votes.shape)
    computable_votes[votes >= abs_cutoff] = votes[votes >= abs_cutoff]

    seats = np.zeros(votes.shape).astype(int)
    for i in range(n_seats):
        s = np.argmax(computable_votes/(seats + 1))
        seats[s] += 1

    price = computable_votes[s]/float(seats[s])
    seats = seats.astype(int)

    return seats, price


def transform_votes2seats_dhondt(votes, votetypes, n_seats, cutoff=0):
    """The general method to transform the different circunscriptions votes
    into seats using DHondt method.

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
    prices: float
        the prices payed (in votes) for each seat for each circunscription.

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

    ## 2. DHondt assignation
    seats, prices = np.zeros((n, m_v)), np.zeros(n)
    for i in range(n):
        seats[i, :], prices[i] = dhondt_method(seatable_votes[i, :],
                                               n_seats[i], cutoff[i])

    seats = seats.astype(int)

    return seats, prices


def compute_residual_dhondt_votes(seatable_votes, seats, prices, cutoff=0):
    """Compute the residual votes not used to buy a seat.

    Parameters
    ----------
    seatable_votes: numpy.ndarray
        the votes which can be transformed to seats.
    seats: numpy.ndarray
        the assigned seats to the candidates
    prices: numpy.ndarray
        the prices payed in each circunscription for the seats.
    cutoff: numpy.ndarray or float [0,1)
        the threshold ratio of the total votes in order to get a seat.

    Returns
    -------
    rest_votes: numpy.ndarray
        the residual votes not used to pay seats and above the cutoff.

    """
    ## 0. Compute excluded by cutoff
    abs_cutoff = np.sum(seatable_votes, axis=1) * cutoff
    logi = np.zeros(seatable_votes.shape)
    for i in range(seatable_votes.shape[1]):
        logi[:, i] = abs_cutoff > seatable_votes[:, i]
    ## 1. Compute votes payed in the Dhondt assignation
    payed_votes = np.zeros(seatable_votes.shape)
    for i in range(seatable_votes.shape[1]):
        payed_votes[:, i] = prices * seats[:, i]
    ## 2. Compute rest votations
    rest_votes = seatable_votes - payed_votes
    ## 3. Filter excluded by cutoff
    rest_votes[logi.astype(bool)] = 0
    rest_votes = rest_votes.astype(int)

    return rest_votes
