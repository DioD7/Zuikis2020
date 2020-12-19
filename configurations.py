from scipy import stats
from scipy.interpolate import interp1d
import numpy as np

def add_carrot(carrot_places):
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