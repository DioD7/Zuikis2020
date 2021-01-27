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
                 Rplus = 10, Ncut = 10, Nalpha = 10, defaultcost = -1):
        super(QSolver, self).__init__(field, data=data, verbose=verbose, seed=seed)
        self.current_state = self.story.get_vision()
        self.last_state = self.current_state
        self.last_action = random.randint(1, 8)
        self.gamma = gamma
        self.R_plus = Rplus
        self.N_cut = Ncut
        self.N_alpha = Nalpha
        self.default_cost = -1
        self.freqs = {self.current_state:Counter()}
        self.Q = {self.current_state:Counter()}
        self.max_iter, self.max_step = maxiter, maxstep

        self.dirs = configurations.Field.dirs.values()
        self.counter = 0
        self.energy = self.story.get_current_energy()
        self.real_energy = 0
        self.change = -1
        self.carrots_gained  = 0
        self.policy = None

    def learn(self):
        for i in range(self.max_iter):
            for s in range(self.max_step):
                #After first move
                self.freqs[self.last_state][self.last_action] += 1
                action, largest = self.get_max_actionvalue()
                delta = self.change + self.gamma * largest - self.Q[self.last_state][self.last_action]
                self.Q[self.last_state][self.last_action] += self.get_alpha() * delta
                #Next move
                next_move, largest = self.get_max_actionvalue(explor=True)
                self.last_state = self.current_state
                self.story.move(next_move)
                if self.story.has_ended: break
                self.last_action = next_move
                self.current_state = self.story.get_vision()
                new_energy = self.story.get_current_energy()
                if s == 0:
                    self.change = self.default_cost
                else:
                    self.change = new_energy - self.energy
                if self.change > 0:
                    self.carrots_gained += 1
                    # self.change *= 10
                elif self.change < self.default_cost:
                    # self.change *= 100
                    pass
                self.energy = new_energy
                self.real_energy += self.change
                #Last things
                if self.current_state not in self.freqs.keys():
                    self.freqs[self.current_state] = Counter()
                    self.Q[self.current_state] = Counter()
                self.data.record(new_energy, self.real_energy, self.change, next_move, self.Q)
                self.counter += 1
            self.story = adventure.Story(self.start, record=False)
            self.last_state = self.story.get_vision()
            self.current_state = self.last_state
            self.last_action = random.randint(1, 8)

    def fnc(self,x):
        return self.Q[self.current_state][x]

    def get_max_actionvalue(self, explor = False):
        vals = dict()
        if explor:
            func = self.f
        else:
            func = self.fnc
        for a in self.dirs:
            val = func(a)
            if val in vals.keys():
                vals[val].append(a)
            else:
                vals[val] = [a]
        max_val = max(vals.keys())
        return random.sample(vals[max_val], 1)[0], max_val

    def f(self, action):
        """Exploration function f"""
        if self.freqs[self.current_state][action] >= self.N_cut:
            return self.Q[self.current_state][action]
        else: return self.R_plus

    def get_alpha(self):
        return self.N_alpha / (self.N_alpha - 1 + self.freqs[self.last_state][self.last_action])

    def solve(self):
        self.policy = self.get_policy()
        self.data.record_policy(self.policy)
        self.data.record_carrots(self.carrots_gained)
        self.data.record_freqs(self.freqs)
        self.data.end()
        self.story = adventure.Story(self.start, record=True)
        while not self.story.is_over():
            state = self.story.get_vision()
            if state not in self.policy.keys(): move = random.randint(1, 8)
            else: move = self.policy[state]
            self.story.move(move)
        self.story.show()


    def get_policy(self):
        policy = dict()
        for st in self.Q.keys():
            largest = -inf
            action = -1
            for act in self.Q[st].keys():
                if self.Q[st][act] > largest:
                    largest = self.Q[st][act]
                    action = act
            if action > 0:
                policy[st] = action
            else: policy[st] = random.randint(1, 8)
        return policy