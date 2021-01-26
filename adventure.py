import numpy as np
import math
import configurations
import random
import copy

from configurations import generate_carrots
import window

####
#Mechanics of the zuikis adventure.
####


#State element identifiers for Zuikis(rabbit) state
elem = {
	'empty': 0,
	'zuikis': 1,
	'carrot': 2,
	'none': -1,
	'vilkas': -2,
	'wall': -3
}
inv_elem =  {val: key for key, val in elem.items()}
print_symbs = {
	0: '-',
	1: 'Z',
	2: 'C',
	-1: '  ',
	-2: 'W',
	-3: '|'
}
#Zuikis vision relative element coordinates in terms of y displacement
zuikis_displacement = {
	-4: tuple([0]),
	-3: (-1, 0, 1),
	-2: (-2,-1, 0, 1, 2),
	-1: (-3, -2, -1, 0, 1,2,2),
	0: (-4, -3, -2, -1, 0, 1, 2, 3, 4),
	1: (-3, -2, -1, 0, 1, 2, 2),
	2: (-2, -1, 0, 1, 2),
	3: (-1, 0, 1),
	4: tuple([0])
}


class Story:
	"""Class for complete story of Zuikis travels"""

	def __init__(self, field, record = True):
		"""field: initial state of the adventure
		record: whatever to record a path for the adventure
		"""
		self.field = field
		self.has_ended = False
		self.record = record
		self.moves = 0

		self.dims = self.field.get_dims()
		self.places = self.field.get_places()
		self.energy = self.field.get_energy()
		self.wolf_dirs = self.field.vilk_dirs
		self.dirs = []
		self.action = Actions2(self.places, dim = self.dims, carrot_energy=self.field.carrot_energy, carrot_factor=self.field.carrot_factor)
		if record:
			self.path = [(self.places[0], self.places[1], self.places[2], self.energy, self.action.rabbit_vision())]
		else: self.path = []

	def move(self, dir):
		"""Moves zuikis to specified direction"""
		if self.has_ended:
			print('WARNING: the story has ended for Zuikis.')
		if isinstance(dir, str):
			dir = configurations.Field.dirs[dir]
		self.dirs.append(dir)
		state = self.action.interactions(self.places, dir, self.wolf_dirs, self.energy)
		self.places = state[0:3]
		self.energy = state[4]
		self.wolf_dirs = state[3]
		if self.energy <= 0 or state[5]:
			self.has_ended = True
		if self.record:
			next_step = (self.places[0], self.places[1], self.places[2], self.energy, self.action.rabbit_vision())
			self.path.append(next_step)

	def potential_move(self, dir):
		"""Potentially moves the zuikis to dir and returns potential zuikis state"""
		if self.has_ended:
			print('WARNING: the story has ended for Zuikis.')
		if isinstance(dir, str):
			dir = configurations.Field.dirs[dir]
		state = self.action.interactions(self.places, dir, self.wolf_dirs, self.energy)
		return self.action.rabbit_vision()

	def is_over(self):
		"""Check if story is over"""
		return self.has_ended

	def show(self, speed = 2):
		"""Show story's path in the window"""
		if self.record:
			return window.Window(path=self.path, dim=self.dims, speed = speed)
		else:
			print('Warning: story has no record to show.')
			return None

	def show_vision(self):
		self.action.rabbit_vision().show()

	def get_vision(self):
		"""Get zuikis vision state"""
		return self.action.rabbit_vision()

	def get_path(self):
		"""Get story path"""
		return self.path

	def get_current_energy(self):
		"""Get current energy in the zuikis story"""
		return self.energy


class Actions2:
	move = {
		7: (-1, -1),
		6: (0, -1),
		5: (1, -1),
		4: (1, 0),
		3: (1, 1),
		2: (0, 1),
		1: (-1, 1),
		8: (-1, 0)
	}

	def __init__(self, agent_places, dim = configurations.DEFAULT_DIMS, carrot_factor = 0.9, carrot_energy = 10, cost = 1, mandistance = 4):
		self.dim = dim
		self.carrot_factor = carrot_factor
		self.carrot_energy = carrot_energy
		self.cost = cost
		self.energy = None
		self.manh_distance = mandistance
		self.carrot_gain = self.carrot_energy * self.carrot_factor
		self.carrot_eaten, self.wolf_encountered = False, False

		self.center = (self.dim[0]//2, self.dim[1]//2)
		self.rabbit, self.wolves, self.carrots = agent_places
		self.dir_angles = dict()
		for k in self.move.keys():
			self.dir_angles[k] = math.atan2(self.move[k][1],self.move[k][0])
		self.inverse_move = {v: k for k,v in self.move.items()}

	def interactions(self, agent_places, dir, wolf_dirs, energy):
		#Resets:
		self.wolf_encountered = False
		self.carrot_eaten = False
		#Move -> Wolf -> Carrot
		self.rabbit, self.wolves, self.carrots = copy.deepcopy(agent_places)
		self.energy = energy - self.cost
		self.wolf_dirs = wolf_dirs
		#Func for rabbit attack by wolf he loses energy
		def attack():
			new_new_energy = self.energy * 3/4
			return new_new_energy

		#Func for rabbit bounce if hes on wolf
		def bounce():
			rabit_vec_center = (-self.rabbit[0] + self.center[0], -self.rabbit[1] + self.center[1])
			magnitude_rabbit_vec_center = math.sqrt(rabit_vec_center[0]**2 + rabit_vec_center[1]**2)
			if magnitude_rabbit_vec_center == 0:
				while magnitude_rabbit_vec_center==0:
					rabit_vec_center = (random.randint(-1, 1)*2,random.randint(-1, 1)*2)
					magnitude_rabbit_vec_center = math.sqrt(rabit_vec_center[0] ** 2 + rabit_vec_center[1] ** 2)
				rabit_vec_center = (int(rabit_vec_center[0]/magnitude_rabbit_vec_center*4),int(rabit_vec_center[1]/magnitude_rabbit_vec_center*4))
			else:
				rabit_vec_center = (int(rabit_vec_center[0]/magnitude_rabbit_vec_center*4),int(rabit_vec_center[1]/magnitude_rabbit_vec_center*4))
			return tuple((self.rabbit[0] + rabit_vec_center[0], self.rabbit[1] + rabit_vec_center[1]))
		#Rabbit movement first
		#Checking if hes on the wolf. If so he bounces away to the center
		for wolf in self.wolves:
			if self.rabbit == wolf:
				self.rabbit = bounce()
				break
		else:
			new_rabbit_place = (self.rabbit[0] + self.move[dir][0],self.rabbit[1] + self.move[dir][1])
			if not 0 <= new_rabbit_place[0] < self.dim[0] or not 0 <= new_rabbit_place[1] < self.dim[1]:
				new_rabbit_place = self.rabbit
			self.rabbit = tuple(new_rabbit_place)
		#Wolves: move, pursuit or attack: move normaly, pursuit rabbit or attack him if they are in the same space accordingly
		#Wolfs movement second
		for index, wolf in enumerate(self.wolves):
			#Is rabbit seen by the wolf
			pursuit = False
			relative_rabbit_pos = (self.rabbit[0] - wolf[0], self.rabbit[1] - wolf[1])
			dir_to_rabbit = self.dot_product(relative_rabbit_pos, self.move[wolf_dirs[index]])
			#If wolf is on rabbit
			if wolf == self.rabbit:
				self.energy = attack()
			#If wolf sees rabbit
			elif self.manhatan_dist(wolf, self.rabbit) <= 4 and dir_to_rabbit > 0:
				pursuit = True
				rabbit_angle = math.atan2(relative_rabbit_pos[1],relative_rabbit_pos[0])
				lower = math.inf
				wolf_action = -1
				#Chose closest dir of pursuit.
				for d in range(1,9):
					angle_abs = abs(self.dir_angles[d] - rabbit_angle)
					if angle_abs < lower:
						lower = angle_abs
						wolf_action = d
				new_wolf_pos = (wolf[0]+self.move[wolf_action][0]*2,wolf[1]+self.move[wolf_action][1]*2)
				if not 0 <= new_wolf_pos[0] < self.dim[0] or not 0 <= new_wolf_pos[1] < self.dim[1]:
					new_wolf_pos = wolf
				self.wolves[index] = new_wolf_pos
				if new_wolf_pos == self.rabbit:
					self.energy = attack()

			#Else try to move normally
			else:
				if pursuit:
					pursuit = False

				delta_wolf_pos = self.move[wolf_dirs[index]]
				new_wolf_pos = (wolf[0]+delta_wolf_pos[0], wolf[1]+delta_wolf_pos[1])
				if not 0 <= new_wolf_pos[0] < self.dim[0]:
					delta_wolf_pos = (delta_wolf_pos[0]*(-1),delta_wolf_pos[1])
					new_wolf_pos = (wolf[0] + delta_wolf_pos[0], wolf[1] + delta_wolf_pos[1])
				if not 0 <= new_wolf_pos[1] < self.dim[1]:
					delta_wolf_pos = (delta_wolf_pos[0],delta_wolf_pos[1]*(-1))
					new_wolf_pos = (wolf[0] + delta_wolf_pos[0], wolf[1] + delta_wolf_pos[1])
				self.wolves[index] = new_wolf_pos
				self.wolf_dirs[index] = self.inverse_move[delta_wolf_pos]
		#Carrot third
		if self.rabbit in self.carrots and not self.wolf_encountered:
			self.carrot_eaten = True
			self.energy += self.carrot_gain
			del self.carrots[self.carrots.index(self.rabbit)]
			car, _ = generate_carrots(dims = self.dim, n_carrots=1, dist = self.carrot_gain)
			self.carrots.append(car[0])

		return [self.rabbit, self.wolves, self.carrots, self.wolf_dirs, self.energy, self.energy <=0]

	def carrot(self):
		"""Is carrot eaten after last interaction with the world"""
		return self.carrot_eaten

	def wolf(self):
		"""Is wolf encountered interaction with the world"""
		return self.wolf_encountered

	def rabbit_vision(self):
		""" Rabbit's space of vision """
		wolves = []
		carrots = []
		##Wolves
		for w in self.wolves:
			if Actions.manh_dist(self.rabbit, w) <= self.manh_distance:
				wolves.append((w[0]-self.rabbit[0],w[1]-self.rabbit[1]))
		##Carrots
		for c in self.carrots:
			if Actions.manh_dist(self.rabbit, c) <= self.manh_distance:
				carrots.append((c[0]-self.rabbit[0],c[1]-self.rabbit[1]))
		##Wall limits for x and y
		if self.rabbit[0] +1 >= self.manh_distance and abs(self.rabbit[0] - self.dim[0] +1) >= self.manh_distance:
			x_lim = 0
		else:
			x_lim = min(self.rabbit[0]-self.manh_distance, self.dim[0] - self.rabbit[0])
		if self.rabbit[1] +1 >= self.manh_distance and abs(self.rabbit[1] - self.dim[1] +1) >= self.manh_distance:
			y_lim = 0
		else:
			y_lim = min(self.rabbit[1]-self.manh_distance, self.dim[1] - self.rabbit[1])
		vision = ZuikisState(wolves, carrots, [x_lim,y_lim])
		return vision

	def is_goal(self):
		return self.energy <= 0

	@staticmethod
	def manhatan_dist(one, two):
		"""Manhattan distance between two 2D points"""
		return abs(two[0] - one[0]) +abs(two[1] - one[1])

	@staticmethod
	def dot_product(one, two):
		"""Dot product between two 2D points"""
		return one[0] * two[0] + one[1] * two[1]

class Actions:

	def __init__(self, agent_places = None, dim=30, carrot_factor=0.9, carrot_energy=10, manh_distance=4, cost = 1):
		if agent_places:
			self.rabbit_place, self.wolf_places, self.carrot_places = copy.deepcopy(agent_places)
		self.cost = cost
		self.init_energy = dim ** 2
		self.dim = dim
		self.manh_distance = manh_distance
		self.carrot_energy = carrot_energy
		self.carrot_factor = carrot_factor
		self.can_get_carrot = False
		self.move = {
				1: (-1, -1),
				2: (0, -1),
				3: (1, -1),
				4: (1, 0),
				5: (1, 1),
				6: (0, 1),
				7: (-1, 1),
				8: (-1, 0)
		}

	def is_goal(self):
		""" Checks if adventure is finished """
		if self.energy <= 0: return True
		return False

	def interactions(self, agent_places, rabbit_dir, wolf_dirs, energy):
		""" Interactions when agents are in the same cell
		Returns a tuple consisting of:
		self.rabbit_place:   new rabbit position
		self.wolf_places:    new wolf positions
		self.carrot_places:  carrot positions
		self.wolf_dirs:      wolf moving directions
		self.energy:         current rabbit energy
		self.is_goal():      is the end of the simulation is reached
		"""
		##Directions around an entity encoded by double compass letters and a number, starting from NW: 1
		#1 2 3
		#8 * 4
		#7 6 5
		# Directions may be also encoded as coordinates, with an entity as the origin of the coordinate system
		# with x axis pointing right and y axis pointing down
		# E.g. the coordinates of cell 1 are (-1, -1), cell 2 - (0, -1), etc.

		self.rabbit_place, self.wolf_places, self.carrot_places = copy.deepcopy(agent_places)
		self.energy = energy - self.cost
		self.wolf_dirs = wolf_dirs
		next_rabbit_place = (self.rabbit_place[0] + self.move[rabbit_dir][0],
				     self.rabbit_place[1] + self.move[rabbit_dir][1])

		if self.rabbit_place in self.wolf_places:
			for i in range(len(self.wolf_places)):
				wolf_place = self.wolf_places[i]
				if self.rabbit_place == wolf_place:
					self.energy -= self.init_energy * 1 / 4
			self.move_rabbit()
			for j in range(len(self.wolf_places)):
				self.move_wolf(j)
			path = (self.rabbit_place, self.wolf_places, self.carrot_places, self.wolf_dirs, self.energy, self.is_goal())
			return path

		for i, carrot_place in enumerate(self.carrot_places):
			if self.rabbit_place == carrot_place:
				self.can_get_carrot = True
				self.energy += self.carrot_energy
				self.eat_carrot(i)
				self.add_carrot()
				for j in range(len(self.wolf_places)):
					self.move_wolf(j)
				self.move_rabbit(next_rabbit_place)
				path = (self.rabbit_place, self.wolf_places, self.carrot_places, self.wolf_dirs, self.energy, self.is_goal())
				return path
		else: self.can_get_carrot = False
		# Wolf is moved first here
		for j in range(len(self.wolf_places)):
			self.move_wolf(j)
		self.move_rabbit(next_rabbit_place)
		path = (self.rabbit_place, self.wolf_places, self.carrot_places, self.wolf_dirs, self.energy, self.is_goal())
		return path

	def add_carrot(self):
		""" Add a new carrot from the uniform distribution """
		carrot, _ = generate_carrots(dims=(self.dim, self.dim), dist=self.carrot_energy * self.carrot_factor, n_carrots=1)
		self.carrot_places.append(carrot[0])

	def eat_carrot(self, index):
		""" Delete eaten carrot from the carrot list """
		del self.carrot_places[index]

	def move_rabbit(self, next_rabbit_place=None):
		""" Move rabbit to another cell """
		if not next_rabbit_place:  # If rabbit moves because of the encounter with the wolf
			cells = 4  # Move rabbit 4 cells from its position
			arr = np.array([-cells, 0, cells])
			new_positions = []
			for x in arr:
				for y in arr:
					x_new = self.rabbit_place[0] + x
					y_new = self.rabbit_place[1] + y
					if x_new == self.rabbit_place[0] and y_new == self.rabbit_place[1]: continue
					if self.is_outside_boundaries(x_new) or self.is_outside_boundaries(y_new): continue
					new_positions.append((x_new, y_new))

			center = int(self.dim / 2)  # Center of the grid
			center_coord = (center, center)
			distances = []
			best_distance = self.dim
			for new_p in new_positions:
				distance = math.sqrt((center_coord[0] - new_p[0]) ** 2 + \
					             (center_coord[1] - new_p[1]) ** 2)
				if distance < best_distance:     # Move to  a cell closest to the center of the grid
					best_distance = distance
					new_position = new_p
			self.rabbit_place = new_position
		elif not self.is_outside_boundaries(next_rabbit_place[0]) and not self.is_outside_boundaries(next_rabbit_place[1]):  # Otherwise, move rabbit to a destined space
			self.rabbit_place = next_rabbit_place

	def move_wolf(self, index):
		""" Move wolf """
		wolf_place = self.wolf_places[index]
		wolf_dir = self.wolf_dirs[index]
		wolf_vision = self.wolf_vision(wolf_place, wolf_dir)
		for i, vision in enumerate(wolf_vision):
			if self.rabbit_place == vision:  # If rabbit is seen by the wolf
				x_diff = self.rabbit_place[0] - wolf_place[0]
				y_diff = self.rabbit_place[1] - wolf_place[1]
				# If the rabbit can be caught by making a single move
				if (x_diff in [-2, 0, 2] and y_diff in [-2, 0, 2]) and \
				   ((x_diff, y_diff) != (0, 0)):
					self.wolf_places[index] = self.rabbit_place
					for m in self.move.items():
						if m[1] == (x_diff / 2, y_diff / 2):
							self.wolf_dirs[index] = m[0]
				else:  # If rabbit cannot be caught directly, move as closely as possible
					best_distance = self.dim
					new_position = wolf_place
					for i in range(-2, 3, 2):
						for j in range(-2, 3, 2):
							trial_wolf_place = (wolf_place[0] + i, wolf_place[1] + j)
							if trial_wolf_place in wolf_vision and (i, j) != (0, 0):
								# The shortest path to the rabbit is based on the Euclidean distance
								distance = math.sqrt((trial_wolf_place[0] - self.rabbit_place[0]) ** 2 + \
										     (trial_wolf_place[1] - self.rabbit_place[1]) ** 2)
								if distance < best_distance:
									best_distance = distance
									new_position = trial_wolf_place
					x_diff = new_position[0] - wolf_place[0]
					y_diff = new_position[1] - wolf_place[1]
					self.wolf_places[index] = new_position
					for m in self.move.items():
						# Change direction of the wolf to move towards the rabbit
						if m[1] == (x_diff / 2, y_diff / 2):
							self.wolf_dirs[index] = m[0]
				return

		# If rabbit not to be seen
		if self.wolf_dirs[index] % 2 == 0:  # Move diagonally to right if current direction is non-diagonal
											# If current direction is diagonal, it is preserved
			self.wolf_dirs[index] = (self.wolf_dirs[index] + 1) % 8

		trial_wolf_dir_x = self.move[self.wolf_dirs[index]][0]
		trial_wolf_dir_y = self.move[self.wolf_dirs[index]][1]
		trial_wolf_place = (self.wolf_places[index][0] + self.move[self.wolf_dirs[index]][0],
						    self.wolf_places[index][1] + self.move[self.wolf_dirs[index]][1])
		if self.is_outside_boundaries(trial_wolf_place[0]):  # If x coordinate is outside the boundary
			trial_wolf_dir_x = -self.move[wolf_dir][0]       # Change direction of vector projection in x axis
		if self.is_outside_boundaries(trial_wolf_place[1]):
			trial_wolf_dir_y = -self.move[wolf_dir][1]
		trial_wolf_dir = (trial_wolf_dir_x, trial_wolf_dir_y)
		for m in self.move.items():
			if m[1] == trial_wolf_dir:
				self.wolf_dirs[index] = m[0]
		self.wolf_places[index] = (self.wolf_places[index][0] + self.move[self.wolf_dirs[index]][0],
			                       self.wolf_places[index][1] + self.move[self.wolf_dirs[index]][1])

	def rabbit_vision(self):
		""" Rabbit's space of vision """
		wolves = []
		carrots = []
		##Wolves
		for w in self.wolf_places:
			if Actions.manh_dist(self.rabbit_place, w) <= self.manh_distance:
				wolves.append((w[0]-self.rabbit_place[0],w[1]-self.rabbit_place[1]))
		##Carrots
		for c in self.carrot_places:
			if Actions.manh_dist(self.rabbit_place, c) <= self.manh_distance:
				carrots.append((c[0]-self.rabbit_place[0],c[1]-self.rabbit_place[1]))
		##Wall limits for x and y
		if self.rabbit_place[0] +1 >= self.manh_distance and abs(self.rabbit_place[0] - self.dim +1) >= self.manh_distance:
			x_lim = 0
		else:
			x_lim = min(self.rabbit_place[0]-self.manh_distance, self.dim - self.rabbit_place[0])
		if self.rabbit_place[1] +1 >= self.manh_distance and abs(self.rabbit_place[1] - self.dim +1) >= self.manh_distance:
			y_lim = 0
		else:
			y_lim = min(self.rabbit_place[1]-self.manh_distance, self.dim - self.rabbit_place[1])
		vision = ZuikisState(wolves, carrots, [x_lim,y_lim])
		return vision

	def wolf_vision(self, wolf_place, wolf_dir):
		""" Wolf's space of vision
		The cells that wolf can see are decided by determining which cells are below the line that separates wolf's
		"back" and "front" view. Positions that are below the line are determined by calculating the cross product
		of two vectors: a vector lying on the line and a vector pointing to the cell in question. If the cross product
		of these two is positive, the cell is behind wolf's back, thus it is discarded.
		"""
		wolf_dir_90deg = (wolf_dir + 2) % 8
		if wolf_dir_90deg == 0: wolf_dir_90deg = 1
		line_vector = self.move[wolf_dir_90deg]
		wolf_vision = []
		for i in range(-self.manh_distance, self.manh_distance + 1):
			for j in range(-self.manh_distance, self.manh_distance + 1):
				if np.abs(i) + np.abs(j) > self.manh_distance: continue  # If coordinate is outside Manhattan space
				x_vision = wolf_place[0] + i
				y_vision = wolf_place[1] + j
				# Wolf cannot see beyond the walls
				if self.is_outside_boundaries(x_vision) or self.is_outside_boundaries(y_vision): continue
				point_vector = (i, j)
				cross_product = line_vector[0] * point_vector[1] - line_vector[1] * point_vector[0]
				if cross_product <= 0:
					wolf_vision.append((x_vision, y_vision))

		return wolf_vision

	def is_outside_boundaries(self, coord, lower=0, upper=29):
		""" Check if the coordinate is outside the boundaries of the grid """
		if coord < lower or coord > upper: return True
		else: return False

	def can_eat_carrot(self): return self.can_get_carrot

	@staticmethod
	def manh_dist(one, two):
		return abs(two[0] - one[0]) +abs(two[1] - one[1])


class ZuikisState:
	"""Zuikis state class"""

	def __init__(self, wolves, carrots, walls):
		self.wolves = frozenset(wolves)
		self.carrots = frozenset(carrots)
		self.walls = tuple(walls)
		self.hsh = hash((self.wolves, self.carrots, self.walls))

	def __hash__(self):
		return self.hsh

	def __eq__(self, other):
		return self.hsh == other.hsh

	def print_state(self):
		"""Prints current state to console"""
		print((self.wolves, self.carrots, self.walls))

	def show(self):
		"""Shows current state in console"""
		show_zuikis_state((self.wolves, self.carrots, self.walls))


def show_zuikis_state(st):
	"""Prints simple visualization of zuikis state into the console"""
	wolves, carrots, walls = st
	keys = sorted(zuikis_displacement.keys())
	for i in keys:
		sides = abs(i)
		print(print_symbs[elem['none']]*sides, end='')
		for j in range(9 - 2*sides):
			point = (zuikis_displacement[abs(i)][j], i)
			if point in wolves:
				symbol = print_symbs[elem['vilkas']]
			elif point in carrots:
				symbol = print_symbs[elem['carrot']]
			elif (0 < walls[0] <= point[0]) or (0 > walls[0] >= point[0]) or \
					(0 < walls[1] <= point[1]) or (0 > walls[1] >= point[1]):
				symbol = print_symbs[elem['wall']]
			elif point == (0,0):
				symbol = print_symbs[elem['zuikis']]
			else:
				symbol = print_symbs[elem['empty']]
			print('{} '.format(symbol), end='')
		print(print_symbs[elem['none']] * sides)