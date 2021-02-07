import adventure
import configurations

import random
import math

class ZuikisState:
	"""Zuikis state class"""

	#1 2 3
	#8 z 4
	#7 6 5
	directions = [1, 2, 3, 4, 5, 6, 7, 8]
	dir_angles = {
		7: -2.356194490192345,
		6: -1.5707963267948966,
		5: -0.7853981633974483,
		4: 0.0,
		3: 0.7853981633974483,
		2: 1.5707963267948966,
		1: 2.356194490192345,
		8: 3.141592653589793
	}
	def __init__(self, wolves, carrots, walls):
		self.wolves = tuple(wolves)
		self.carrots = tuple(carrots)
		self.walls = tuple(walls)
		self.tpl = (self.wolves, self.carrots, self.walls)
		self.dirs, self.type = None, None
		self.hsh = None #Hash of the object init to None later to be created in parse()
		self.signature = None
		self.carrot_dirs, self.wolf_dirs, self.wall_dirs = [], [], []
		self.parse()

	def __hash__(self):
		return self.hsh

	def __eq__(self, other):
		return self.hsh == other.hsh

	def parse(self):
		"""Parses the state based on what zuikis sees in self.tpl"""
		#First parse what type it is
		self.type = (len(self.wolves), len(self.carrots), sum([1 for w in self.walls if w != 0]))
		self.parse_entities()
		##Sees nothing
		if self.type[0] == 0 and self.type[1] == 0 and self.type[2] == 0:
			self.dirs = [i for i in range(1, 10)]
			self.hsh = hash(self.type)
		##Sees only carrots
		elif self.type[1] > 0 and self.type[0] == 0 and self.type[2] == 0:
			self.dirs = [i for i in range(len(self.carrot_dirs))]
			self.hsh = hash(self.carrot_dirs)
		##All other scenarios. With wolfs and walls you need to keep track both direction and distance
		else:
			self.dirs = [i for i in range(1, 9)]
			self.hsh = hash(self.signature)

	def parse_entities(self):
		out_list = [self.wolf_dirs, self.carrot_dirs]
		for i,entities in enumerate([self.wolves, self.carrots]):
			for ent in entities:
				dist = adventure.Actions2.manhatan_dist((0,0), ent)
				dirr = self.get_closest_dir(ent)
				out_list[i].append((dirr, dist))
		self.wolf_dirs = frozenset(self.wolf_dirs)
		self.carrot_dirs = frozenset(self.carrot_dirs)
		self.wall_dirs = frozenset([1 if w != 0 else 0 for w in self.walls]) ##Here is an interesting place. Where we define the signature for the walls.
		self.signature = tuple([self.wolf_dirs, self.carrot_dirs, self.wall_dirs])


	def get_real_move(self, direction):
		if self.type[0] == 0 and self.type[1] == 0 and self.type[2] == 0:
			if 1 <= direction <= 8:
				return direction
			elif direction == 9:
				return random.sample(self.directions, 1)[0]
		elif self.type[1] >= 1 and self.type[0] == 0 and self.type[2] == 0:
			ordered = self.get_closest_carrots()
			return ordered[direction][0]
		else:
			return direction

	def get_closest_carrots(self):
		return list(sorted(self.carrot_dirs,key = lambda x: x[1]))

	def get_closest_dir(self, ent):
		direction = -1
		lowest = math.inf
		ent_angle = math.atan2(ent[1], ent[0])
		for k in self.dir_angles.keys():
			absolute_difference = abs(ent_angle - self.dir_angles[k])
			if absolute_difference < lowest:
				lowest = absolute_difference
				direction = k
		return direction

	def get_empty_dirs(self):
		return {d:0 for d in self.dirs}

	def get_dirs(self):
		return self.dirs

	def get_type(self):
		return self.type

	def get_type_string(self):
		if sum(self.type) == 0:
			return 'Empty'
		elif self.type[1] >= 1 and self.type[0] == 0 and self.type[2] == 0:
			return 'Carrots'
		else:
			return 'Mixed'

	def get_state(self):
		"""Returns a tuple of this state"""
		return self.tpl

	def print_state(self):
		"""Prints current state to console"""
		print(self.tpl)

	def show(self):
		"""Shows current state in console"""
		show_zuikis_state(self.tpl)


def show_zuikis_state(st):
	"""Prints simple visualization of zuikis state into the console"""
	wolves, carrots, walls = st
	keys = sorted(adventure.zuikis_displacement.keys())
	for i in keys:
		sides = abs(i)
		print(adventure.print_symbs[adventure.elem['none']]*sides, end='')
		for j in range(9 - 2*sides):
			point = (adventure.zuikis_displacement[abs(i)][j], i)
			if point in wolves:
				symbol = adventure.print_symbs[adventure.elem['vilkas']]
			elif point in carrots:
				symbol = adventure.print_symbs[adventure.elem['carrot']]
			elif (0 < walls[0] <= point[0]) or (0 > walls[0] >= point[0]) or \
					(0 < walls[1] <= point[1]) or (0 > walls[1] >= point[1]):
				symbol = adventure.print_symbs[adventure.elem['wall']]
			elif point == (0,0):
				symbol = adventure.print_symbs[adventure.elem['zuikis']]
			else:
				symbol = adventure.print_symbs[adventure.elem['empty']]
			print('{} '.format(symbol), end='')
		print(adventure.print_symbs[adventure.elem['none']] * sides)