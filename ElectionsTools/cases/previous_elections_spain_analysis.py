
import numpy as np
import pandas as pd
from ElectionsTools.Seats_assignation import DHondt_assignation
from previous_elections_spain_parser import *
import os

pathfiles = '../data/spain_previous_elections_results/provincia/'
pathfiles = '/'.join(os.path.realpath(__file__).split('/')[:-1]+[pathfiles])

fles = [pathfiles+'PROV_02_197706_1.xlsx',
        pathfiles+'PROV_02_197903_1.xlsx',
        pathfiles+'PROV_02_198210_1.xlsx',
        pathfiles+'PROV_02_198606_1.xlsx',
        pathfiles+'PROV_02_198910_1.xlsx',
        pathfiles+'PROV_02_199306_1.xlsx',
        pathfiles+'PROV_02_199603_1.xlsx',
        pathfiles+'PROV_02_200003_1.xlsx',
        pathfiles+'PROV_02_200403_1.xlsx',
        pathfiles+'PROV_02_200803_1.xlsx',
        pathfiles+'PROV_02_201111_1.xlsx']
years = [1977, 1979, 1982, 1986, 1989, 1993, 1996, 2000, 2004, 2008, 2011]


def compute_diputes_DHont(filename):
    ## 1. Parse
    circ, parties, votes, diputes = parse_data_elecciones_esp(filename)
    circ_com, votes_com, dips_com = collapse_by_col(circ, votes, diputes, 0)
    circ_sp, votes_sp, dips_sp = collapse_by_col(circ, votes, diputes, None)
    votes_sp = votes_sp.reshape(1,len(parties))
    
    ## 2. Assignation objects
    assign = DHondt_assignation(diputes.sum(1))
    assign1 = DHondt_assignation(dips_com.sum(1))
    assign2 = DHondt_assignation(np.array([dips_sp.sum(0)]))

    ## 3. Compute assignations
    d, price = assign.assignation(pd.DataFrame(votes, columns=parties))
    d1, price1 = assign1.assignation(pd.DataFrame(votes_com, columns=parties))
    d2, price2 = assign2.assignation(pd.DataFrame(votes_sp, columns=parties))

    return d, d1, d2, parties


def prepare2export(d, d1, d2, parties):
    logi = np.logical_or(np.logical_or(d.sum(0)>0, d1.sum(0)>0), d2.sum(0)>0)
    parties = [parties[i] for i in np.where(logi)[0]]
    d, d1, d2 = d[:, logi].sum(0), d1[:, logi].sum(0), d2[:, logi].sum(0)
    return d, d1, d2, parties

def compute_all_year(year):
    filename = fles[years.index(year)]
    d, d1, d2, parties = compute_diputes_DHont(filename)
    exp_d, exp_d1, exp_d2, exp_parties = prepare2export(d, d1, d2, parties)
    return exp_d, exp_d1, exp_d2, exp_parties
    

def compute_table_all_years(year):
    d1, d2, d3, cols = compute_all_year(year)
    d1, d2, d3 = pd.DataFrame(d1), pd.DataFrame(d2), pd.DataFrame(d3)
    ind = ['Dhont_estado', 'Dhont_comunidad', 'Dhont_provincia']
    exp = pd.concat([d1.T, d2.T, d3.T], axis=0)
    exp.columns = cols
    exp.index = ind
    return exp

    
