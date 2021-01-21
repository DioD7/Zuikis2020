import configurations
import adventure
from data import Data

import random
from abc import abstractmethod
from collections import Counter
from math import inf, exp

#####
#AI solutions for the zuikis to manouver during the adventure.
#####


class Solver:
    """General interface for a solver"""
    def __init__(self, field, data = None, verbose = False, record = False, seed = 0):
        if not field: self.start = configurations.TestFields.getTests()[0]
        else: self.start = field
        if not data: self.data = Data(verbose = True)
        else: self.data = data
        self.verbose = verbose
        self.story = adventure.Story(self.start, record=record)
        self.energy = self.story.get_current_energy()
        self.change = 0
        random.seed(seed)

    @abstractmethod
    def learn(self):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def get_policy(self):
        pass


class RandomSolver(Solver):
    """Random solver for zuikis. For testing purposes"""
    def __init__(self, field, data = None, verbose = False, seed = 0):
        super(RandomSolver, self).__init__(field, data==data, verbose = verbose, record = True, seed = seed)

    def learn(self):
        print('WARNING: Random solver doesn\'t learn!')

    def solve(self):
        while not self.story.has_ended:
            self.story.move(random.randint(1, 8))
        self.story.show()

    def get_policy(self):
        return None


class MDPSolver(Solver):

    """Simple MDP solver with different next state choosing options"""
    def __init__(self, field, data = None, verbose = False, seed = None, usepolicy = True, maxiter = 1000, maxstep = 1000, chooser = 'epsilon', cost = 1, nc = 10, sa = False):
        super(MDPSolver, self).__init__(field, data=data, verbose=verbose, seed=seed)
        self.current_state = self.story.get_vision()
        self.last_state = self.current_state
        self.freqs = Counter({self.current_state:0}) #Frequincies of all state visits
        self.U = {self.current_state:0}#U - Utility (naudos) function
        self.visits = {self.current_state:self.get_empty_visits()} #Visits: list of next states based from moevement taken from some state
        self.eps = [0.5, 'random']
        self.greed = [1 - self.eps[0], 'greedy']
        self.gamma = 1
        self.max_step = maxstep
        self.max_iter = maxiter #Together will have step * iter = 10**6 steps
        self.real_energy = 0
        self.reseted = True
        self.on_carrot = False
        self.policy = None
        ##next state chooser selection
        if chooser == 'epsilon': self.chooser = self.epsilon_chooser
        elif chooser == 'pi': self.chooser = self.pi_chooser
        elif chooser == 'R' : self.chooser = self.R_chooser
        else: print('ERROR: Wrong chooser selected'); exit(1)
        self.nc = nc #Limiting value for alpha calculations based on visit count
        self.sa = sa #Is simulated annealing on or off.
        self.counter = 0
        self.counter_max = self.max_iter * self.max_step
        self.carrot_gain = self.start.carrot_energy * self.start.carrot_factor
        self.cost = cost
        self.use_policy = usepolicy

    def learn(self):
        for i in range(self.max_iter):
            for s in range(self.max_step):
                self.counter += 1
                ##Do greedy or random move
                next_move = self.get_next_move()
                ##Do the move
                self.story.move(next_move)
                new_energy = self.story.get_current_energy()
                self.change = new_energy - self.energy
                if self.change > 0: self.on_carrot = True
                else: self.on_carrot = False
                self.energy = new_energy
                self.real_energy += self.change
                ##Dealing with states
                self.last_state = self.current_state
                self.current_state = self.story.get_vision()
                if self.story.has_ended: break
                if self.current_state not in self.U.keys():
                    self.U[self.current_state] = 0
                    self.visits[self.current_state] = self.get_empty_visits()
                self.freqs[self.last_state] += 1
                if self.last_state in self.visits.keys():
                    self.visits[self.last_state][next_move].append(self.current_state)
                ##TD - laikiniu skirtumu U atnaujinimas
                self.TD()
                if self.reseted: self.reseted = False
                self.data.record(new_energy, self.real_energy, self.change, next_move, self.U)
            if self.use_policy: self.policy = self.get_policy()
            self.story = adventure.Story(self.start, record=False)
            self.reseted = True

    def get_next_move(self, default = 1):
        if self.use_policy and self.policy is not None and self.current_state in self.policy.keys():
            return self.policy[self.current_state]
        nxt, prob = self.chooser()
        if nxt: return nxt
        next_move = default
        if prob == self.eps[1]:
            next_move = MDPSolver.random_move()
        else:
            largest = -inf
            for direction in self.visits[self.current_state].keys():
                num = len(self.visits[self.current_state][direction])
                for state in set(self.visits[self.current_state][direction]):
                    util_average = self.U[self.current_state] * self.visits[self.current_state][direction].count(state) / num
                    if util_average > largest:
                        largest = util_average
                        next_move = direction
        return next_move

    def epsilon_chooser(self, default = 1):
        """Choses next move selection mode base on uniform probability epsilon"""
        r = random.random()
        for p in [self.eps, self.greed]:
            r -= p[0]
            if r < 0.000001:
                prob = p[1]
                break
        else:
            prob = self.rng[1]
        if self.sa: self.simulated_annealing()
        return None, prob

    def simulated_annealing(self):
        """Changes epsilon value based on iteration number"""
        self.eps[0] = exp(-(self.counter/self.counter_max))
        self.greed[0] = 1 - self.eps[0]

    def pi_chooser(self, default = 1):
        pass

    def R_chooser(self):


        return None, None

    def get_alpha(self, state):
        return self.nc / (self.freqs[state] - 1 + self.nc)

    def TD(self):
        """Performs temporal difference calculation for single transition"""
        if self.reseted: return
        if self.freqs[self.current_state] == 1 and self.on_carrot: effective_U = self.carrot_gain
        else: effective_U = self.U[self.current_state]
        delta = -self.cost + self.gamma * effective_U - self.U[self.last_state]
        self.U[self.last_state] += self.get_alpha(self.last_state) * delta

    @staticmethod
    def random_move():
        p = 1/len(configurations.Field.dirs.keys())
        r = random.random()
        for i in range(1, len(configurations.Field.dirs.keys())+1):
            r -= p
            if r < 0.1**5:
                return i
        return 1

    @staticmethod
    def get_empty_visits():
        return {k:[] for k in configurations.Field.dirs.values()}

    # def mdp_move(self):
    #     if len(self.U[self.current_state][1]) == 0: return self.random_move()
    #     else:
    #         for m in self.U[self.current_state][1]:
    #             pass

    # def add_move(self, state,move):
    #     for i, e in enumerate(self.U[state][1]):
    #         if move[0] == e[0]:


    def solve(self):
        if not self.policy: self.policy = self.get_policy()
        self.data.record_policy(self.policy)
        self.story = adventure.Story(self.start, record=True)
        while not self.story.is_over():
            state = self.story.get_vision()
            if state not in self.policy.keys(): move = self.random_move()
            else: move = self.policy[state]
            self.story.move(move)
        self.data.end()
        self.story.show()

    def get_policy(self):
        policy = dict()
        for state in self.U.keys():
            largest = -inf
            for direction in self.visits[state].keys():
                num = len(self.visits[state][direction])
                for next_state in set(self.visits[state][direction]):
                    util_average = self.U[next_state] * self.visits[next_state][direction].count(next_state) / num
                    if util_average > largest:
                        largest = util_average
                        policy[state] = direction

        return policy
