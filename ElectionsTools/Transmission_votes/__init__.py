





def transmission_votes(votes1, votes2):
    n_circ, n_cand = votes1.shape
    trans = np.zeros((n_cand, n_cand, 2))
    for i in xrange(n_circ):
        trans_i = np.zeros((n_cand, n_cand))
        diff = votes2[i, :] - votes1[i, :]
        losers = np.where(diff < 0)[0]
        p_winners = diff[diff > 0] / diff[diff > 0].sum().astype(float)
        for loser in losers:
            p_lose = diff[loser]/float(votes1[i, loser])
            trans_i[loser, diff > 0] += -p_lose*p_winners
            trans_i[loser, loser] += p_lose
        trans[:, :, 0] += votes2.sum(1)[i]*trans_i/votes2.sum().astype(float)
        trans_i = np.zeros((n_cand, n_cand))
        winners = np.where(diff > 0)[0]
        p_losers = diff[diff < 0] / diff[diff < 0].sum().astype(float)
        for winner in winners:
            p_winner = diff[winner]/float(votes2[i, winner])
            trans_i[winner, diff < 0] += -p_winner*p_losers
            trans_i[winner, winner] += p_winner
        trans[:, :, 1] += votes2.sum(1)[i]*trans_i/votes2.sum().astype(float)
        #trans += votes2.sum(1)[i]*trans_i/votes2.sum().astype(float)
    return trans




def transmission_votes(votes1, votes2):
    n_circ, n_cand = votes1.shape
    trans = np.zeros((n_cand, n_cand))
    for i in xrange(n_circ):
        trans_i = np.zeros((n_cand, n_cand))
        diff = votes2[i, :] - votes1[i, :]
        losers = np.where(diff < 0)[0]
        p_winners = diff[diff > 0] / diff[diff > 0].sum().astype(float)
        for loser in losers:
            p_lose = diff[loser]
            trans_i[loser, diff > 0] += -p_lose*p_winners
            trans_i[loser, loser] += p_lose
        #trans[:, :, 0] += votes2.sum(1)[i]*trans_i/votes2.sum().astype(float)
        winners = np.where(diff > 0)[0]
        p_losers = diff[diff < 0] / diff[diff < 0].sum().astype(float)
        for winner in winners:
            p_winner = diff[winner]
            trans_i[winner, diff < 0] += -p_winner*p_losers
            trans_i[winner, winner] += p_winner
        #trans[:, :, 1] += votes2.sum(1)[i]*trans_i/votes2.sum().astype(float)
        #trans += votes2.sum(1)[i]*trans_i/votes2.sum().astype(float)
        trans += trans_i*float(votes2[i, :].sum())
    trans = trans/float(votes2.sum())
    return trans




#
#"""
#mathes: list of jornadas (list of individual matches)
#f_points(match, result): 
#
#"""
#
#f_points = lambda x: [(3, 0), (1, 1), (0, 3)][-int(x)+1]
#f_class = lambda match, classi, res: classi[list(match)] += np.array(f_points(res))
#
#classi = np.zeros(n_teams)
#matches = []
#results = []
#
