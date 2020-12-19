import window
import configurations
import random


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
    test_field()
