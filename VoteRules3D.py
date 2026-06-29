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
            x_voters = random.normal(30, 18,n)
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
        data.append(temp_list)
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
            if random.randint(0,2) == 0: 
                last_index = (m + 1) - random.randint(0, m-1) #randomize how many candidates will be removed 
            temp_list = row[:last_index] 
            new_data.append(temp_list)
    
    return new_data, header
            
def gen_altered(data,header): 
    with open(r'C:\Users\sagbo\Desktop\summer2026\mainresearch\altered_ballots.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)  
        
def main():
    candidate_num = 5
    voter_num = 1000
    test = VoteResult3D(voter_num, candidate_num, "2D", "normal") #this is num of voters, candidate, dimension, distribution
    gen_file(test.ballots,candidate_num,voter_num) 
    data, header = remove_randoms('sim_ballots.csv',candidate_num)
    gen_altered(data,header)
            
if __name__ == "__main__":  
    main()
    