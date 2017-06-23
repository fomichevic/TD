import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit
from collections import defaultdict
from uuid import uuid4 as uuid
import time as Timer
import json
import random
import math

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
room = {}
coroutine = {}
clients = defaultdict(list)
wait_room = None

#Constants
UPDATE_FULL = 5
UPDATE_DELTA = 0.1
UPDATE_SERVER = 0.1

ANIM_FIST = [0.25, 0.5, 0.75]
ANIM_BOW = [0.75]
ANIM_SWORD = [0.25, 0.75]

AREA_RANGE = 3
CASTLE_X = 1
MINIMAL_RANGE = 0.2
PLANE_HEIGHT = 10
PLANE_WIDTH = 10
#PRICE_PSY = 200
RESOURCES_PER_SECOND = 20
STATE_ATTACK = 'ATTACK'
STATE_DIE = 'DIE'
STATE_GO = 'GO'
#TOWER_PSY = Template('psy', 20, 15, 9, 150)
UNIT_SPEED = 0.1

DEBUG = True

TEMPLATES = {'single': ('single', 100, 50, 5, 5, 800), #type, price, hp, dmg, range, timeout
			 'area': ('area', 140, 30, 7.5, 8, 1600), 
			 'fist': ('fist', 20, 40, 2.5, 1, 400), 
			 'bow': ('bow', 35, 30, 5, 3, 1200), 
			 'sword': ('sword', 40, 50, 7.5, 1.5, 800),
			 'castle': ('castle', 0, 500, 0, 0, 0)}

@socketio.on('buy')
def buy(data):
	GameManager.players[request.sid].buy(data)
	
@socketio.on('sell')
def sell(data):
	GameManager.players[request.sid].sell(data)
	
@socketio.on('join')
def join(data):
	GameManager.join(request.sid)
	
@socketio.on('leave')
def leave(data):
	GameManager.leave(request.sid)

@app.route('/')
def start():
    return render_template('base.html', async_mode=socketio.async_mode)

def min_by_val(dictionary):
	result = None
	for key in dictionary:
		if not result or ((key in dictionary) and (dictionary[key] < dictionary[result])):
			result = key
	return result
	
def sign(x):
	if x in [0.0, -0.0, 0, -0]:
		return 0
	if x > 0:
		return 1
	return -1

def infinite(func, timeout):
	while True:
		func()
		eventlet.sleep(timeout)
	
class Unit:
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template[0]
		self.hp = template[2]
		self.maxHP = self.hp
		self.dmg = template[3]
		self.range = template[4]
		self.timeout = template[5]
		self.timer = template[5]
		self.time = int(Timer.time() * 1000)
		id = uuid().int
		while id in self.user.game.usedID:
			id = uuid().int
		self.id = id
		self.user.game.usedID.append(id)
		#self.state = STATE_GO
		self.path = []
		self.target = None
	
	def toJSON(self):
		return str(self.id) + ':{"position":{"x":' + str(self.x) + ',"y":' + str(self.y) + '},"type":"' + self.type + '","hp":{"HP":' + str(self.hp) + ',"maxHP":' + str(self.maxHP) + '}}'

	def move(self, dX, dY):
		self.x = self.x + (dX / math.sqrt(dX ** 2 + dY ** 2)) * UNIT_SPEED
		self.y = self.y + (dY / math.sqrt(dX ** 2 + dY ** 2)) * UNIT_SPEED
	
	def update(self):
		if self.hp <= 0:
			self.user.game.units.remove(self)
			self.user.game.addToUpdate('{"type":"remove","id":' + str(self.id) + '}')
			del self
		else:
			delta = int(Timer.time() * 1000) - self.time
			self.time = self.time + delta
			self.timer = self.timer - delta
			possibleTarget = self.user.game.findNearestUnit(self.x, self.y, self.user.game.other(self.user.id))
			if self.target == None or self.target.hp <= 0 or (possibleTarget and (self.x - possibleTarget.x) ** 2 + (self.y - possibleTarget.y) ** 2 < (self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2):
				self.target = possibleTarget
				if not possibleTarget:
					self.target = self.user.game.findNearestTower(self.x, self.y, self.user.game.other(self.user.id))
				if self.target:
					self.path = self.user.game.path(self.user.game.nearestPoint(self.target.x, self.target.y, self.x, self.y), self.user.game.nearestPointTo(int(self.target.x), int(self.target.y), self.x, self.y, self.range))
			if self.target and math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.range:
				if self.timer <= 0:
					self.target.hp = int(self.target.hp - self.dmg)
					self.timer = self.timeout
			else:
				if self.target:
					self.path = self.user.game.path(self.user.game.nearestPoint(self.target.x, self.target.y, self.x, self.y), self.user.game.nearestPointTo(int(self.target.x), int(self.target.y), self.x, self.y, self.range))
				if self.path and math.sqrt((self.x - self.path[0][0]) ** 2 + (self.y - self.path[0][1]) ** 2) <= MINIMAL_RANGE:
					self.x = self.path[0][0]
					self.y = self.path[0][1]
					self.path.pop(0)
				if self.path:
					self.move(self.path[0][0] - self.x, self.path[0][1] - self.y)
	
	def toStr(self, b):
		if self.target and b:
			return self.type + '[' + str(self.user.id) + ']: (' + str(self.hp) + '/' + str(self.maxHP) + ') at {' + str(round(self.x, 2)) + '; ' + str(round(self.y, 2)) + '} -> ' + self.target.toStr(False)
		else:
			return self.type + '[' + str(self.user.id) + ']: (' + str(self.hp) + '/' + str(self.maxHP) + ') at {' + str(round(self.x, 2)) + '; ' + str(round(self.y, 2)) + '}'
	
class Tower:
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template[0]
		self.hp = template[2]
		self.maxHP = self.hp
		self.dmg = template[3]
		self.range = template[4]
		self.timeout = template[5]
		self.timer = template[5]
		self.time = int(Timer.time() * 1000)
		#self.state = STATE_GO
		id = uuid().int
		while id in self.user.game.usedID:
			id = uuid().int
		self.id = id
		self.user.game.usedID.append(id)
		self.target = None

	def toJSON(self):
		return str(self.id) + ':{"position":{"x":' + str(self.x) + ',"y":' + str(self.y) + '},"type":"' + str(self.type) + '","hp":{"HP":' + str(self.hp) + ',"maxHP":' + str(self.maxHP) + '}}'

	def update(self):
		if self.hp <= 0:
			del self.user.game.plane[(self.x, self.y)]
			self.user.game.addToUpdate('{"type":"remove","id":' + str(self.id) + '}')
			self.user.towers.remove(self)
			del self
		else:
			delta = int(Timer.time() * 1000) - self.time
			self.time = self.time + delta
			self.timer = self.timer - delta
			if self.target and self.target.hp <= 0:
				self.target = None
			if self.timer <= 0:
				if not self.target or math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) > self.range:
					self.target = self.user.game.findNearestUnit(self.x, self.y, self.user.game.other(self.user.id))
				if not self.target:
					self.target = self.user.game.findNearestTower(self.x, self.y, self.user.game.other(self.user.id))
				if self.target and math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.range:
					if self.type == 'single':
						self.target.hp = int(self.target.hp - self.dmg)
					elif self.type == 'area':
						self.user.game.areaDamage(self.target.x, self.target.y, self.dmg, AREA_RANGE)
					self.timer = self.timeout

	def toStr(self, b):
		if b and self.target:
			return self.type + '[' + str(self.user.id) + ']: (' + str(self.hp) + '/' + str(self.maxHP) + ') at {' + str(round(self.x, 2)) + '; ' + str(round(self.y, 2)) + '} -> ' + self.target.toStr(False)
		else:
			return self.type + '[' + str(self.user.id) + ']: (' + str(self.hp) + '/' + str(self.maxHP) + ') at {' + str(round(self.x, 2)) + '; ' + str(round(self.y, 2)) + '}'
			
class User:
	def __init__(self, game, id, castle_x):
		self.game = game
		self.id = id
		self.resources = 0
		self.towers = []
		self.time = int(Timer.time() * 1000)
		self.castle = Tower(self, castle_x, (PLANE_HEIGHT - 1) / 2, TEMPLATES['castle'])
		
	def update(self):
		delta = int(Timer.time() * 1000) - self.time
		self.time = self.time + delta
		self.resources = int(self.resources + RESOURCES_PER_SECOND * delta / 1000)
	
	def buyUnit(self, template):
		if self.resources < template[1]:
			return
		self.game.units.append(Unit(self, self.castle.x, self.castle.y, template))
		self.resources = self.resources - template[1]
		self.game.addToUpdate('{"type":"add","x":' + str(self.castle.x) + ',"y":' + str(self.castle.y) + ',"type":' + template[0] + '}')
	
	def buyTower(self, x, y, template):
		if self.resources < template[1] or (x, y) in self.game.plane:
			return
		self.game.plane[(x, y)] = Tower(self, x, y, template)
		self.towers.append(self.game.plane[(x, y)])
		self.resources = self.resources - template[1]
		self.game.addToUpdate('{"type":"add","x":' + str(x) + ',"y":' + str(y) + ',"type":' + template[0] + '}')
	
	def buy(self, str):
		data = json.loads(str)
		if data and data['type']:
			if data['type'] in ['fist', 'bow', 'sword']:
				self.buyUnit(TEMPLATES[data['type']])
			elif data['type'] in ['single', 'area']:
				self.buyTower(data['x'], data['y'], TEMPLATES[data['type']])
	
	def sell(self, str):
		data = json.loads(str)
		if not self.game.plane[(data.x, data.y)]:
			return
		self.resources = self.resources + TEMPLATES[self.game.plane[(data.x, data.y)].type].price / 2
		del self.game.plane[(data.x, data.y)]
		for tower in self.towers:
			if tower.x == data.x and tower.y == data.y:
				self.towers.remove(tower)
				break
		self.game.addToUpdate('{"type":"remove","id":' + str(self.id) + '}')
	
	def toJSON(self):
		string = '{"id":' + str(self.id) + ',"res":' + str(self.resources) + ',"static":{'
		for tower in self.towers:
			string = string + tower.toJSON() + ','
		string = string + '"castle":{"position":{"x":' + str(self.castle.x) + ',"y":' + str(self.castle.y) + '},"type":"castle","hp":{"HP":' + str(self.castle.hp) + ',"maxHP":' + str(TEMPLATES['castle'][2]) + '}}},"dynamic":{'
		for unit in self.game.units:
			if unit.user == self:
				string = string + unit.toJSON() + ','
		return string + '}}'
	
class Game:
	def __init__(self, id, id1, id2):
		self.id = id
		self.users = {}
		self.units = []
		self.updates = []
		self.plane = {}
		self.usedID = []
		self.width = PLANE_WIDTH
		self.height = PLANE_WIDTH
		self.time = int(Timer.time() * 1000)
		self.users[id1] = User(self, id1, CASTLE_X)
		self.users[id2] = User(self, id2, PLANE_WIDTH - CASTLE_X - 1)
	
	def other(self, id):
		u = []
		for user in self.users.values():
			u.append(user)
		if u[0].id == id:
			return u[1].id
		else:
			return u[0].id
	
	def update(self):
		for unit in self.units:
			unit.update()
		for user in self.users.values():
			user.update()
			for tower in user.towers:
				tower.update()
		if self.winner():
			GameManager.stop(self.id)
	
	def areaDamage(self, x, y, damage, range):
		for unit in self.units:
			if math.sqrt((unit.x - x) ** 2 + (unit.y - y) ** 2) <= range:
				unit.hp = int(unit.hp - damage)
		for user in self.users.values():
			for tower in user.towers:
				if math.sqrt((tower.x - x) ** 2 + (tower.y - y) ** 2) <= range:
					tower.hp = int(tower.hp - damage)
	
	def findNearestUnit(self, x, y, id):
		len = -1
		u = None
		for unit in self.units:
			if unit.user.id == id and ((len == -1) or (len > math.sqrt((unit.x - x) * (unit.x - x) + (unit.y - y) * (unit.y - y)))):
				u = unit
				len = math.sqrt((unit.x - x) * (unit.x - x) + (unit.y - y) * (unit.y - y))
		return u
	
	def findNearestTower(self, x, y, id):
		twr = None
		for tower in self.users[id].towers:
			if not twr or math.sqrt((tower.x - x) ** 2 + (tower.y - y) ** 2) < math.sqrt((twr.x - x) ** 2 + (twr.y - y) ** 2):
				twr = tower
		return twr
	
	def nearestPoint(self, targetX, targetY, x, y):
		return (int(int(x) + sign(targetX - x)), int(int(y) + sign(targetY - y)))
	
	def nearestPointTo(self, targetX, targetY, x, y, rng):
		data = {}
		for tX in range(int(targetX - rng), int(targetX + rng)):
			for tY in range(int(targetY - rng), int(targetY + rng)):
				if math.sqrt((tX - targetX) ** 2 + (tY - targetY) ** 2) <= rng:
					data[(tX, tY)] = math.sqrt((tX - x) ** 2 + (tY - y) ** 2)
		return min_by_val(data) #?
	
	def near(self, num, pos):
		points = {}
		if (pos[0] + 1, pos[1]) in num:
			points[(pos[0] + 1, pos[1])] = num[(pos[0] + 1, pos[1])]
		if (pos[0], pos[1] + 1) in num:
			points[(pos[0], pos[1] + 1)] = num[(pos[0], pos[1] + 1)]
		if (pos[0] - 1, pos[1]) in num:
			points[(pos[0] - 1, pos[1])] = num[(pos[0] - 1, pos[1])]
		if (pos[0], pos[1] - 1) in num:
			points[(pos[0], pos[1] - 1)] = num[(pos[0], pos[1] - 1)]
		return points
	
	def path(self, pos1, pos2):
		if pos1 == None or pos2 == None:
			return []
		queue = [pos1]
		temp = []
		num = {pos1: 0}
		while queue:
			pos = queue[0]
			queue.remove(pos)
			if pos == pos2:
				break
			elif pos in self.plane:
				continue
			else:
				temp.append(pos)
				if not pos in num:
					num[pos] = num[min_by_val(self.near(num, pos))] + 1
				if pos[0] < self.width - 1 and not (pos[0] + 1, pos[1]) in temp:
					queue.append((pos[0] + 1, pos[1]))
				if pos[0] > 0 and not (pos[0] - 1, pos[1]) in temp:
					queue.append((pos[0] - 1, pos[1]))
				if pos[1] < self.height - 1 and not (pos[0], pos[1] + 1) in temp:
					queue.append((pos[0], pos[1] + 1))
				if pos[1] > 0 and not (pos[0], pos[1] - 1) in temp:
					queue.append((pos[0], pos[1] - 1))
		data = []
		pos = pos2
		if pos1 == None or pos2 == None:
			return []
		while not pos == pos1:
			pos = min_by_val(self.near(num, pos))
			if pos in data:
				print(data)
				raise pos
			data.insert(0, pos)
		return data
	
	def winner(self):
		for user in self.users.values():
			if user.castle.hp <= 0:
				return self.other(user.id)
		return None
	
	def addToUpdate(self, str):
		self.updates.append(str)
	
	def updatesToJSON(self):
		str = '{['
		for upd in self.updates:
			str = str + upd + ','
		return str + ']}'
	
	def sendUpdate(self):
		json = self.updatesToJSON()
		socketio.emit('update-delta', json, room = self.id)
		del self.updates[:]
	
	def toJSON(self):
		str = '{"players":['
		for user in self.users.values():
			str = str + user.toJSON() + ','
		return str + ']}'

	def unitsToString(self):
		str = ''
		for unit in self.units:
			str = str + unit.toStr(True) + '\n'
		return str
		
	def towersToString(self):
		str = ''
		for user in self.users.values():
			for tower in user.towers:
				str = str + tower.toStr(True) + '\n'
		return str

	def sendFullState(self):
		del self.updates[:]
		socketio.emit('update-full', self.toJSON(), room = self.id)

	def toStr(self):
		s = ''
		for user in self.users.values():
			s = s + '[' + str(user.id) + ']: (' + str(user.castle.hp) + '/' + str(user.castle.maxHP) + ') - ' + str(user.resources) + '\n'
		return s

	def isOver(self):
		return not self.winner() == None

class GameManager:
	games = {}
	threads = {}
	players = {}
	waiting = None

	@classmethod
	def killAll(cls): # Do not use!
		keys = list(cls.games.keys())
		for key in keys:
			cls.kill(key)

	@classmethod
	def start(cls, id1, id2):
		gID = uuid().int
		while gID in cls.games:
			gID = uuid().int
		if not DEBUG:
			join_room(gID, id1)
			join_room(gID, id2)
		cls.games[gID] = Game(gID, id1, id2)
		cls.players.update(cls.games[gID].users)
		cls.threads[gID] = [eventlet.spawn(infinite, cls.games[gID].update, UPDATE_SERVER), eventlet.spawn(infinite, cls.games[gID].sendFullState, UPDATE_FULL), eventlet.spawn(infinite, cls.games[gID].sendUpdate, UPDATE_DELTA)]
		return gID

	@classmethod
	def stop(cls, gID):
		win = cls.games[gID].winner()
		socketio.emit('end', '{"winner"=' + str(win) + '}', room = gID)
		if DEBUG:
			print('Winner is ' + str(win))
		cls.kill(gID)

	@classmethod
	def kill(cls, gID):
		keys = cls.games[gID].users.keys()
		for id in keys:
			if not DEBUG:
				leave_room(gID, sid = id)
			cls.players.pop(id, None)
		if not DEBUG:
			close_room(gID)
		for thread in cls.threads[gID]:
			thread.kill()
		game = cls.games[gID]
		del cls.threads[gID]
		del cls.games[gID]
		del game
	
	@classmethod
	def join(cls, id):
		if cls.waiting == None:
			cls.waiting = id
		else:
			cls.start(cls.waiting, id)
			cls.waiting = None

	@classmethod
	def leave(cls, id):
		socketio.emit('end', '{"winner"=' + cls.games[cls.players[id].game.id].other(id) + '}', room = cls.players[id].game.id)
		cls.kill(players[id].game.id)

#Testing
gID = GameManager.start(1, 2)
game = GameManager.games[gID]
def test_print():
	if not game.isOver():
		if bool(random.getrandbits(1)):
			if bool(random.getrandbits(1)):
				game.users[random.getrandbits(1) + 1].buy('{"type":"' + random.choice(['fist', 'bow', 'sword']) + '"}')
			else:
				game.users[random.getrandbits(1) + 1].buy('{"type":"' + random.choice(['single', 'area']) + '","x":' + str(random.choice(range(0, 10))) + ',"y":' + str(random.choice(range(0, 10))) + '}')
		print('\n' + game.toStr())
		print('\n' + game.unitsToString())
		print('\n' + game.towersToString())
test_thread = eventlet.spawn(infinite, test_print, 1)
#GameManager.killAll()
while True:
	eventlet.sleep(50)