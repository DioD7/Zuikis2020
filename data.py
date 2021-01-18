import utils
##
# File for data gathering/verbose/analysis
##

class Data:
    """Class for data collection and its applications"""
    def __init__(self, verbose = False, verboseinterval = 100, time = True, printU = False):
        self.verbose = verbose
        self.verbose_interval = verboseinterval
        self.print_time = time
        self.records = []
        self.policy = None
        self.U = None
        self.print_U = printU
        self.num_records = 0
        self.timer = utils.Timer()
        self.timer.start()

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

    def end(self):
        if self.print_U: ('U:',self.U.values())
        print('States detected:', len(self.U.keys()))
        print('Policy values:', self.policy.values())
        print('Total time {:.4f} s'.format(self.timer.get_total_time()))