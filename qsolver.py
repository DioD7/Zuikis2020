from solvers import Solver
import configurations

from collections import Counter
from math import inf
import random

###
#The Q solver
###


class QSolver(Solver):
    """Reinforcement learning Q solver"""
    def __init__(self, field, data = None, maxiter = 100, maxstep = 100, verbose = False, seed = None, gamma = 1, Rplus = 10, Ncut = 10):
        super(QSolver, self).__init__(field, data=data, verbose=verbose, seed=seed)
        self.current_state = self.story.get_vision()
        self.last_state = self.current_state
        self.last_action = 1
        self.gamma = gamma
        self.R_plus = Rplus
        self.N_cut = Ncut
        self.freqs = {self.current_state:Counter()}
        self.Q = {self.current_state:Counter()}
        self.max_iter, self.max_step = maxiter, maxstep

        self.dirs = configurations.Field.dirs.values()
        self.counter = 0
        self.energy = 0
        self.change = -1

    def learn(self):
        for i in range(self.max_iter):
            for s in range(self.max_step):
                #After first move
                self.freqs[self.last_state][self.last_action] += 1
                action, largest = self.get_max_actionvalue()
                delta = self.change + self.gamma * largest - self.Q[self.last_state][self.last_action]
                self.Q[self.last_action][self.last_action] += self.get_alpha() * delta
                #Next move
                next_move, largest = self.get_max_actionvalue(explor=True)
                self.last_state = self.current_state
                self.story.move(next_move)
                self.last_action = next_move
                self.current_state = self.story.get_vision()
                new_energy = self.story.get_current_energy()
                self.change = self.energy - new_energy
                self.energy = new_energy
                #Last things
                if self.current_state not in self.freqs.keys():
                    self.freqs[self.current_state] = Counter()
                    self.Q[self.current_state] = Counter()
                self.counter += 1

    def get_max_actionvalue(self, explor = False):
        vals = dict()
        if explor:
            func = self.f
        else:
            func = lambda x: self.Q[self.current_state][x]
        for a in self.dirs:
            val = func(a)
            if val in vals.keys():
                vals[val].append(a)
            else:
                vals[val] = [a]
        max_val = max(vals.keys())
        return random.sample(vals[max_val], 1), max_val

    def f(self, action):
        """Exploration function f"""
        if self.freqs[self.current_state][action] >= self.N_cut:
            return self.Q[self.current_state][action]
        else: return self.R_plus

    def get_alpha(self):
        return 1

    def solve(self):
        while not self.story.has_ended:
            self.story.move(random.randint(1, 8))
        self.story.show()

    def get_policy(self):
        return None