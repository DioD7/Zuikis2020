import window
import configurations
import adventure
import utils
import random
import sys
from inspect import getmembers, isfunction


def test_zuikis_vision2():
    random.seed(0)
    start = configurations.Field(zuikis = (14,15), vilkai=[(11, 15)], carrots=[(14, 11)])
    story = adventure.Story(start)
    story.get_vision().print_state()
    wind = story.show()


def test_zuikisstate():
    state1 = adventure.ZuikisState([(1,1),(24,5)],[(12,22),(7,9)],[-4, 0])
    state2 = adventure.ZuikisState([ (24, 5),(1, 1)], [(12, 22), (7, 9)],[-4, 0])
    d = {state1: 'One'}
    print(state2 in d.keys())


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
    adventure.print_zuikis_state(act.rabbit_vision())


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


def test_path():
    random.seed(0)
    dim = 30
    energy = 10
    mean_distance = 0.7
    ncarrot = int((dim / (mean_distance * energy)) ** 2)
    carrot_places = [(random.randint(0, dim - 1), random.randint(0, dim - 1)) for i in range(ncarrot)]
    for i in range(10):
        vilkas_place = (random.randint(0, 29), random.randint(0, 29))
    sample_path = [[(0,0), [vilkas_place], carrot_places]]
    for i in range(1, 20):
        new_p = (i, i)
        sample_path.append([new_p,[vilkas_place],carrot_places])
    wind = window.Window(path=sample_path)


class Testing:
    def __init__(self):
        self.tests = [[obj, name] for name, obj in getmembers(sys.modules[__name__]) if isfunction(obj) and name.startswith('test')]
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
        print('FOUND',len(self.tests), 'TESTS:')
        for i in range(len(self.tests)):
            print(i+1, '. ', self.tests[i][1], sep='')
        if default: num = default - 1
        else:
            ans = input('Launch which test?')
            num = int(ans) - 1
        self.sep2()
        test = self.tests[num]
        test_func = utils.time_it(test[0])
        self.sep()
        rezult, time = test_func()
        self.sep()
        print('Test finished in', '{:.4f}'.format(time), 's')

    def sep(self):
        print(self.breaker)

    def sep2(self):
        print(self.breaker2)


if __name__ == '__main__':
    test = Testing()
    test.execute_by_input(default = 6)
