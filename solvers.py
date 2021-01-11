import configurations
import adventure
import data

import random
from abc import abstractmethod

#####
#AI solutions for the zuikis to manouver during the adventure.
#####

class Solver:
    """General interface for a solver"""
    def __init__(self, field, data_enabled = True, verbose = False, record = False, seed = None):
        if not field: self.start = configurations.TestFields.getTests()[0]
        else: self.start = field
        self.data_enabled = data_enabled
        self.verbose = verbose
        if self.data_enabled:
            self.data = data.Data(verbose = verbose)
        self.story = adventure.Story(self.start, record=record)
        random.seed(seed)

    @abstractmethod
    def learn(self):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def get_policy(self):
        pass


class RandomSolver(Solver):
    """Random solver for zuikis. For testing purposes"""
    def __init__(self, field, data = True, verbose = False, seed = None):
        super(RandomSolver, self).__init__(field, data_enabled=data, verbose = verbose, record = True, seed = seed)

    def learn(self):
        print('WARNING: Random solver doesn\'t learn!')

    def solve(self):
        while not self.story.has_ended:
            self.story.move(random.randint(1, 8))
        self.story.show()

    def get_policy(self):
        return None


class QSolver(Solver):
    """Reinforcement learning Q solver"""
    def __init__(self):
        pass

