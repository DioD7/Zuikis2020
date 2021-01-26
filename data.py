import utils
import datetime
import sys
import os
import pathlib
##
# File for data gathering/verbose/analysis
##

class Data:
    """Class for data collection and its applications"""
    def __init__(self, iter, steps, verbose = False, verboseinterval = 100, time = True, printU = False, printstates = False, name='Solver'):
        self.iter, self.steps = iter, steps
        self.verbose = verbose
        self.verbose_interval = verboseinterval
        self.print_time = time
        self.records = []
        self.policy = None
        self.U = None
        self.freqs = None
        self.print_U = printU
        self.print_states = printstates
        self.num_records = 0
        self.timer = utils.Timer()
        self.timer.start()
        self.carrots = 0
        self.name = name

    def record(self, energy, real_energy, change, next_move, U):
        self.num_records += 1
        info = [energy, real_energy, change, next_move]
        #TODO: better printing format
        #TODO revise printing info fields
        if self.num_records % self.verbose_interval == 0 and self.verbose:
            print('#{} Energy, Real energy, change, next_move: {} Elapsed: {:.4f} s'.format(str(self.num_records),str(info),self.timer.get_time()))
        self.records.append(info)
        self.U = U

    def record_policy(self, policy):
        self.policy = policy

    def record_carrots(self, carrots):
        self.carrots = carrots

    def record_freqs(self, freqs):
        self.freqs = freqs

    def end(self):
        if self.print_U: ('U:',self.U.values())
        print('States detected:', len(self.U.keys()))
        if self.policy:
            print('Policy values:', self.policy.values())
        if self.print_states:
            for st in self.U.keys():
                st.print_state()
                st.show()
                print('Value: ', self.U[st])
                print('*'*80)
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
            for st in self.U.keys():
                st.print_state()
                st.show()
                print('Value: ', self.U[st])
                print('Frequency', self.freqs[st])
                print('='*80)
            sys.stdout = old_stdout
