
"""

Example
-------
>>> from ElectionsTools.cases.elections_spain2015_analysis import \
>>>     compute_comparative_dhont, general_results_comparison, aggregate_comparison
>>> res, names_c, names_a = compute_comparative_dhont()
>>> g_results, g_names = general_results_comparison(res, names_c, names_a)
>>> res_table = aggregate_comparison(g_results)
>>> res_table.index = g_names
>>> res_table.to_csv('/home/antonio/code/CooperativeGames/res_table.csv', sep=';')
"""



import numpy as np
import pandas as pd
from ElectionsTools.Seats_assignation import DHondt_assignation, create_bunch_assignators
from ElectionsTools.Preprocess_votes import Collapser, create_collapse_info,\
    create_bunch_collapsers
from pythonUtils.CodingText import encode_dictlist, encode_list

from build_csv_congress_2015 import *
from data import *


def compute_diputes_list(votations, collapsers, assignators, seats, extras):
    """

    """
    results = []
    for c in collapsers:
        results_c = []
        votations_c, seats_c = c.collapse_bunch([votations, seats])
        extras_c = c.collapse_rows(extras)
        votes_res = pd.concat([extras_c, votations_c], axis=1)
        for a in assignators:
            a = a[0](seats_c.sum(1), **a[1])
            res = a.assignation(votes_res)
            results_c.append(res)
        results.append(results_c)
    return results


def compute_comparative_dhont():
    """
    """
    extras, votes, seats, pre_level = csv_builder('provincia', None, True)
    parties = list(votes.columns)
    circ = encode_list(list(votes.index))
    collapse_info1 = encode_dictlist(create_collapse_info(*pre_level))

    # Creation collapsers
    collapses_p = [grup_fus_prov, cand_fus_prov]
    collapses_c = [{}, collapse_info1, {'ES': circ}]
    names_collapsers = [['GruposParlamentarios', 'Candidaturas']]
    names_collapsers.append(['Provincia', 'CA', 'ES'])

    collapsers, names_c = create_bunch_collapsers(collapses_p, collapses_c,
                                                  names_collapsers)
    assign_class, assign_pars = [DHondt_assignation], [{'cutoff': 0.0}, {'cutoff': 0.03}]
    names_a = [['hondt'], ['cutoff0', 'cutoff003']]
    assignators, names_a = create_bunch_assignators(assign_class, assign_pars,
                                                    names_a)
    res = compute_diputes_list(votes, collapsers, assignators, seats, extras)
    return res, names_c, names_a


def general_results_comparison(res, names_c, names_a):
    """
    """
    prices, g_results, g_names = [], [], []
    for i in range(len(res)):
        for j in range(len(res[i])):
            aux, name = res[i][j][0].sum(0), '-'.join([names_c[i], names_a[j]])
            g_results.append(pd.DataFrame(aux))
            prices.append(res[i][j][1])
            g_names.append(name)
    return g_results, g_names


def aggregate_comparison(g_results, iffilter=True):
    """
    """
    res_table = pd.concat(g_results, axis=1).T
    res_table.index = range(res_table.shape[0])

    if iffilter:
        n_tab = len(g_results)
        res_matrix = res_table.as_matrix()
        logi = np.zeros(res_table.shape[1]).astype(bool)
        for i in range(n_tab):
            logi = np.logical_or(logi, res_matrix[i, :])
        res_table = res_table.iloc[:, logi]
        res_table = res_table.replace({np.nan: '-'})
    return res_table
