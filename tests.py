import window
import configurations
import adventure
import random


def test_story():
    random.seed(0)
    start = configurations.Field(zuikis = (14,15), vilkai=[(11, 15)], carrots=[(14, 11)])
    story = adventure.Story(start)
    for i in range(25):
        story.move('EE')
    for p in story.get_path():
        print(p)
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


if __name__ == '__main__':
    #test_path()
    #test_field()
    #test_actions()
    #test_vision()
    test_story()
