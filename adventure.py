import numpy as np
import math
import configurations
import random

####
#Mechanics of the zuikis adventure.
####

class Actions:

	def __init__(self, dim=30, carrot_energy=10, manh_distance=4):
		self.init_energy = dim ** 2
		self.dim = dim
		self.carrot_energy = carrot_energy
		self.manh_distance = manh_distance
		
	def is_goal(self):
		""" Checks if adventure is finished """
		if self.energy <= 0: return True
		return False

	def interactions(self, agent_places, energy, wolf_dirs):
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
		
		self.rabbit_place, self.wolf_places, self.carrot_places = copy.deepcopy(agent_places)
		self.energy = energy
		self.wolf_dirs = wolf_dirs
		
		if self.rabbit_place in self.wolf_places:
			for i in range(len(self.wolf_places)):
				wolf_place = self.wolf_places[i]
				if self.rabbit_place == wolf_place:
					self.energy -= self.init_energy * 1 / 4
			self.move_rabbit(cells=4)
			for j in range(len(self.wolf_places)):
				self.move_wolf(j)
			path = (self.rabbit_place, self.wolf_places, self.carrot_places, self.wolf_dirs, self.energy, self.is_goal())
			return path

		for i, carrot_place in enumerate(self.carrot_places):
			if self.rabbit_place == carrot_place:
				self.energy += self.carrot_energy
				self.eat_carrot(i)
				self.add_carrot()
				self.move_rabbit(cells=1)
				for j in range(len(self.wolf_places)):
					self.move_wolf(j)
				path = (self.rabbit_place, self.wolf_places, self.carrot_places, self.wolf_dirs, self.energy, self.is_goal())
				return path
		self.move_rabbit(cells=1)
		for j in range(len(self.wolf_places)):
			self.move_wolf(j)
		path = (self.rabbit_place, self.wolf_places, self.carrot_places, self.wolf_dirs, self.energy, self.is_goal())
		return path
		
	def add_carrot(self):
		""" Add a new carrot from the uniform distribution """
		pass

	def eat_carrot(self, index):
		""" Delete eaten carrot from the carrot list """
		del self.carrot_places[index]

	def move_rabbit(self, cells=1):
		""" Move rabbit to another cell """
		arr = np.array([-cells, 0, cells])
		new_positions = []
		for x in arr:
			for y in arr:
				x_new = self.rabbit_place[0] + x
				y_new = self.rabbit_place[1] + y
				if x_new == self.rabbit_place[0] and y_new == self.rabbit_place[1]: continue
				if self.is_outside_boundaries(x_new) or self.is_outside_boundaries(y_new): continue
				new_positions.append((new_x, new_y))
		if cells == 1:
			rand_pos = new_positions[random.randint(0, len(new_positions) - 1)]
			self.rabbit_place = rand_pos
		else:  # If rabbit moves because of the encounter with the wolf
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

	def move_wolf(self, index):
		""" Move wolf """
		wolf_place = self.wolf_places[index]
		wolf_dir = self.wolf_dirs[index]
		wolf_vision = self.wolf_vision(wolf_place, wolf_dir)
		for i, vision in enumerate(wolf_vision):
			if self.rabbit_place == vision:  # If rabbit is seen by the wolf
				x_diff = abs(self.rabbit_place[0] - wolf_place[0])
				y_diff = abs(self.rabbit_place[1] - wolf_place[1])
				# If the rabbit can be caught by making a single move
				if (x_diff in [0, 2] and y_diff in [0, 2]) and \
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
							if trial_wolf_place in wolf_vision:
								# The shortest path to the rabbit is based on the Euclidean distance
								distance = math.sqrt((trial_wolf_place[0] - self.rabbit_place[0]) ** 2 + \
										     (trial_wolf_place[1] - self.rabbit_place[1]) ** 2)
								if distance < best_distance:
									best_distance = distance
									new_position = trial_wolf_place
									
					self.wolf_places[index] = new_position
					for m in self.move.items():
						# Change direction of the wolf to move towards the rabbit
						if m[1] == (x_diff / 2, y_diff / 2):
							self.wolf_dirs[index] = m[0]
				return
			
		# If rabbit not to be seen
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
		rabbit_vision = []
		for i in range(-self.manh_distance, self.manh_distance + 1):
			for j in range(-self.manh_distance, self.manh_distance + 1):
				if np.abs(i) + np.abs(j) > self.manh_distance: continue  # Discard cells outside the
											                             # Manhattan space
				x_vision = self.rabbit_place[0] + i
				y_vision = self.rabbit_place[1] + j
				# Boundary conditions
				if self.is_outside_boundaries(x_vision) or self.is_outside_boundaries(y_vision): continue
				rabbit_vision.append((x_vision, y_vision))
		return rabbit_vision
		
	def wolf_vision(self, wolf_place, wolf_dir):
		""" Wolf's space of vision """
		# Directions described as the coordinates from the origin as dictionary keys; dictionary values are limits
		# for the coordinates, based on the shape of the Manhattan space;
		# limits are formatted as [(x_min, x_max), (y_min, y_max)]
		intervals = {
					 (-1, 1): [(-4, 2), (-2, 4)],
					 (0, 1): [(-4, 4), (0, 4)],
					 (1, 1): [(-2, 4), (-2, 4)],
					 (1, 0): [(0, 4), (-4, 4)],
					 (1, -1): [(-2, 4), (-4, 2)],
					 (0, -1): [(-4, 0), (-4, 4)],
					 (-1, -1): [(-4, 2), (-4, 2)],
					 (-1, 0): [(-4, 0), (-4, 4)]
		}
		manh_boundaries = intervals[self.move[wolf_dir]]

		wolf_vision = []
		for i in range(-self.manh_distance, self.manh_distance + 1):
			for j in range(-self.manh_distance, self.manh_distance + 1):
				if i >= manh_boundaries[0][0] and i <= manh_boundaries[0][1] and \
				   j >= manh_boundaries[1][0] and j <= manh_boundaries[1][1]:
					if np.abs(i) + np.abs(j) > self.manh_distance: continue
					x_vision = wolf_place[0] + i
					y_vision = wolf_place[1] + j
					if self.is_outside_boundaries(x_vision) or self.is_outside_boundaries(y_vision): continue
					wolf_vision.append((x_vision, y_vision))
		return wolf_vision

	def is_outside_boundaries(self, coord, lower=0, upper=29):
		""" Check if the coordinate is outside the boundaries of the grid """
		if coord < lower or coord > upper: return True
		else: return False
