from solvers import Solver
import configurations
import adventure

from collections import Counter
from math import inf
import random
import copy
from collections import deque

###
#The Q solver
###


# class QSolver(Solver):
#     """Reinforcement learning Q solver"""
#     def __init__(self, field, data = None, maxiter = 100, maxstep = 100, verbose = False, seed = None, gamma = 1, \
#                  Rplus = 10, Ncut = 5, Nmin = 5, defaultcost = -1, saveinfo = False):
#         super(QSolver, self).__init__(field, data=data, verbose=verbose, seed=seed)
#         self.current_state, self.last_state = None, None
#         self.last_action = None
#         self.freqs = dict()
#         self.Q = dict()
#         self.energy = 0
#         self.policy = None
#         self.story_copy = None
#         self.multi_q = []
#         self.Qs, self.paths = [], []
#
#         self.save = saveinfo
#         self.max_iter, self.max_step = maxiter, maxstep
#         self.gamma = gamma
#         self.n_cut, self.n_min, self.r_plus = Ncut, Nmin, Rplus
#
#     def learn(self, start_story = None, save_point = (0,0)):
#         """Learn Q function"""
#         #Perform max_iter number of episodes
#         max_carrot = 0
#         for i in range(self.max_iter):
#             carrot_counter = 0
#             #Create new story and get its state
#             if not start_story:
#                 self.story = adventure.Story(self.start, record=False)
#             self.energy = self.story.get_current_energy()
#             self.current_state = self.story.get_vision()
#             self.data.start_new_episode(self.current_state, self.energy, self.Q, self.freqs)
#             #Fill the state in memory. Current state must always be defined in memory.
#             if self.current_state not in self.freqs.keys():
#                 self.freqs[self.current_state] = self.current_state.get_empty_dirs()
#                 self.Q[self.current_state] = self.current_state.get_empty_dirs()
#             if self.save:
#                 self.Qs.append([copy.deepcopy(self.Q[self.current_state])])
#                 self.paths.append([copy.deepcopy(self.story.get_state())])
#             #Perform a single episode
#             for s in range(self.max_step):
#                 if self.story.has_eaten():
#                     eat = True
#                     carrot_counter += 1
#                 else: eat = False
#                 if (i+1, s+1) == save_point: self.story_copy = copy.deepcopy(self.story)
#                 #Find best next move value from current state
#                 next_move = self.get_max_actionvalue()
#                 self.last_state = self.current_state
#                 self.story.move(self.last_state.get_real_move(next_move))
#                 self.current_state = self.story.get_vision()
#                 #check, fill and update memory:
#                 self.freqs[self.last_state][next_move] += 1
#                 if self.current_state not in self.freqs.keys():
#                     self.freqs[self.current_state] = self.current_state.get_empty_dirs()
#                     self.Q[self.current_state] = self.current_state.get_empty_dirs()
#                 if self.save:
#                     self.Qs[-1].append(copy.deepcopy(self.Q[self.current_state]))
#                     self.paths[-1].append(copy.deepcopy(self.story.get_state()))
#                 #Update Q of the previous state
#                 R = self.story.get_current_energy() - self.energy
#                 # if R > 0: R = 1000
#                 self.energy = self.story.get_current_energy()
#                 delta_Q = R + self.gamma * max(self.Q[self.current_state].values()) - self.Q[self.last_state][next_move]
#                 self.Q[self.last_state][next_move] += self.get_alpha(self.last_state, next_move) * delta_Q
#                 self.data.record_step(self.current_state, self.energy, self.Q, self.freqs)
#                 if self.story.is_over(): break
#             if carrot_counter > max_carrot: max_carrot = carrot_counter
#             if self.save:
#                 self.multi_q.append(copy.deepcopy(self.Q))
#         print('Max carrots per episode:', max_carrot)
#         if self.save:
#             return self.paths, self.Qs, self.multi_q
#
#     def f(self, action):
#         """Exploration function f based on action from current state"""
#         if self.freqs[self.current_state][action] <= self.n_min: return self.r_plus
#         else: return self.Q[self.current_state][action]
#
#     def get_max_actionvalue(self, explor = False):
#         """Find best action from current state"""
#         if explor: func = self.f
#         else: func = lambda x: self.Q[self.current_state][x]
#         #Maximum
#         values = dict()
#         for direction in self.Q[self.current_state].keys():
#             single_value = func(direction)
#             #Put in value database
#             if single_value in values.keys():
#                 values[single_value].append(direction)
#             else:
#                 values[single_value] = [direction]
#         max_value = max(values.keys())
#         return random.sample(values[max_value],1)[0]
#
#     def get_alpha(self, state, action):
#         return self.n_cut / (self.n_cut - 1 + self.freqs[state][action])
#
#     def solve(self):
#         self.data.record_freqs(self.freqs)
#         self.data.record_Q(self.Q)
#         self.policy = self.get_policy()
#         self.data.record_policy(self.policy)
#         self.story = adventure.Story(self.start, record=True)
#         q = []
#         while not self.story.is_over():
#             state = self.story.get_vision()
#             q.append(self.Q[state])
#             if state in self.policy.keys():
#                 self.story.move(state.get_real_move(self.policy[state]))
#             else:
#                 print('WARNING. Unknown state detected. Exiting.')
#                 exit(1)
#         q.append(self.Q[self.story.get_vision()])
#         self.data.end()
#         return self.story.get_path(), q
#
#     def get_policy(self):
#         policy = dict()
#         for state in self.Q.keys():
#             values = dict()
#             for direction in self.Q[state].keys():
#                 single_value = self.Q[state][direction]
#                 if single_value in values.keys():
#                     values[single_value].append(direction)
#                 else:
#                     values[single_value] = [direction]
#             max_value = max(values.keys())
#             policy[state] = random.sample(values[max_value],1)[0]
#         return policy
#
#     def get_story_copy(self):
#         return self.story_copy

class QSolver:
    """Class for solver using Q(state action) function learning"""
    def __init__(self, gamma = 1, ncut = 60, nmin = 5, rplus = 5):
        self.gamma = gamma
        self.n_cut = ncut
        self.n_min = nmin
        self.r_plus = rplus

        self.policy = None
        self.quality = Quality()

    def learn(self, field, max_iter, max_step, default_story = None):
        paths = []
        qs = []
        counter = 0
        ##Do all the episodes
        for iter in range(max_iter):
            if not default_story:
                story = adventure.Story(field, record= False)
            else:
                story = copy.deepcopy(default_story)
            current_state = story.get_vision()
            energy = story.get_current_energy()
            next_move = self.quality.get_maxaction(current_state, self.n_min, self.r_plus)
            ##Record paths for future returning
            paths.append([])
            qs.append([])
            last_state = None
            ##Do a single episode composed of multiple steps in a story
            for step in range(max_step):
                counter += 1
                ##Record paths
                paths[-1].append(story.get_state())
                qs[-1].append(self.quality.getq_state(current_state))
                ##Check if story is over
                if story.is_over():
                    break
                #Increase visit count N(s,a)
                self.quality.increase(current_state, next_move)
                #Alpha calculation
                a = self.quality.alpha(current_state, next_move, self.n_cut)
                ##Move to new state
                story.move(current_state.get_real_move(next_move))
                #Change variables to new values
                last_last_state = last_state
                last_state = current_state
                current_state = story.get_vision()
                change = story.get_current_energy() - energy
                #check if zuikis has moved back to the same state as before. If so penalize him for potentially being stuck.
                energy = story.get_current_energy()
                ##Calculate delta, alpha delta product and update quality of last state
                delta = change + self.gamma * self.quality.get_maxvalue(current_state) - self.quality.getq(last_state, next_move)
                alpha_delta = a * delta
                self.quality.update_value(last_state, next_move, alpha_delta)
                ##Calculate new move for next iteration
                next_move = self.quality.get_maxaction(current_state, self.n_min, self.r_plus)
        return paths, qs

    def solve(self, field, limit_turns = 500, loop_limit = 3):
        """Performs zuikis journey based on current policy"""
        self.find_policy()
        story = adventure.Story(field, record=True)
        counter = 0
        history = deque() #Deque to keep history of visited states
        path, qs = [], [] #Lists for keeping the path for all states.
        q = self.quality.get_quality_func()
        while not story.is_over() and counter < limit_turns:
            counter += 1
            current_state = story.get_vision()
            path.append(story.get_state())
            loop = False
            if current_state in history:
                position_in_history = history.index(current_state)
                if position_in_history <= loop_limit:
                    loop = True
            if loop:
                next_move = random.sample(current_state.get_dirs(),1)[0]
                if current_state in self.policy.keys():
                    qs.append(q[current_state])
                else:
                    qs.append({i: -1 for i in range(8)})
            elif current_state in self.policy.keys():
                qs.append(q[current_state])
                next_move = self.policy[current_state]
            else:
                qs.append({i:-1 for i in range(8)})
                print('WARNING: no current state description in quality function')
                next_move = random.sample(current_state.get_dirs(), 1)[0]
            story.move(current_state.get_real_move(next_move))
            history.appendleft(current_state)

        return path, qs


    def find_policy(self):
        """Calculates policy based on current state of quality function"""
        q = self.quality.get_quality_func()
        _policy = dict()
        for state in q.keys():
            values = dict()
            for direction in q[state].keys():
                _value = q[state][direction]
                if _value in values.keys():
                    values[_value].append(direction)
                else:
                    values[_value] = [direction]
            max_value = max(values.keys())
            _policy[state] = random.sample(values[max_value],1)[0]
        self.policy = _policy


class Quality:
    """Class for Quality(state action) function"""
    def __init__(self):
        self.Q = dict()
        self.F = dict()
        self.observed_states = None
        self.observations = []

    def set_observed_states(self, states):
        """Set observed states to be tracked during learning"""
        self.observed_states = states
        for i in range(len(states)):
            self.check_state(states[i])
            self.observed.append([self.Q[states[i]]])

    def update_value(self,state: adventure.ZuikisState, action,ad):
        """updates += for Q(state, action) with ad"""
        self.check_state(state)
        self.Q[state][action] += ad

    def increase(self, state, action):
        """Increase state visit count for state and action"""
        self.check_state(state)
        self.F[state][action] += 1

    def get_maxaction(self, state, nmin, rplus):
        """Get action with highest value for state"""
        self.check_state(state)
        values = dict()
        for key in self.Q[state].keys():
            # value = self.Q[state][key]
            value = self.f(state, key, nmin, rplus)
            if value in values.keys():
                values[value].append(key)
            else:
                values[value] = [key]

        max_value = max(values.keys())
        return random.sample(values[max_value], 1)[0]

    def get_maxvalue(self, state):
        """Get max quality function value for state"""
        self.check_state(state)
        return max(self.Q[state].values())

    def check_state(self, state):
        """Checks if state is in memory. If not adds empty state state"""
        if state not in self.Q:
            self.Q[state] = state.get_empty_dirs()
            self.F[state] = state.get_empty_dirs()

    def f(self, state, action, nmin, rplus):
        """Exploration function f"""
        self.check_state(state)
        if self.F[state][action] <= nmin:
            return rplus
        else:
            return self.Q[state][action]

    def alpha(self,state, action, ncut):
        """Calculates alpha"""
        self.check_state(state)
        return ncut/(ncut - 1 + self.F[state][action])

    def getq(self, state, action):
        """Get quality function value in state for action"""
        return self.Q[state][action]

    def getq_state(self, state):
        """Returns quality function of state"""
        return self.Q[state]

    def get_quality_func(self):
        """Returns quality function Q"""
        return self.Q

    def get_state_info(self):
        """Returns all state info in quality function for visualization inside window. The field state is fictional."""
        qs = []
        path = []
        place_holder = [(0,0),[],[(7,7)]]
        for state in self.Q.keys():
            path.append(place_holder + [0] + [state.get_state()])
            qs.append(self.Q[state])
        return path, qs
