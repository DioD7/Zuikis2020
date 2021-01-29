from solvers import Solver
import configurations
import adventure

from collections import Counter
from math import inf
import random

###
#The Q solver
###


class QSolver(Solver):
    """Reinforcement learning Q solver"""
    def __init__(self, field, data = None, maxiter = 100, maxstep = 100, verbose = False, seed = None, gamma = 1, \
                 Rplus = 10, Ncut = 5, Nmin = 5, defaultcost = -1):
        super(QSolver, self).__init__(field, data=data, verbose=verbose, seed=seed)
        self.current_state, self.last_state = None, None
        self.last_action = None
        self.freqs = dict()
        self.Q = dict()
        self.energy = 0
        self.policy = None

        self.max_iter, self.max_step = maxiter, maxstep
        self.gamma = gamma
        self.n_cut, self.n_min, self.r_plus = Ncut, Nmin, Rplus


    def learn(self):
        """Learn Q function"""
        #Perform max_iter number of episodes
        for i in range(self.max_iter):
            #Create new story and get its state
            self.story = adventure.Story(self.start, record=False)
            self.energy = self.story.get_current_energy()
            self.current_state = self.story.get_vision()
            #Fill the state in memory. Current state must always be defined in memory.
            if self.current_state not in self.freqs.keys():
                self.freqs[self.current_state] = self.current_state.get_empty_dirs()
                self.Q[self.current_state] = self.current_state.get_empty_dirs()
            #Perform a single episode
            for s in range(self.max_step):
                #Find best next move value from current state
                next_move = self.get_max_actionvalue()
                self.last_state = self.current_state
                self.story.move(self.last_state.get_real_move(next_move))
                self.current_state = self.story.get_vision()
                #check, fill and update memory:
                self.freqs[self.last_state][next_move] += 1
                if self.current_state not in self.freqs.keys():
                    self.freqs[self.current_state] = self.current_state.get_empty_dirs()
                    self.Q[self.current_state] = self.current_state.get_empty_dirs()
                #Update Q of the previous state
                R = self.story.get_current_energy() - self.energy
                self.energy = self.story.get_current_energy()
                delta_Q = R + self.gamma * max(self.Q[self.current_state].values()) - self.Q[self.last_state][next_move]
                self.Q[self.last_state][next_move] += self.get_alpha(self.last_state, next_move) * delta_Q
                if self.story.is_over(): break
            self.data.record(self.energy, 0, 0, next_move, self.Q)


    def f(self, action):
        """Exploration function f based on action from current state"""
        if self.freqs[self.current_state][action] <= self.n_min: return self.r_plus
        else: return self.Q[self.current_state][action]

    def get_max_actionvalue(self, explor = False):
        """Find best action from current state"""
        if explor: func = self.f
        else: func = lambda x: self.Q[self.current_state][x]
        #Maximum
        values = dict()
        for direction in self.Q[self.current_state].keys():
            single_value = func(direction)
            #Put in value database
            if single_value in values.keys():
                values[single_value].append(direction)
            else:
                values[single_value] = [direction]
        max_value = max(values.keys())
        return random.sample(values[max_value],1)[0]

    def get_alpha(self, state, action):
        return self.n_cut / (self.n_cut - 1 + self.freqs[state][action])

    def solve(self):
        self.data.record_freqs(self.freqs)
        self.policy = self.get_policy()
        self.data.record_policy(self.policy)
        self.story = adventure.Story(self.start, record=True)
        while not self.story.is_over():
            state = self.story.get_vision()
            if state in self.policy.keys():
                self.story.move(state.get_real_move(self.policy[state]))
            else:
                self.story.move(7)
        self.data.end()
        self.story.show()

    def get_policy(self):
        policy = dict()
        for state in self.Q.keys():
            values = dict()
            for direction in self.Q[state].keys():
                single_value = self.Q[state][direction]
                if single_value in values.keys():
                    values[single_value].append(direction)
                else:
                    values[single_value] = [direction]
            max_value = max(values.keys())
            policy[state] = random.sample(values[max_value],1)[0]
        return policy