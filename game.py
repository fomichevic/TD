from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit
from collections import defaultdict
from uuid import uuid4 as uuid
import time as Timer
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

room = {}
coroutine = {}
clients = defaultdict(list)
wait_room = None

#Constants
ANIM_FIST = [0.25, 0.5, 0.75]
ANIM_BOW = [0.75]
ANIM_SWORD = [0.25, 0.75]
CASTLE_X = 1
PLANE_HEIGHT = 10
PLANE_WIDTH = 10
RESOURCES_PER_SECOND = 40
STATE_ATTACK = 'ATTACK'
STATE_DIE = 'DIE'
STATE_GO = 'GO'
TOWER_SINGLE = Template('single', 50, 10, 5, 100)
TOWER_AREA = Template('area', 30, 15, 8, 200)
TOWER_PSY = Template('psy', 20, 15, 9, 150)
UNIT_SPEED = 0.5
UNIT_FIST = Template('fist', 40, 5, 1, 50)
UNIT_BOW = Template('bow', 30, 10, 6, 150)
UNIT_SWORD = Template('sword', 50, 15, 1.5, 100)
USER_HP = 500

class Template:
	type = None
	hp = None
	dmg = None
	range = None
	time = None
	
	def __init__(self, type, hp, dmg, range, time):
		self.type = template.type
		self.hp = template.hp
		self.dmg = template.dmg
		self.range = template.range
		self.time = time

class Unit:
	user = None
	x = None
	y = None
	type = None
	time = None
	timeout = None
	HP = None
	maxHP = None
	dmg = None
	range = None
	#state = None
	
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template.type
		self.HP = template.hp
		self.maxHP = self.HP
		self.dmg = template.dmg
		self.range = template.range
		self.timeout = time
		self.time = time
		#self.state = STATE_GO
		
	def toJSON(self):
		return '{"position":{"x":' + x + ',"y":' + y + '},"type":"' + type + '","hp":{"HP":' + hp + ',"maxHP":' + maxHP + '}}'

class Tower:
	user = None
	x = None
	y = None
	type = None
	time = None
	timeout = None
	HP = None
	maxHP = None
	dmg = None
	range = None
	state = None
	
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template.type
		self.HP = template.hp
		self.maxHP = self.HP
		self.dmg = template.dmg
		self.range = template.range
		self.timeout = time
		self.time = time
		self.state = STATE_GO
		
	def toJSON(self):
		return '{"position":{"x":' + x + ',"y":' + y + '},"type":"' + type + '","hp":{"HP":' + hp + ',"maxHP":' + maxHP + '}}'
		
	def update(self, delta):
		

class User:
	game = None
	id = None
	resources = None
	hp = USER_HP
	towers = []
	x = None
	y = None
	
	def __init__(self, game, id, castle_x):
		self.game = game
		self.id = id
		self.resources = 0
		x = castle_x
		y = (PLANE_HEIGHT - 1) / 2
		
	def update(self, delta):
		resources = resources + RESOURCES_PER_SECOND * delta / 1000
		
	def toJSON(self):
		str = '{"id":' + id + ',"res":' + resources + ',"static":['
		for tower in towers:
			str = str + tower.toJSON() + ','
		str = str + '],"dynamic":['
		for unit in game.units:
			if unit.id == id:
				str = str + unit.toJSON() + ','
		return str + '],"castle":{"position":{"x":' + x + ',"y":' + y + '},"type":"castle", "state":"' + STATE_ATTACK + '","hp":{"HP":' + hp + ',"maxHP":' + USER_HP + '}}}'
		
class Game:
	id = None
	time = None
	units = []
	users = {}
	updates = []
	plane = {}
	width = None
	height = None
	
	def __init__(self, id, id1, id2):
		self.id = id
		users[id1] = User(self, id1, CASTLE_X)
		users[id2] = User(self, id2, PLANE_WIDTH - CASTLE_X - 1)
		width = PLANE_WIDTH
		height = PLANE_WIDTH
		self.time = Timer.time() * 1000
		
	def other(self, id):
		u = []
		for user in users:
			u.append(user)
		if u[0].id == id:
			return u[1].id
		else:
			return u[0].id
	
	def update(self):
		delta = Timer.time() * 1000 - time
		time = time + delta
		for unit in units:
			unit.update(delta)
		for user in users:
			for tower in user.towers:
				tower.update(delta)
	
	def findNearestUnit(self, x, y):
		len = -1
		u = None
		for unit in units:
			if (len == -1) or (len > math.sqrt((unit.x - x) * (unit.x - x) + (unit.y - y) * (unit.y - y))):
				u = unit
				len = math.sqrt((unit.x - x) * (unit.x - x) + (unit.y - y) * (unit.y - y))
		return u
		
	def findNearestTower(self, x, y, id):
		tower = None
		temp = []
		queue = [(x, y)]
		while queue:
			pos = queue[0]
			queue.remove(pos)
			tower = plane[pos]
			if tower and tower.id == id:
				del queue
				del temp
				return tower
			temp.append(pos)
			if pos[0] < width - 1 and not (pos[0] + 1, pos[1]) in temp:
				queue.append((pos[0] + 1, pos[1]))
			if pos[0] > 0 and not (pos[0] - 1, pos[1]) in temp:
				queue.append((pos[0] - 1, pos[1]))
			if pos[1] < height - 1 and not (pos[0], pos[1] + 1) in temp:
				queue.append((pos[0], pos[1] + 1))
			if pos[1] > 0 and not (pos[0], pos[1] - 1) in temp:
				queue.append((pos[0], pos[1] - 1))
		return None
	
	def addToUpdate(self, str):
		updates.append(str)
		
	def updatesToJSON(self):
		str = '{['
		for upd in updates:
			str = str + upd + ','
		return str + ']}'
		
	def sendUpdate(self):
		json = deltasToJSON()
		for user in users:
			socketio.emit('update-delta', json, user.id)
		del updates[:]
	
	def toJSON(self):
		str = '{"users":['
		for user in users:
			str = str + user.toJSON() + ','
		str = str + '],"units":['
		for unit in units:
			str = str + unit.toJSON() + ','
		return str + ']}'
	
	def sendFullState(self):
		del updates[:]
		for user in users:
			socketio.emit('update-full', toJSON(), user.id)
	
class GameManager:
	games = None
	threads = {}
	
	def __init__(self):
		games = {}
		
	def create(self, gID, id1, id2):
		games[gID] = Game(gID, id1, id2, Timer.time() * 1000)
		threads[gID] = eventlet.spawn(games[gID].update)
	
	def update(self):
		for game in games:
			game.update(Timer.time() * 1000)