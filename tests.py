import window
import random


def test_path():
    random.seed(0)
    carrot_places = [(random.randint(0, 29), random.randint(0, 29)) for i in range(5)]
    vilkas_place = (random.randint(0, 29), random.randint(0, 29))
    sample_path = [[(0,0), [vilkas_place], carrot_places]]
    for i in range(1, 20):
        new_p = (i, i)
        sample_path.append([new_p,[vilkas_place],carrot_places])
    wind = window.Window(path=sample_path)


if __name__ == '__main__':
    test_path()
