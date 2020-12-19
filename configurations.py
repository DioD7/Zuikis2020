import random
import math

from scipy import stats
from scipy.interpolate import interp1d
import numpy as np

####
#Configurations for the initial state and carrot generation
####

DEFAULT_DIMS = (30,30)#Default field dims


def add_carrot(carrot_places):
	dim = 30
	prob = prob_density(carrot_places)
	while True:
		p = np.random.rand()
		coord = (random.randint(0, dim - 1), random.randint(0, dim - 1))
		if p < prob[coord[0], coord[1]]:
			carrot_places.append(coord)
			break


def prob_density(carrot_places):
	m1 = np.array([i[0] for i in carrot_places])
	m2 = np.array([i[1] for i in carrot_places])

	X, Y = np.mgrid[0:30, 0:30]
	
	positions = np.vstack([X.ravel(), Y.ravel()])
	values = np.vstack([m1, m2])
	# Probability density function
	kernel = stats.gaussian_kde(values)
	Z = np.reshape(kernel(positions).T, X.shape)
	# Interpolate PDF into interval [0, 1]
	m = interp1d([np.min(np.array(Z)), np.max(np.array(Z))], [0, 1])
	prob = np.rot90(1 - m(Z))
	return prob


def generate_carrots_fromdensity(dims, dist):
	"""Generates carrots from density distribution"""
	pass


def generate_carrots_fromuniform(dims, dist):
	"""Generates carrots from uniform distribution in a field"""
	n_carrots = int(dims[0]*dims[1]/(math.pi*dist))
	carrots = []
	for i in range(n_carrots):
		next_carrot = (random.randint(0, dims[0]-1), random.randint(0, dims[1]-1))
		carrots.append(next_carrot)
	return carrots, n_carrots


def generate_carrots(dims, dist):
	# return generate_carrots_fromdensity(dims, factor)
	return generate_carrots_fromuniform(dims, dist)


class Field:
	"""Class for initial state of field"""

	##Directions around an entity encoded by double compass letters and a number, starting from NW: 1
	#1 2 3
	#8 * 4
	#7 6 5
	dirs = {
		'NN': 2,
		'NE': 3,
		'EE': 4,
		'SE': 5,
		'SS': 6,
		'SW': 7,
		'WW': 8,
		'NW': 1,
	}
	dir_names = ('NN', 'NE', 'EE', 'SE', 'SS', 'SW', 'WW', 'NW')

	def __init__(self, dims = None, zuikis = None, vilkai = None, carrotfactor = 0.9, carrotenergy = DEFAULT_DIMS[0]):
		if not dims: self.dims = DEFAULT_DIMS
		else: self.dims = dims
		if not zuikis: self.zuikis = [random.randint(0, self.dims[0]-1), random.randint(0, self.dims[1]-1)]
		else: self.zuikis = zuikis
		if not vilkai:
			self.nvilkai = 1
			self.vilkai = [[random.randint(0, self.dims[0]-1), random.randint(0, self.dims[1]-1)]]
		else: self.nvilkai = len(vilkai); self.vilkai = vilkai
		self.carrot_energy = carrotenergy
		self.carrot_factor = carrotfactor
		self.carrots, self.ncarrots = generate_carrots(self.dims, carrotfactor * carrotenergy) #Generate carrots
		self.vilk_dirs = [[self.dirs['EE']]]*self.nvilkai #Set initial wolves moving direction to East
		self.energy = self.dims[0] * self.dims[1] #Starting energy of the zuikis
		#Generate initial state
		self.state = (self.zuikis, self.vilkai, self.carrots, self.energy)

	def get_state(self):
		return self.state

	def get_dims(self): return self.dims


class TestFields:
	"""Class for holding various initial test field states"""
	def __init__(self):
		self.tests = TestFields.getTests()

	@staticmethod
	def getTests():
		tests = []
		tests.append(Field())
		tests.append(Field(carrotenergy=15))
		tests.append(Field(dims=(15,15), zuikis=[5, 7], vilkai=[[8, 7]], carrotenergy=10))
		return tests