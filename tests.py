import window
import configurations
import adventure
import zuikis_state
import solvers
import qsolver
import time
from data import Data
import utils
import random
import sys
import cProfile
from inspect import getmembers, isfunction

##
#Tests
##


def test_qsolver():
    print('Q solver testing')
    start1 = configurations.Field(dims=(16,16), zuikis = (2,2), vilkai=[], carrotenergy=5, carrotfactor= 0.7)
    start2 = configurations.Field(dims=(16, 16), zuikis=(2, 14), vilkai=[], carrotenergy=5, carrotfactor=0.7)
    start3 = configurations.Field(dims=(16, 16), zuikis=(14, 2), vilkai=[], carrotenergy= 5, carrotfactor=0.7)
    start4 = configurations.Field(dims=(16, 16), zuikis=(14, 14), vilkai=[], carrotenergy= 5, carrotfactor=0.7)
    solver = qsolver.QSolver(ncut = 1500, nmin = 10, rplus=20)
    paths, quality = solver.learn(start1, 200, 400)
    paths, quality = solver.learn(start2, 200, 400)
    paths, quality = solver.learn(start3, 200, 400)
    paths, quality = solver.learn(start4, 200, 400)
    __path, __qs = solver.solve(start1)
    episode = 99
    _path = __path
    _q = __qs
    print('Total states:',len(solver.quality.Q.keys()))
    win = window.Window(dim=start1.get_dims(), path=_path, showQ=True, q=_q)



def test_zuikisstatevisual():
    print('Zuikis state visualization')
    random.seed(0)
    # start = configurations.TestFields.getTests()[0]
    start = configurations.Field(dims = (16,16), zuikis = (2, 2), vilkai=[], carrots=[(13, 13)])

    dms = start.get_dims()
    act = adventure.Actions2(start.get_places(), dim = start.get_dims())
    state = start.get_state()[0:-1]
    energy = start.get_state()[-1]
    dirs = [3]
    path = [list(start.get_state())+[act.rabbit_vision().get_state()]]
    for i in range(25):
        next_state = act.interactions(state, 3, dirs, energy)
        state = next_state[0:3]
        energy = next_state[4]
        dirs = next_state[3]
        zuikis_state = act.rabbit_vision().get_state()
        path.append(list(state) + [energy]+[zuikis_state])
    wind = window.Window(path=path, dim=dms)


def test_newzuikisstate():
    print('New ZuikisState')
    start = configurations.Field(dims=(30, 30), zuikis=(15, 15), vilkai=[], carrots=[(14,14), (17,17)], carrotenergy=5)
    act = adventure.Actions2(start.get_places())
    state = act.rabbit_vision()
    state.show()
    print('Type is',state.type)
    print('wolves, carrots, walls',state.wolves, state.carrots, state.walls)
    print('Empty dirs',state.get_empty_dirs())
    print('Dirs', state.get_dirs())


def test_newaction():
    print('Action2')
    random.seed(0)
    # start = configurations.TestFields.getTests()[0]
    start = configurations.Field(dims = (16,16), zuikis = (2, 2), vilkai=[], carrots=[(13, 13)])

    dms = start.get_dims()
    act = adventure.Actions2(start.get_places(), dim = start.get_dims())
    state = start.get_state()[0:-1]
    energy = start.get_state()[-1]
    dirs = [3]
    path = [start.get_state()]
    for i in range(25):
        next_state = act.interactions(state, 3, dirs, energy)
        state = next_state[0:3]
        energy = next_state[4]
        dirs = next_state[3]
        path.append(list(state) + [energy])
    zuikis_state = act.rabbit_vision()
    zuikis_state.show()
    wind = window.Window(path=path, dim=dms)


def test_zuikisstate():
    random.seed(0)
    start = configurations.Field(zuikis = (14,15), vilkai=[(11, 15)], carrots=[(14, 11)])
    story = adventure.Story(start)
    for i in range(25):
        story.move('EE')
        story.show_vision()
    wind = story.show()


def test_story():
    random.seed(0)
    start = configurations.Field(zuikis = (14,15), vilkai=[(11, 15)], carrots=[(14, 11)])
    story = adventure.Story(start)
    for i in range(25):
        story.move('EE')
    wind = story.show()





class Testing:
    """Class for automatic test handling"""
    def __init__(self):
        self.tests = [[obj, name] for name, obj in getmembers(sys.modules[__name__]) if isfunction(obj) and (name.startswith('test') or name.startswith('profile'))]
        self.breaker = '='*80
        self.breaker2 = '*'*85

    def execute(self):
        """Executes all the tests starting from the last one"""
        print('Found',len(self.tests), 'tests.')
        for i in reversed(range(len(self.tests))):
            self.sep2()
            test = self.tests[i]
            test_func = utils.time_it(test[0])
            print('EXECUTING Test:',test[1])
            self.sep()
            rezult, time = test_func()
            self.sep()
            print('Test finished in', '{:.4f}'.format(time), 's')
            ans = input('Launch next?(y/n)')
            if ans.lower() == 'n':
                break

    def execute_by_input(self, default = None):
        """Executes tests determined by user input"""
        print('FOUND',len(self.tests), 'TESTS:')
        for i in range(len(self.tests)):
            print(i+1, '. ', self.tests[i][1], sep='')
        if default:
            for t in self.tests:
                if t[1] == default:
                    num = self.tests.index(t)
                    break
            else:
                print('Default test', default, 'not found')
                exit(1)
        else:
            ans = input('Launch which test?')
            num = int(ans) - 1
        self.sep2()
        test = self.tests[num]
        print('LAUNCHING',test[1])
        test_func = utils.time_it(test[0])
        self.sep()
        rezult, time = test_func()
        self.sep()
        print('Test finished in', '{:.4f}'.format(time), 's')

    def sep(self):
        print(self.breaker)

    def sep2(self):
        print(self.breaker2)

default_test = 'test_qsolver'

if __name__ == '__main__':
    test = Testing()
    test.execute_by_input(default = default_test)
