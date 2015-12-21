
"""
Utilities para parsear resultados de las elecciones generales 2015 en espana.

"""

import urllib2
import simplejson
import numpy as np
import pandas as pd

from pythonUtils.CodingText import *


#"http://resultadosgenerales2015.interior.es/congreso/results/ES201512-CON-ES/ES/CA09/08/info.json"
urlreq = "http://resultadosgenerales2015.interior.es/congreso/results/ES201512-CON-ES/ES/%sinfo.json"
urlreg = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/%s.json"
urlca = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/comunidad.json"
urlprov = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/provincia.json"
urlmuni = "http://resultadosgenerales2015.interior.es/congreso/config/ES201512-CON-ES/municipio.json"
urlweb = "http://resultadosgenerales2015.interior.es/congreso/results/ES201512-CON-ES/ES/"


def parse_json(urljson):
    "Fetch and parse a json file from internet."
    req = urllib2.Request(urljson)
    opener = urllib2.build_opener()
    f = opener.open(req)
    a = simplejson.load(f)
    return a


def create_regions_urls(regions_data, region_lvl):
    """Create regions urls to query for the results.
    """
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
    "Get the parties info of one region from results data."
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
    "Obtain the region info."
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


def get_pre_level(region_level):
    "Obtain the previous region level."
    urlregion = urlreg % region_level
    regions_data = parse_json(urlregion)
    regions_names = get_region_names(regions_data)
    if region_level == 'provincia':
        region_prelevel = 'comunidad'
    elif region_level == 'comunidad':
        region_prelevel = 'estado'
        pre_names = ['ES' for i in range(len(regions_names))]
        return regions_names, pre_names
    urlpreregion = urlreg % region_prelevel
    preregions_data = parse_json(urlpreregion)
    preregions_id = []
    for i in range(len(regions_data)):
        preregions_id.append(regions_data[i][2])
    preregion_codes = [e[0] for e in preregions_data]
    preregion_names = [e[1] for e in preregions_data]
    pre_names = [preregion_names[preregion_codes.index(e)] for e in preregions_id]
    return regions_names, pre_names


def get_region_codes(regions_data):
    "Get the list of the regions codes."
    regions_id = []
    for i in range(len(regions_data)):
        regions_id.append(regions_data[i][0])
    return regions_id


def get_region_names(regions_data):
    "Get the list of the regions names."
    regions_names = []
    for i in range(len(regions_data)):
        regions_names.append(regions_data[i][1])
    return regions_names


def get_extra_data(data):
    "Get extra data."
    data_i = data['results']
    aux = [data_i['census'], data_i['abstention'], data_i['blank'], data_i['null']]
    extras_i = np.array(aux)
    return extras_i


def csv_builder(region_lvl, folder=None, opt=None):
    """csv builder.

    Parameters
    ----------
    region_lvl: str optional ['provincia', 'comunidad', 'estado']
        the region level we want to explore.
    folder: str or None
        the folder in which we want to save the file.
    opt: optional
        flag to get the previous region.

    Returns
    -------
    extras: pandas.DataFrame
        the extra information about the region, the census and the nonseatable
        vote.
    votes: pandas.DataFrame
        the votes obtained for each party.
    seats: pandas.DataFrame
        the seats obtained for each party.

    """
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
    cols, rows = encode_list(party_acronyms), encode_list(regions_names)
    rep = {';': ','}
    cols, rows = change_char_list(cols, rep), change_char_list(rows, rep)

    votes = pd.DataFrame(votes, columns=cols, index=rows)
    seats = pd.DataFrame(seats, columns=cols, index=rows)
    cols = ['abstencion', 'blancos', 'nulos']
    extras = pd.DataFrame(extras[:, 1:], columns=cols, index=rows)
    if folder is not None:
        extras.to_csv(folder+"extras_"+region_lvl+'.csv', sep=';')
        votes.to_csv(folder+"votes_"+region_lvl+'.csv', sep=";")
        seats.to_csv(folder+"seats_"+region_lvl+'.csv', sep=";")
    if opt is not None:
        pre_level = get_pre_level(region_lvl)
        return extras, votes, seats, pre_level
    return extras, votes, seats
