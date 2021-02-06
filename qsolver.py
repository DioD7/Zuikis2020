from solvers import Solver
import configurations
import adventure

from collections import Counter
from math import inf
import random
import copy

###
#The Q solver
###


class QSolver(Solver):
    """Reinforcement learning Q solver"""
    def __init__(self, field, data = None, maxiter = 100, maxstep = 100, verbose = False, seed = None, gamma = 1, \
                 Rplus = 10, Ncut = 5, Nmin = 5, defaultcost = -1, saveinfo = False):
        super(QSolver, self).__init__(field, data=data, verbose=verbose, seed=seed)
        self.current_state, self.last_state = None, None
        self.last_action = None
        self.freqs = dict()
        self.Q = dict()
        self.energy = 0
        self.policy = None
        self.story_copy = None
        self.multi_q = []
        self.Qs, self.paths = [], []

        self.save = saveinfo
        self.max_iter, self.max_step = maxiter, maxstep
        self.gamma = gamma
        self.n_cut, self.n_min, self.r_plus = Ncut, Nmin, Rplus

    def learn(self, start_story = None, save_point = (0,0)):
        """Learn Q function"""
        #Perform max_iter number of episodes
        max_carrot = 0
        for i in range(self.max_iter):
            carrot_counter = 0
            #Create new story and get its state
            if not start_story:
                self.story = adventure.Story(self.start, record=False)
            self.energy = self.story.get_current_energy()
            self.current_state = self.story.get_vision()
            self.data.start_new_episode(self.current_state, self.energy, self.Q, self.freqs)
            #Fill the state in memory. Current state must always be defined in memory.
            if self.current_state not in self.freqs.keys():
                self.freqs[self.current_state] = self.current_state.get_empty_dirs()
                self.Q[self.current_state] = self.current_state.get_empty_dirs()
            if self.save:
                self.Qs.append([copy.deepcopy(self.Q[self.current_state])])
                self.paths.append([copy.deepcopy(self.story.get_state())])
            #Perform a single episode
            for s in range(self.max_step):
                if self.story.has_eaten():
                    eat = True
                    carrot_counter += 1
                else: eat = False
                if (i+1, s+1) == save_point: self.story_copy = copy.deepcopy(self.story)
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
                if self.save:
                    self.Qs[-1].append(copy.deepcopy(self.Q[self.current_state]))
                    self.paths[-1].append(copy.deepcopy(self.story.get_state()))
                #Update Q of the previous state
                R = self.story.get_current_energy() - self.energy
                # if R > 0: R = 1000
                self.energy = self.story.get_current_energy()
                delta_Q = R + self.gamma * max(self.Q[self.current_state].values()) - self.Q[self.last_state][next_move]
                self.Q[self.last_state][next_move] += self.get_alpha(self.last_state, next_move) * delta_Q
                self.data.record_step(self.current_state, self.energy, self.Q, self.freqs)
                if self.story.is_over(): break
            if carrot_counter > max_carrot: max_carrot = carrot_counter
            if self.save:
                self.multi_q.append(copy.deepcopy(self.Q))
        print('Max carrots per episode:', max_carrot)
        if self.save:
            return self.paths, self.Qs, self.multi_q

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
        self.data.record_Q(self.Q)
        self.policy = self.get_policy()
        self.data.record_policy(self.policy)
        self.story = adventure.Story(self.start, record=True)
        q = []
        while not self.story.is_over():
            state = self.story.get_vision()
            q.append(self.Q[state])
            if state in self.policy.keys():
                self.story.move(state.get_real_move(self.policy[state]))
            else:
                print('WARNING. Unknown state detected. Exiting.')
                exit(1)
        q.append(self.Q[self.story.get_vision()])
        self.data.end()
        return self.story.get_path(), q

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

    def get_story_copy(self):
        return self.story_copy