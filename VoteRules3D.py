from numpy import random
import numpy as np
import scipy as sp
import math
import matplotlib.pyplot as plt 
import csv
import pandas as pd
import glob

class SVoter3D:
    def __init__(self, num, x, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        
        self.id = num
        self.scores = {}

    def setScores(self,scoreDict):
        self.scores = scoreDict

    def __str__(self):
        return "Voter "+str(self.id)

class SCandidate3D:
    def __init__(self, num, x, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.id = num

    def __str__(self):
        return "Candidate "+str(self.id)
    
class VoteResult3D:
    def __init__(self, n, m, dimension, distribution):
        self.voters = []      #size of voters is n
        self.candidates = []  #size of candidates is m
        self.distribution = distribution
        self.dimension = dimension

        #generate random coordinates of voters and candidates for different distributions
        if self.distribution == "normal":
            x_voters = random.normal(30, 20,n)
            x_candidates = random.normal(30, 18, m)
            y_voters = random.normal(30, 18,n)
            y_candidates = random.normal(30, 18, m)
            z_voters = random.normal(30, 18,n)
            z_candidates = random.normal(30, 18, m)
            
            
        elif self.distribution == "poisson":
            x_voters = random.poisson(30, n)
            x_candidates = random.poisson(30, m)
            y_voters = random.poisson(30, n)
            y_candidates = random.poisson(30, m)
            z_voters = random.poisson(30, n)
            z_candidates = random.poisson(30, m)
    
        elif self.distribution == "uniform":
            x_voters = random.uniform(0, 100, n)
            x_candidates = random.uniform(0, 100, m)
            y_voters = random.uniform(0, 100, n)
            y_candidates = random.uniform(0, 100, m)
            z_voters = random.uniform(0, 100, n)
            z_candidates = random.uniform(0, 100, m)
            

        elif self.distribution == "bimodal":
            x_voters1 = random.normal(30, 10, n//2)
            x_voters2 = random.normal(70, 10, n-n//2)
            y_voters1 = random.normal(30,10,n//2)
            y_voters2 = random.normal(70, 10, n-n//2)
            z_voters1 = random.normal(30,10,n//2)
            z_voters2 = random.normal(70, 10, n-n//2)

            x_candidates1 = random.normal(30, 10, m//2)   
            x_candidates2 = random.normal(70, 10, m-m//2)
            y_candidates1 = random.normal(30, 10, m//2)
            y_candidates2 = random.normal(70, 10, m-m//2)
            z_candidates1 = random.normal(30, 10, m//2)
            z_candidates2 = random.normal(70, 10, m-m//2)

            x_voters = np.concatenate((x_voters1, x_voters2), axis=None)
            y_voters = np.concatenate((y_voters1, y_voters2), axis=None)
            z_voters = np.concatenate((z_voters1, z_voters2), axis=None)

            x_candidates = np.concatenate((x_candidates1, x_candidates2), axis = None)
            y_candidates = np.concatenate((y_candidates1, y_candidates2), axis = None)
            z_candidates = np.concatenate((z_candidates1, z_candidates2), axis = None)

        #generate voters and candidates based on the coordinates
        for i in range(n):
            voter = None
            if self.dimension == "1D":
                voter = SVoter3D(i, x_voters[i])
            elif self.dimension == "2D":
                voter = SVoter3D(i, x_voters[i], y_voters[i])
            elif self.dimension == "3D":
                voter = SVoter3D(i, x_voters[i], y_voters[i], z_voters[i])
            
            self.voters.append(voter)

        for i in range(m):
            candidate = None
            if self.dimension == "1D":
                candidate = SCandidate3D(i, x_candidates[i])
            elif self.dimension == "2D":
                candidate = SCandidate3D(i, x_candidates[i], y_candidates[i])
            elif self.dimension == "3D":
                candidate = SCandidate3D(i, x_candidates[i], y_candidates[i], z_candidates[i])
            
            self.candidates.append(candidate)


        self.minDistance = float('inf')
        self.OPTcandidate = self.candidates[0]
        for candidate in self.candidates:
            sumDistance = 0
            for voter in self.voters:
                distance = math.sqrt((voter.x - candidate.x) ** 2 + (voter.y - candidate.y) ** 2 + (voter.z - candidate.z) ** 2)
                sumDistance += distance
            if sumDistance < self.minDistance:
                self.minDistance = sumDistance
                self.OPTcandidate = candidate

        #get preference profile of each voter given a set of candidates
        self.ballots = []
        for voter in self.voters:
            distances = {}
            for candidate in self.candidates:
                distance = math.sqrt((voter.x - candidate.x) ** 2 + (voter.y - candidate.y) ** 2 + (voter.z - candidate.z) ** 2)
                distances[candidate] = distance         
            sorted_dict = sorted(distances, key = distances.get)
            self.ballots.append(sorted_dict)
            
    def distortion(self,candidate): #Krishh distortion code
        if not candidate:
            return False
            
        sumDistance = 0 
        for voter in self.voters:
            distance = math.sqrt((voter.x - candidate.x) ** 2 + (voter.y - candidate.y) ** 2 + (voter.z - candidate.z)**2)
            sumDistance += distance

        
        distortion = sumDistance / self.minDistance
        return distortion

        
def gen_file(ballots,num,voter_count): 
    #here num signifies how many candidate columns this should generate, voter count is number of voters
    header = ["ballot_id"]
    rank = 1
    while rank < num + 1: 
        header.append(rank)
        rank += 1
    data = []
    vc = 0
    while vc < voter_count: 
        temp_list = [vc]
        for c in ballots[vc]: 
            temp_list.append(c.id)
        data.append(temp_list[:num+1])
        vc += 1
    
    with open(r'C:\Users\sagbo\Desktop\summer2026\mainresearch\sim_ballots.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data) 
    
def remove_randoms(file,m): 
    #here m is the number of candidates 
    new_data = []
    with open(file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader) #skipping header
        
        for row in reader:
            temp_list = []
            last_index = m + 1
            chance = random.random()
            if chance >= 0: #where we alter percent complete ##comment this part out for 100% trials (SO > .6 MEANS 60% fully complete)
                #print(chance)
                last_index = (m) - random.randint(0, m-1) #randomize how many candidates will be removed''' 
            temp_list = row[:last_index] 
            new_data.append(temp_list)
    
    return new_data, header
            
def gen_altered(data,header): 
    with open(r'C:\Users\sagbo\Desktop\summer2026\mainresearch\altered_ballots.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)  

def simulate_copeland(ballots,candidates): 
    from itertools import combinations
    cand_index = {c: i for i, c in enumerate(candidates)}
    n = len(candidates)
    matrix = np.zeros((n, n))
    
    for ballot, weight in ballots:
        ranked = [c for c in ballot if c in cand_index]
        
        # Ranked candidates vs each other: order on the ballot determines the win
        for c1, c2 in combinations(ranked, 2):
            matrix[cand_index[c1]][cand_index[c2]] += weight
    
    scores = {c: 0 for c in candidates}
    for c1, c2 in combinations(candidates, 2):
        i, j = cand_index[c1], cand_index[c2]
        if matrix[i][j] > matrix[j][i]:
            scores[c1] += 1
            scores[c2] -= 1
        elif matrix[j][i] > matrix[i][j]:
            scores[c2] += 1
            scores[c1] -= 1
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_scores[0][0]
    #print(f"\nCopeland Winner: {winner}")
    return winner

def simulate_actual_plurality_veto(ballots, candidates):
    cand_set = set(candidates)

    scores = {c: 0 for c in candidates}
    expanded_voters = []
    

    for ballot, weight in ballots:
        ranked = [c for c in ballot if c in cand_set]
        scores[ranked[0]] += weight
        for _ in range(weight):
            expanded_voters.append(ranked)
    random.shuffle(expanded_voters)
        

    standing = set(candidates)
    elimination_order = []
    

    for ranked_ballot in expanded_voters:
        if len(standing) == 1:
            break

        ranked_set = set(ranked_ballot)

        
        for c in reversed(ranked_ballot):
            if c in standing:
                vetoed_this_pass = {c}
                break

        for vetoed in vetoed_this_pass:
            scores[vetoed] -= 1
            if scores[vetoed] <= 0 and vetoed in standing:
                standing.remove(vetoed)
                elimination_order.append(vetoed)

    if standing:
        winner = list(standing)[0]
    else:
        winner = elimination_order[-1]
    #print(f"Elimination order: {elimination_order}")
    #print(f"Plurality Veto Winner: {winner}")
    return winner

def plurality(ballots,candidates): 
    scores = {c: 0 for c in candidates}
    for ballot, weight in ballots:
        #print(candidates)
        #print(ballot)
        for c in ballot:
            if c in candidates:
                scores[c] += weight
                break
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_scores[0][0]
    #print(f"Plurality Winner: {winner}")
    return winner

def simulate_trunk_copeland_fast(ballots, candidates):
    from itertools import combinations
    cand_index = {c: i for i, c in enumerate(candidates)}
    n = len(candidates)
    matrix = np.zeros((n, n))
        
    for ballot, weight in ballots:
        ranked = [c for c in ballot if c in cand_index]
        unranked = [c for c in candidates if c not in ranked]
            
        # Ranked candidates vs each other: order on the ballot determines the win
        for c1, c2 in combinations(ranked, 2):
            matrix[cand_index[c1]][cand_index[c2]] += weight
            
        # Every ranked candidate beats every unranked candidate
        for c1 in ranked:
            for c2 in unranked:
                matrix[cand_index[c1]][cand_index[c2]] += weight
            
        # Unranked vs unranked: no preference was expressed, so skip (tie)
        
    scores = {c: 0 for c in candidates}
    for c1, c2 in combinations(candidates, 2):
        i, j = cand_index[c1], cand_index[c2]
        if matrix[i][j] > matrix[j][i]:
            scores[c1] += 1
            scores[c2] -= 1
        elif matrix[j][i] > matrix[i][j]:
            scores[c2] += 1
            scores[c1] -= 1
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    #for candidate, score in sorted_scores:
    #    print(f"  {candidate}: {score}")
    winner = sorted_scores[0][0]
    #print(f"\nCopeland Truncated Winner: {winner}")
    return winner

def simulate_equal_plurality_veto(ballots, candidates): 
    cand_set = set(candidates)

    scores = {c: 0 for c in candidates}
    expanded_voters = []

    for ballot, weight in ballots:
        ranked = [c for c in ballot if c in cand_set]
        if ranked:
            scores[ranked[0]] += weight
            for _ in range(weight):
                expanded_voters.append(ranked)

    standing = set(candidates)
    elimination_order = []

    for ranked_ballot in expanded_voters:
        if len(standing) == 1:
            break

        ranked_set = set(ranked_ballot)
        # Every standing candidate this voter left off their ballot is treated as equally "last" and gets vetoed simultaneously.
        unranked_standing = standing - ranked_set

        vetoed_this_pass = set(unranked_standing)

        if not unranked_standing:
            for c in reversed(ranked_ballot):
                if c in standing:
                    vetoed_this_pass = {c}
                    break

        for vetoed in vetoed_this_pass:
            scores[vetoed] -= 1
            if scores[vetoed] <= 0 and vetoed in standing:
                standing.remove(vetoed)
                elimination_order.append(vetoed)

    if standing:
        winner = list(standing)[0]
    else:
        winner = elimination_order[-1]
    #print(f"Plurality Veto Eq Winner: {winner}")
    return winner

def simulate_stat_plurality_veto(ballots, candidates, last_place_counts):
    
    cand_set = set(candidates)

    scores = {c: 0 for c in candidates}
    expanded_voters = []

    for ballot, weight in ballots:
        ranked = [c for c in ballot if c in cand_set]
        if ranked:
            scores[ranked[0]] += weight
            for _ in range(weight):
                expanded_voters.append(ranked)

    # Derive the denominator from the counts themselves 
    # total last-place appearances across all candidates = total complete-ballot weight
    total_last_place = sum(last_place_counts.get(c, 0) for c in candidates)

    if total_last_place > 0:
        last_place_pct = {
            c: last_place_counts.get(c, 0) / total_last_place
            for c in candidates
        }
    else:
        last_place_pct = {c: 0.0 for c in candidates}

    standing = set(candidates)
    elimination_order = []

    for ranked_ballot in expanded_voters:
        if len(standing) == 1:
            break

        ranked_set = set(ranked_ballot)
        unranked_standing = standing - ranked_set

        vetoed_this_pass = set(unranked_standing)

        if not unranked_standing:
            for c in reversed(ranked_ballot):
                if c in standing:
                    vetoed_this_pass = {c}
                    break

        newly_eliminated = []
        for vetoed in vetoed_this_pass:
            scores[vetoed] -= 1
            if scores[vetoed] <= 0 and vetoed in standing:
                newly_eliminated.append(vetoed)

        newly_eliminated.sort(key=lambda c: (-last_place_pct[c], c))

        for c in newly_eliminated:
            if c in standing:
                standing.remove(c)
                elimination_order.append(c)

    if standing:
        winner = list(standing)[0]
    else:
        winner = elimination_order[-1]
    #print(f"Plurality Veto Stat Winner: {winner}")
    return winner

def count_votes(ballots, candidates):
    """
    Count the votes for the current round using weighted ballots.
    Each ballot contributes its weight to the vote of the highest-ranked candidate
    that hasn't been eliminated.
    """
    vote_counts = {candidate: 0 for candidate in candidates}
    for ballot, weight in ballots:
        for candidate in ballot:
            if candidate in candidates:
                vote_counts[candidate] += weight
                break  # Only count the top remaining candidate.
    return vote_counts

def STV(ballots, candidates): 
    round_num = 1
    while True:
        # Tally the weighted votes for this round.
        vote_counts = count_votes(ballots, candidates)
        total_votes = sum(vote_counts.values())
        #print(f"Round {round_num} vote counts: {vote_counts} (Total active votes: {total_votes})")

        # Check if any candidate has a majority (>50% of active votes)
        for candidate, count in vote_counts.items():
            if count > total_votes / 2:
                #print(f"\nWinner: {candidate} with {count} votes (majority of {total_votes} active votes)!")
                winner = candidate
                return winner
        else:
            # No candidate has a majority; eliminate candidate(s) with the fewest votes.
            min_votes = min(vote_counts.values())
            eliminated = [candidate for candidate, count in vote_counts.items() if count == min_votes]
            #print(f"Eliminated in round {round_num}: {eliminated}\n")
            # Remove the eliminated candidate(s) from further consideration.
            for candidate in eliminated:
                candidates.remove(candidate)
            
            # If no candidates remain or all remaining are tied, declare a tie.
            if not candidates:
                return eliminated[-1]
            elif len(vote_counts) == len(eliminated):
                print("Election resulted in a tie among the remaining candidates:")
                print(vote_counts)
                return random.choice(candidates) #returns a random from the remaining candidates

            round_num += 1
            continue
        break
    
def full_ballot_sim(full_ballot): 
    df = pd.read_csv(full_ballot)
    ballots = [(list(row[1:]), 1) for row in df.values.tolist()]
    from itertools import combinations
    candidates = set()
    for ballot, weight in ballots:
        for candidate in ballot:
            candidates.add(candidate)
    candidates = list(candidates)
    
    copeland_winner = simulate_copeland(ballots, candidates)
    plurality_veto_winner = simulate_actual_plurality_veto(ballots, candidates)
    PL_winner = plurality(ballots,candidates)
    STV_winner = STV(ballots,candidates) #this is actually removing things from global variable
    return copeland_winner, plurality_veto_winner, STV_winner, PL_winner

def clean_ballot(row):
    ranked = []
    for c in row:
        if pd.isna(c):
            break
        ranked.append(int(c))
    return ranked

def trunk_ballot_sim(trunk_ballots): 
    from itertools import combinations
    
    last_place_counts = {
    0 : 20,
    1 : 0,
    2 : 8,
    3 : 0,
    4 : 0
    }  
    
    df = pd.read_csv(trunk_ballots)
    rank_cols = ['1', '2', '3', '4','5'] #this needs to be manually updated
    df_clean = df[df[rank_cols].notna().any(axis=1)] 
    ballots = [(clean_ballot(row), 1) for row in df_clean[rank_cols].values.tolist()]
    
    candidates = set()
    for ballot, weight in ballots:
        for candidate in ballot:
            candidates.add(candidate)
    candidates = list(candidates)
    
    copeland_trunk = simulate_trunk_copeland_fast(ballots,candidates)
    pl_eq_veto_trunk = simulate_equal_plurality_veto(ballots, candidates)
    pl_st_veto_trunk = simulate_stat_plurality_veto(ballots,candidates,last_place_counts)
    PL_winner = plurality(ballots,candidates)
    T_STV_winner = STV(ballots,candidates)
    return copeland_trunk,pl_eq_veto_trunk, pl_st_veto_trunk, T_STV_winner, PL_winner

def is_same(ideal,result): 
    if int(ideal) == int(result):
        return 1
    else: 
        return 0

def max_dist(ls,winner,test):
    win_dist = test.distortion(test.candidates[winner])
    if win_dist > ls[0]:
        ls[0] = win_dist
    return ls
    
def super_sim(c_num,v_num,trials):
    '''n_cope_ls = []
    n_pl_veto_ls = []
    n_STV_ls = []'''
    n_PL_ls = [0] #initalized to 0 for this max_dist 
    t_cope_ls = [0]
    t_pl_eq_veto_ls = [0]
    t_pl_st_veto_ls = [0]
    t_STV_ls = [0]
    
    for i in range(0,trials):
        test = VoteResult3D(v_num, c_num, "2D", "normal") #this is num of voters, candidate, dimension, distribution
        ideal = str(test.OPTcandidate)[10:] #making the ideal candidate object into a int
        gen_file(test.ballots,5,v_num) #here the 2nd number is how many candidates are being ranked
        data, header = remove_randoms('sim_ballots.csv',c_num)
        gen_altered(data,header)
        
        #cope, pl_v,STVn,PLn = full_ballot_sim('sim_ballots.csv')
        tcope, t_pl_eq, t_pl_st,stvt,plt = trunk_ballot_sim('altered_ballots.csv')
        
        #print(ideal,cope,pl_v,STVn,tcope,t_pl_eq,t_pl_st,stvt)
        n_PL_ls = max_dist(n_PL_ls,plt,test)
        t_cope_ls = max_dist(t_cope_ls,tcope,test)
        t_pl_eq_veto_ls = max_dist(t_pl_eq_veto_ls,t_pl_eq,test)
        t_pl_st_veto_ls = max_dist(t_pl_st_veto_ls,t_pl_st,test)
        t_STV_ls =  max_dist(t_STV_ls,stvt,test)


    print("Max Dist  N PL : ", n_PL_ls[0])
    print("Max Dist  T Cope : ", t_cope_ls[0])
    print("Max Dist  T Pl EQ Veto : ", t_pl_eq_veto_ls[0])
    print("Max Dist  T Pl ST Veto : ", t_pl_st_veto_ls[0])
    print("Max Dist  T STV : ",  t_STV_ls[0])
    
def main():
    #if changing the cand num need to change 578,550,514
    candidate_num = 13
    voter_num = 1000
    trials = 1000
    super_sim(candidate_num,voter_num,trials)

    
            
if __name__ == "__main__":  
    main()
    