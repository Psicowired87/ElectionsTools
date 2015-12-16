
"""
Spain
-----

"""

import pandas as pd
import numpy as np


def read_csv_org(file_0):
    organization = {}
    f = open(file_0, 'w')
    for line in f:
        line_0 = line.split(';')
        organization[line_0[0]] = line_0[1].split(',')
    f.close()
    return organization


def from_regions2superregions(table, vartype, map_):

    n, n2 = table.shape[0], len(vartype['code'])
    collapsed = np.zeros(n, n2)
    for e in map_:
        # Building logi array
        m = len(map_[e])
        logi = np.zeros(n)
        for i in range(m):
            aux_logi = np.array(table[vartype['code'] == map_[e][i])
            logi = np.logical_or(logi, aux_logi)
        # Building the 
        suma = np.sum(table[vartype['votes']].as_matrix()[logi, :], axis=0)
        collapsed[vartype['code'].index(e), :] = suma
    return collapsed, map_.keys(), vartype['code']

