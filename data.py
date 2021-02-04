import utils
import datetime
import sys
import os
import copy
##
# File for data gathering/verbose/analysis
##

class Data:
    """Class for data collection and its applications"""
    def __init__(self, iter, steps, verbose = False, verboseinterval = 100, time = True, printU = True, printstates = False,\
                 name='Solver', logepisodes = False):
        self.iter, self.steps = iter, steps
        self.verbose = verbose
        self.verbose_interval = verboseinterval
        self.print_time = time
        self.records = []
        self.policy = None
        self.U = None
        self.freqs = None
        self.print_U = printU
        self.log_episodes = logepisodes
        self.print_states = printstates
        self.num_records = 0
        self.timer = utils.Timer()
        self.timer.start()
        self.carrots = 0
        self.name = name

        self.episodes = []
        self.current_episode = -1

    def start_new_episode(self, state, energy, Q, freq):
        if self.log_episodes:
            self.current_episode += 1
            self.episodes.append([[state, energy,copy.deepcopy(Q), copy.deepcopy(freq)]])

    def record_step(self, state, energy, Q, freq):
        if self.log_episodes:
            self.episodes[self.current_episode].append([state, energy, copy.deepcopy(Q), copy.deepcopy(freq)])

    def record_policy(self, policy):
        self.policy = policy

    def record_freqs(self, freqs):
        self.freqs = freqs

    def record_Q(self, q):
        self.U = q

    def end(self):
        if self.print_U: ('U:',self.U.values())
        print('States detected:', len(self.U.keys()))
        if self.policy:
            print('Policy values:', self.policy.values())
        print('Carrots gathered:',self.carrots)
        total_sum = 0
        for st in self.freqs.keys():
            total_sum += sum(self.freqs[st].values())
        print('Total actions:',total_sum)
        print('Total time {:.4f} s'.format(self.timer.get_total_time()))

    def log(self):
        dat = datetime.datetime.now()
        name = 'out 0{}{} {}_{}_{}.txt'.format(dat.month, dat.day, dat.hour, dat.minute, dat.second)
        out_path = os.path.join(os.path.join(os.path.abspath('logs'),name))
        old_stdout = sys.stdout
        with open(out_path, 'w') as f:
            sys.stdout = f
            print(self.name)
            print('Iterations',self.iter)
            print('Steps per iteration', self.steps)
            print('*'*80)
            print('3 2 1')
            print('4 z 8')
            print('5 6 7')
            print('*' * 80)
            counter = 0
            if self.log_episodes:
                for episode in self.episodes:
                    counter += 1
                    if counter >5: break
                    previous_state = None
                    for step in episode:
                        state, energy, Q, freqs = step
                        print('#',counter)
                        state.print_state()
                        state.show()
                        print('current energy',energy)
                        print('current type', state.get_type_string())
                        # print('current freqs', freqs[state])
                        # print('current Q',Q[state])
                        if previous_state:
                            print('previous freqs',freqs[previous_state])
                            print('previous Q',Q[previous_state])
                        previous_state = state
                        print('=' * 80)

            for st in self.U.keys():
                    st.print_state()
                    st.show()
                    print('Value: ', self.U[st])
                    print('Frequency', self.freqs[st])
                    print('Sum freqs',sum(self.freqs[st].values()))
                    print('Policy:', self.policy[st])

            sys.stdout = old_stdout
