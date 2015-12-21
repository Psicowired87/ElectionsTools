
"""
"""


import numpy as np
import pandas as pd


def parse_data_elecciones_esp(votation_file):
    #Headers as rows for now
    df = pd.read_excel(votation_file, 0)

    ## circunscripcion
    circunscripcion = df.loc[:, :14]
    circunscripcion = pd.DataFrame(circunscripcion.loc[1:, :].as_matrix(), columns = circunscripcion.loc[0, :])

    # Votes
    data = df.loc[:, 14:].as_matrix()[1:, 1:]

    m_circs = data.shape[0]
    n_parties = data.shape[1]/2
    parties_b = df.loc[:, 14:].columns[1:]
    parties = []
    votes, diputes = np.zeros((m_circs, n_parties)), np.zeros((m_circs, n_parties))
    for i in range(n_parties):
        votes[:, i] = data[:, 2*i]
        diputes[:, i] = data[:, 2*i+1]
        parties.append(parties_b[2*i])

    votes, diputes = votes.astype(int), diputes.astype(int)

    return circunscripcion, parties, votes, diputes


def collapse_by_col(circunscripcion, votes, diputes, icol):

    if icol is None:
        l_n = ["Spain", 0, "Spain"]
        l = [l_n + list(circunscripcion.iloc[:, 3:].sum(0).astype(int))]
        new_circunscripcion = pd.DataFrame(l, columns=circunscripcion.columns)
        vts = votes.sum(0)
        dips = diputes.sum(0)
        return new_circunscripcion, vts, dips 

    new_circuns = list(circunscripcion.iloc[:, icol].unique())
    cs, m_circ, n_parties = [], len(new_circuns), votes.shape[1]
    vts, dips = np.zeros((m_circ, n_parties)), np.zeros((m_circ, n_parties))
    for nc in new_circuns:
        logi = np.array(circunscripcion.iloc[:, icol] == nc)
        l_n = [nc, new_circuns.index(nc), nc]
        l = l_n + list(circunscripcion.iloc[logi, 3:].sum(0).astype(int))
        cs.append(l)
        vts[new_circuns.index(nc), :] = votes[logi, :].sum(0)
        dips[new_circuns.index(nc), :] = diputes[logi, :].sum(0)
        
    new_circunscripcion = pd.DataFrame(cs, columns=circunscripcion.columns)
    vts, dips = vts.astype(int), dips.astype(int)

    return new_circunscripcion, vts, dips

    





