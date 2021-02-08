import window
import configurations
import qsolver
import utils

import random

####
#Launcher for the project
####

class Launcher:
    """Launcher of the project AI programs and visualization"""

    def __init__(self, seed = 0):
        random.seed(seed)
        ##Setttings
        ######
        #General
        self.max_iter = 400 #Max episodes per learning cycle
        self.max_step = 500 #Max steps per episode
        self.n_cut = 5     #Alpha cut value N_c
        self.n_min = 10     #Exploration N_min value
        self.r_plus = 200   #Exploration R_+ value
        self.gamma = 0.8    #Q learning gamma value

        self.loop_limit = 3 #What maximum length closed loops does zuikis tries to break from
        self.turn_limit = 500   #Maximum turns in visualization adventure
        ######
        self.solver = qsolver.QSolver(ncut = self.n_cut, nmin = self.n_min, rplus=self.r_plus, gamma=self.gamma)
        self.example_fields = [
            configurations.Field(dims=(16, 16), zuikis=(2, 2), vilkai=[], carrotenergy=5, carrotfactor=0.7),
            configurations.Field(dims=(16, 16), zuikis=(2, 2), vilkai=[(8, 13)], carrotenergy=5, carrotfactor=0.7),
            configurations.Field(dims=(16, 16), zuikis=(2, 2), vilkai=[(8, 13), (13, 8)], carrotenergy=5, carrotfactor=0.7)
            #More examples here
        ]
        self.timer = utils.Timer()
        print('=' * 80)
        print('LAUNCHING ZUIKIS ADVENTURES')
        print('='*80)
        print('Starting learning...')
        self.learn()
        self.launch()

    def learn(self):
        """Find the best quality Q function possible"""
        learning_fields = [
            configurations.Field(dims=(16, 16), zuikis=(2, 2), vilkai=[(8, 13)], carrotenergy=5, carrotfactor=0.7),
            configurations.Field(dims=(16, 16), zuikis=(2, 14), vilkai=[(8, 13)], carrotenergy=5, carrotfactor=0.7),
            configurations.Field(dims=(16, 16), zuikis=(14, 2), vilkai=[(8, 13)], carrotenergy=5, carrotfactor=0.7),
            configurations.Field(dims=(16, 16), zuikis=(14, 14), vilkai=[(8, 13)], carrotenergy=5, carrotfactor=0.7)
        ]
        self.timer.start()
        for l_field in learning_fields:
            self.solver.learn(l_field, self.max_iter, self.max_step)
        time = self.timer.get_time()
        print('Learning finished in', '{:.4f}'.format(time),' s')
        print('='*80)

    def launch(self):
        """Launch examples"""
        print('Launching examples')
        ##Launching examples here
        ######
        # custom_example = configurations.Field(dims=(16, 16),zuikis=(0,0), vilkai=[(14,15)], carrots=[(13,13)], carrotfactor=0.7, carrotenergy=9)
        # self.launch_example(custom_example, showq=False)
        self.launch_example(self.example_fields[0], showq=False)

        # self.launch_example(self.example_fields[1], showq=False)
        # self.launch_example(self.example_fields[2], showq=False)

        # self.launch_q()

        ######

    def launch_example(self, example, showq = False):
        _path, _qs = self.solver.solve(example, loop_limit=self.loop_limit, limit_turns=self.turn_limit)
        window.Window(dim=example.get_dims(), path=_path, showQ=showq, q=_qs)

    def launch_q(self):
        __path, __qs = self.solver.quality.get_state_info()
        window.Window(dim=(16,16), path=__path, showQ=True, q=__qs)

if __name__ == "__main__":
    Launcher()
