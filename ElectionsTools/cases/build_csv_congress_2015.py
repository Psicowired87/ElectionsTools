
"""
Utilities para parsear resultados de las elecciones generales 2015 en espana.

"""

import urllib2
import simplejson
import numpy as np
import pandas as pd


#"http://resultadosgenerales2015.interior.es/congreso/results/ES201512-CON-ES/ES/CA09/08/info.json"
urlreq = "http://resultadosgenerales2015.interior.es/congreso/results/ES201512-CON-ES/ES/%sinfo.json"
urlreg = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/%s.json"
urlca = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/comunidad.json"
urlprov = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/provincia.json"
urlmuni = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/municipio.json"
urlweb = "http://resultadosgenerales2015.interior.es/congreso/results/ES201512-CON-ES/ES/"


def parse_json(urljson):
    req = urllib2.Request(urljson)
    opener = urllib2.build_opener()
    f = opener.open(req)
    a = simplejson.load(f)
    return a


def create_regions_urls(regions_data, region_lvl):
    if region_lvl == 'comunidad':
        regions_nf = [str(regions_data[i][0])+"/" for i in range(len(regions_data))]
        regions_urls = [urlreq % regions_nf[i] for i in range(len(regions_nf))]
    elif region_lvl == 'provincia':
        regions_urls = []
        for i in range(len(regions_data)):
            rf = str(regions_data[i][2])+"/"+str(regions_data[i][0])+"/"
            regions_urls.append(urlreq % rf)
    elif region_lvl == 'municipio':
        prov_data = parse_json(urlprov)
        prov_ids = [prov_data[i][0] for i in range(len(prov_data))]
        regions_urls = []
        for i in range(len(regions_data)):
            if len(regions_data[i][2]) == 3:
                rf = str(regions_data[i][2])+"/"+str(regions_data[i][0][:2])+"/"
                rf = rf+str(regions_data[i][0])+"/"
            else:
                rf = str(regions_data[i][2])+"/"+str(regions_data[i][0])+"/"
            prov_id = regions_data[i][2][:2]
            rf = str(prov_data[prov_ids.index(prov_id)][2])+"/"+rf
            regions_urls.append(urlreq % rf)
    return regions_urls

def get_parties_info(regions_urls=None):
    if regions_urls is None:
        party_info = parse_json(urlweb + "/info.json")['results']['parties']
        party_acronyms = [party_info[i]['acronym'] for i in range(len(party_info))]
        party_ids = [party_info[i]['code'] for i in range(len(party_info))]
        party_names = [party_info[i]['name'] for i in range(len(party_info))]
    else:
        party_names, party_ids, party_acronyms, party_info = [], [], [], []
        for j in range(len(regions_urls)):
            party_info = parse_json(regions_urls[j])['results']['parties']
            parties_ac = [party_info[i]['acronym'] for i in range(len(party_info))]
            for k in range(len(parties_ac)):
                if parties_ac[k] not in party_acronyms:
                    party_acronyms.append(party_info[k]['acronym'])
                    party_ids.append(party_info[k]['code'])
                    party_names.append(party_info[k]['name'])
            
    return party_info, party_acronyms, party_ids, party_names


def get_regions_info(region_lvl):
    if region_lvl in ['', 'nacional', 'estado']:
        urlregion = urlreq % ''
        regions_data = parse_json(urlregion)
        regions_id = ['ES']
        regions_names = ['ESPA\xc3\x91A']
        regions_urls = [urlreq % '']
    else:
        urlregion = urlreg % region_lvl
        regions_data = parse_json(urlregion)
        regions_id = get_region_codes(regions_data)
        regions_names = get_region_names(regions_data)
        regions_urls = create_regions_urls(regions_data, region_lvl)
    return regions_data, regions_id, regions_names, regions_urls


def get_region_codes(regions_data):
    regions_id = []
    for i in range(len(regions_data)):
        regions_id.append(regions_data[i][0])
    return regions_id


def get_region_names(regions_data):
    regions_names = []
    for i in range(len(regions_data)):
        regions_names.append(regions_data[i][1])
    return regions_names


def get_extra_data(data):
    data_i = data['results']
    aux = [data_i['census'], data_i['abstention'], data_i['blank'], data_i['null']]
    extras_i = np.array(aux)
    return extras_i


def collapsing_parties(matrix, party, collapsing_info):
    n_parties = len(collapsing_info.keys())
    new_matrix = np.zeros((matrix.shape[0], n_parties))
    for i in range(n_parties):
        aux = collapsing_info.keys()[i]
        ns = len(aux)
        idxs = [party.index(aux[j]) for j in range(ns)]
        new_matrix[:, i] = np.sum(matrix[:, idxs] , axis=1)
    return new_matrix


def csv_builder(region_lvl, folder):
    regions_data, regions_id, regions_names, regions_urls = get_regions_info(region_lvl)
    party_info, party_acronyms, party_ids, party_names = get_parties_info(regions_urls)
    n_regions, n_parties = len(regions_id), len(party_ids)
    ## matrices
    extras = np.zeros((n_regions, 4)).astype(int)
    votes = np.zeros((n_regions, n_parties)).astype(int)
    seats = np.zeros((n_regions, n_parties)).astype(int)
    for r_i in range(n_regions):
        data = parse_json(regions_urls[r_i])

        extras[r_i, :] = get_extra_data(data)
        for i in range(len(data['results']['parties'])):
            data_i = data['results']['parties'][i]
            p_i = party_acronyms.index(data_i['acronym'])
            votes[r_i, p_i] = data_i['votes']['presential']
            seats[r_i, p_i] = data_i['seats']
    votes = pd.DataFrame(votes, columns=party_acronyms, index=regions_names)
    seats = pd.DataFrame(seats, columns=party_acronyms, index=regions_names)
    cols = ['abstencion', 'blancos', 'nulos']
    extras = pd.DataFrame(extras[:, 1:], columns=cols, index=regions_names)
    #votes.to_csv(folder+"votes_"+region_lvl, sep=";")
    #seats.to_csv(folder+"seats_"+region_lvl, sep=";")
    return extras, votes, seats





