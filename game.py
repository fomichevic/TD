from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit
from collections import defaultdict
from uuid import uuid4 as uuid
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

room = {}
coroutine = {}
clients = defaultdict(list)
wait_room = None

#Constants
RESOURCES_PER_SECOND = 200
TOWER_SINGLE = Template('single', 50, 10, 5, 100)
TOWER_AREA = Template('area', 30, 15, 8, 200)
TOWER_PSY = Template('psy', 20, 15, 9, 150)
UNIT_SPEED = 0.005
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
	hp = None
	dmg = None
	range = None
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template.type
		self.hp = template.hp
		self.dmg = template.dmg
		self.range = template.range
		self.timeout = time
		self.time = time
	

class Tower:
	user = None
	x = None
	y = None
	type = None
	time = None
	timeout = None
	hp = None
	dmg = None
	range = None
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template.type
		self.hp = template.hp
		self.dmg = template.dmg
		self.range = template.range
		self.timeout = time
		self.time = time
	def update(self, delta):
		
		
class User:
	game = None
	id = None
	resources = None
	hp = USER_HP
	towers = []
	def __init__(self, game, id):
		self.game = game
		self.id = id
		self.resources = 0

class Game:
	time = 0
	units = []
	users = {}
	updates = []
	
	
	def __init__(self, id1, id2):
		users[id1] = User(self, id1)
		users[id2] = User(self, id2)
		
	def other(self, id):
		u = []
		for user in users:
			u.append(user)
		if u[0].id == id:
			return u[1].id
		else:
			return u[0].id
	
	def update(self, delta):
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
		
	
	def addToUpdate(self, str):
		updates.append(str)
		
	def updatesToJSON(self):
		str = '{'
		for upd in updates:
			str = str + upd + ','
		return str + '}'
		
	def sendUpdates(self):
		socketio.emit('update', updatesToJSON())
		del updates[:]