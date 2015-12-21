
"""
Collapser
---------
Module with utilities to collapse joining circunscriptions and parties.

"""

import numpy as np
import pandas as pd
from itertools import product


class Collapser():

    def __init__(self, party_collapser={}, circ_collapser={}):
        self.collapser_p = party_collapser
        self.collapser_c = circ_collapser

    def collapse(self, votation_data, pandas_out=True):
        parties = list(votation_data.columns)
        circs = list(votation_data.index)
        matrix = votation_data.as_matrix()
        if self.collapser_p:
            matrix = collapsing_parties(matrix, parties, self.collapser_p)
            parties = list(self.collapser_p.keys())
        if self.collapser_c:
            matrix = collapsing_circ(matrix, circs, self.collapser_c)
            circs = list(self.collapser_c.keys())
        if pandas_out:
            matrix = pd.DataFrame(matrix, columns=parties, index=circs)
        return matrix

    def collapse_bunch(self, votation_datas, pandas_out=True):
        matrices = []
        for d in votation_datas:
            matrices.append(self.collapse(d, pandas_out))
        return matrices

    def collapse_columns(self, votation_data, pandas_out=True):
        parties = list(votation_data.columns)
        circs = list(votation_data.index)
        matrix = votation_data.as_matrix()
        if self.collapser_p:
            matrix = collapsing_parties(matrix, parties, self.collapser_p)
            parties = list(self.collapser_p.keys())
        if pandas_out:
            matrix = pd.DataFrame(matrix, columns=parties, index=circs)
        return matrix

    def collapse_rows(self, votation_data, pandas_out=True):
        parties = list(votation_data.columns)
        circs = list(votation_data.index)
        matrix = votation_data.as_matrix()
        if self.collapser_c:
            matrix = collapsing_circ(matrix, circs, self.collapser_c)
            circs = list(self.collapser_c.keys())
        if pandas_out:
            matrix = pd.DataFrame(matrix, columns=parties, index=circs)
        return matrix


def collapsing_parties(matrix, party, collapsing_info):
    n_parties = len(collapsing_info.keys())
    new_matrix = np.zeros((matrix.shape[0], n_parties)).astype(int)
    for i in range(n_parties):
        aux = collapsing_info.keys()[i]
        ns = len(collapsing_info[aux])
        idxs = [party.index(collapsing_info[aux][j]) for j in range(ns)]
        new_matrix[:, i] = np.sum(matrix[:, idxs], axis=1)
    return new_matrix


def collapsing_circ(matrix, circs, collapsing_info):
    n_circ = len(collapsing_info.keys())
    new_matrix = np.zeros((n_circ, matrix.shape[1])).astype(int)
    for i in range(n_circ):
        aux = collapsing_info.keys()[i]
        ns = len(collapsing_info[aux])
        idxs = [circs.index(collapsing_info[aux][j]) for j in range(ns)]
        new_matrix[i, :] = np.sum(matrix[idxs, :], axis=0)
    return new_matrix


def create_collapse_info(lista1, lista2):
    n1, n2, u2 = len(lista1), len(np.unique(lista2)), np.unique(lista2)
    collapse = {}
    for j in range(n2):
        collapse[u2[j]] = [lista1[i] for i in range(n1) if lista2[i] == u2[j]]
    return collapse


def create_bunch_collapsers(party_cols, reg_cols, names=None):
    a, b = range(len(party_cols)), range(len(reg_cols))
    collapsers = []
    names_c = []
    for i, j in product(a, b):
        collapsers.append(Collapser(party_cols[i], reg_cols[j]))
        if names:
            names_c.append('_'.join([names[0][i], names[1][j]]))
        else:
            names_c.append([i, j])
    return collapsers, names_c
