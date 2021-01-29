import window
import configurations
import adventure
import solvers
import qsolver
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
    print('Q solver')
    random.seed(0)
    start = configurations.Field(dims=(16,16),zuikis=(2,2),vilkai=[], carrots=[(13,13)],carrotenergy=5)
    steps = 100
    iter = 30
    data = Data(iter, steps, verbose=False, printU=True, printstates=True)
    solver = qsolver.QSolver(start, data=data, maxiter=iter, maxstep=steps, seed=0, Nmin= 5, Ncut=5, Rplus=256)
    solver.learn()
    solver.solve()
    data.log()


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


def profile_qsolver():
    print('Q profiler')
    random.seed(0)
    start = configurations.TestFields.getTests()[0]
    steps = 1000
    iter = 100
    data = Data(iter, steps, verbose=False, printU=True, printstates=True)
    solver = qsolver.QSolver(start, data=data, maxiter=iter, maxstep=steps, seed=0, Nalpha=2, Ncut=2, Rplus=500)
    cProfile.runctx('solver.learn()',globals(),locals(), sort='time')


def test_newaction():
    print('Action2')
    random.seed(0)
    # start = configurations.TestFields.getTests()[0]
    start = configurations.Field(dims = configurations.DEFAULT_DIMS, zuikis = (15, 15), vilkai=[(12, 12)], carrots=[(18, 15)])

    dms = start.get_dims()
    act = adventure.Actions2(start.get_places())
    state = start.get_state()[0:-1]
    energy = start.get_state()[-1]
    dirs = [3]
    path = [start.get_state()]
    for i in range(25):
        next_state = act.interactions(state, 4, dirs, energy)
        state = next_state[0:3]
        energy = next_state[4]
        dirs = next_state[3]
        path.append(list(state) + [energy])
    zuikis_state = act.rabbit_vision()
    zuikis_state.show()
    wind = window.Window(path=path, dim=dms)


# def test_mdpsolver():
#     random.seed(0)
#     start = configurations.TestFields.getTests()[0]
#     iter = 200
#     steps = 900
#     data = Data(iter, steps, verbose = False)
#     solver = solvers.MDPSolver(start, data = data,maxiter=200, maxstep=900, seed=0, nc = 50, sa = False, usepolicy=True)
#     solver.learn()
#     solver.solve()


def test_randomsolver():
    random.seed(0)
    start = configurations.TestFields.getTests()[0]
    solver = solvers.RandomSolver(start)
    solver.learn()
    solver.solve()


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


def test_vision():
    start = configurations.Field(zuikis = (14,15), vilkai=[(11, 15)], carrots=[(14, 11)])
    act = adventure.Actions(agent_places=start.get_places())
    dms = start.get_dims()
    state = start.get_state()[0:-1]
    energy = start.get_state()[-1]
    dirs = [3]
    path = [start.get_state()]
    for i in range(50):
        next_state = act.interactions(state, 8, dirs, energy)
        state = next_state[0:3]
        energy = next_state[4]
        dirs = next_state[3]
        path.append(list(state) + [energy])


def test_actions():
    random.seed(0)
    start = configurations.TestFields.getTests()[0]
    dms = start.get_dims()
    act = adventure.Actions()
    state = start.get_state()[0:-1]
    energy = start.get_state()[-1]
    dirs = [3]
    path = [start.get_state()]
    for i in range(100):
        next_state = act.interactions(state, 8, dirs, energy)
        state = next_state[0:3]
        energy = next_state[4]
        dirs = next_state[3]
        path.append(list(state) + [energy])
    wind = window.Window(path = path, dim = dms)


def test_field():
    tst = configurations.TestFields.getTests()
    state = tst[2].get_state()
    wind = window.Window(path=[state], dim = tst[2].get_dims())


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
