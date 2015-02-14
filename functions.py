
"""
"""


import pandas as pd
import numpy as np


def hondt_method(votes, n_seats, cutoff=0):
    """
    """

    n_total_votes = votes.sum()
    abs_cutoff = cutoff*n_total_votes

    computable_votes = np.zeros(votes.shape)
    computable_votes[votes >= abs_cutoff] = votes[votes >= abs_cutoff]

    seats = np.zeros(votes.shape)

    for i in range(n_seats):
        s = np.argmax(computable_votes/(seats + 1))
        seats[s] += 1

    seats = seats.astype(int)

    return seats
