from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit
from collections import defaultdict
from uuid import uuid4 as uuid
import time as Timer
import eventlet
import json
import random
import math

eventlet.monkey_patch()
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
room = {}
coroutine = {}
clients = defaultdict(list)
wait_room = None

class Template:
	def __init__(self, type, price, hp, dmg, range, time):
		self.type = type
		self.price = price
		self.hp = hp
		self.dmg = dmg
		self.range = range
		self.time = time

#Constants
UPDATE_FULL = 5
UPDATE_DELTA = 0.1
UPDATE_SERVER = 0.1
ANIM_FIST = [0.25, 0.5, 0.75]
ANIM_BOW = [0.75]
ANIM_SWORD = [0.25, 0.75]
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
UNIT_SPEED = 0.05

DEBUG = True

TEMPLATES = {'single': Template('single', 100, 50, 10, 5, 100), 
			 'area': Template('area', 140, 30, 15, 8, 200), 
			 'fist': Template('fist', 20, 40, 5, 1, 50), 
			 'bow': Template('bow', 35, 30, 10, 3, 150), 
			 'sword': Template('sword', 40, 50, 15, 1.5, 100),
			 'castle': Template('castle', 0, 500, 0, 0, 0)}

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


class Utils:
	@staticmethod
	def min_by_val(dictionary):
		result = None
		for key in dictionary:
			if not result or ((key in dictionary) and (dictionary[key] < dictionary[result])):
				result = key
		return result
	
	@staticmethod
	def max_by_val(dictionary):
		result = None
		for key in dictionary:
			if not result or ((dictionary[key]) and (dictionary[key] > dictionary[result])):
				result = key
		return result
	
	@staticmethod
	def sign(x):
		if x in [None, 0.0, -0.0, 0, -0]:
			return 0
		if x > 0:
			return 1
		return -1

	@staticmethod
	def infinite(func, timeout):
		while True:
			func()
			eventlet.sleep(timeout)
		
class Unit:
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template.type
		self.hp = template.hp
		self.maxHP = self.hp
		self.dmg = template.dmg
		self.range = template.range
		self.timeout = template.time
		self.timer = template.time
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
		global UNIT_SPEED
		self.x = self.x + (dX / math.sqrt(dX ** 2 + dY ** 2)) * UNIT_SPEED
		self.y = self.y + (dY / math.sqrt(dX ** 2 + dY ** 2)) * UNIT_SPEED
	
	def update(self):
		global MINIMAL_RANGE
		if self.hp <= 0:
			self.user.units.remove(self)
			self.user.game.addToUpdate('{"type":"remove","id":' + str(self.id) + '}')
			del self
		else:
			delta = int(Timer.time() * 1000) - self.time
			self.time = self.time + delta
			self.timer = self.timer - delta
			if self.target == None:
				self.target = self.user.game.findNearestUnit(self.x, self.y, self.user.game.other(self.user.id))
				if self.target == None:
					self.target = self.user.game.users[self.user.game.other(self.user.id)].castle
			print(math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) - self.range)
			if math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.range:
				if self.timer <= 0:
					print('Hit!')
					self.target.hp = self.target.hp - self.dmg
					self.timer = self.timeout
			if not self.path:
				self.path = self.user.game.path(self.user.game.nearestPoint(self.target.x, self.target.y, self.x, self.y), self.user.game.nearestPointTo(int(self.target.x), int(self.target.y), self.x, self.y, self.range))
			if self.path and math.sqrt((self.x - self.path[0][0]) ** 2 + (self.y - self.path[0][1]) ** 2) <= MINIMAL_RANGE:
				self.x = self.path[0][0]
				self.y = self.path[0][1]
				self.path.pop(0)
			if self.path:
				self.move(self.path[0][0] - self.x, self.path[0][1] - self.y)
	
class Tower:
	def __init__(self, user, x, y, template):
		self.user = user
		self.x = x
		self.y = y
		self.type = template.type
		self.hp = template.hp
		self.maxHP = self.hp
		self.dmg = template.dmg
		self.range = template.range
		self.timeout = template.time
		self.timer = template.time
		self.time = int(Timer.time() * 1000)
		#self.state = STATE_GO
		id = uuid().int
		while id in self.user.game.usedID:
			id = uuid().int
		self.id = id
		self.user.game.usedID.append(id)
		
	def toJSON(self):
		return str(self.id) + ':{"position":{"x":' + str(self.x) + ',"y":' + str(self.y) + '},"type":"' + str(self.type) + '","hp":{"HP":' + str(self.hp) + ',"maxHP":' + str(self.maxHP) + '}}'
	
	def update(self):
		if self.hp <= 0:
			del self.game.plane[(self.x, self.y)]
			self.user.game.addToUpdate('{"type":"remove","id":' + str(self.id) + '}')
			self.user.towers.remove(self)
			del self
		else:
			delta = int(Timer.time() * 1000) - self.time
			self.time = self.time + delta
			self.timer = self.timer - delta
			if self.timer <= 0:
				target = self.user.game.findNearestUnit(self.x, self.y, self.user.game.other(self.user.id))
				if math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2) <= self.range:
					target.hp = target.hp - self.dmg
				self.timer = self.timeout

class User:
	def __init__(self, game, id, castle_x):
		global TEMPLATES
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
		global DEBUG
		if self.resources < template.price:
			return
		if DEBUG:
			print("[" + str(self.id) + "]: Let's buy a " + template.type + " unit!")
		self.game.units.append(Unit(self, self.castle.x, self.castle.y, template))
		self.resources = self.resources - template.price
		self.game.addToUpdate('{"type":"add","x":' + str(self.castle.x) + ',"y":' + str(self.castle.y) + ',"type":' + template.type + '}')
	
	def buyTower(self, x, y, template):
		if self.resources < template.price or self.game.plane[(x, y)]:
			return
		self.game.plane[(x, y)] = Tower(self, x, y, template)
		self.towers.append(self.game.plane[(x, y)])
		self.resources = self.resources - template.price
		self.game.addToUpdate('{"type":"add","x":' + str(x) + ',"y":' + str(y) + ',"type":' + template.type + '}')
	
	def buy(self, str):
		global TEMPLATES
		data = json.loads(str)
		if data and data['type']:
			if data['type'] in ['fist', 'bow', 'sword']:
				self.buyUnit(TEMPLATES[data['type']])
			elif data['type'] in ['single', 'area']:
				self.buyTower(data.x, data.y, TEMPLATES[data['type']])
	
	def sell(self, str):
		global TEMPLATES
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
		global TEMPLATES
		string = '{"id":' + str(self.id) + ',"res":' + str(self.resources) + ',"static":{'
		for tower in self.towers:
			string = string + tower.toJSON() + ','
		string = string + '"castle":{"position":{"x":' + str(self.castle.x) + ',"y":' + str(self.castle.y) + '},"type":"castle","hp":{"HP":' + str(self.castle.hp) + ',"maxHP":' + str(TEMPLATES['castle'].hp) + '}}},"dynamic":{'
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
	
	def findNearestUnit(self, x, y, id):
		len = -1
		u = None
		for unit in self.units:
			if unit.id == id and ((len == -1) or (len > math.sqrt((unit.x - x) * (unit.x - x) + (unit.y - y) * (unit.y - y)))):
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
			if pos in self.plane:
				tower = self.plane[pos]
			if tower and tower.id == id:
				del queue
				del temp
				return tower
			temp.append(pos)
			if pos[0] < self.width - 1 and not (pos[0] + 1, pos[1]) in temp:
				queue.append((pos[0] + 1, pos[1]))
			if pos[0] > 0 and not (pos[0] - 1, pos[1]) in temp:
				queue.append((pos[0] - 1, pos[1]))
			if pos[1] < self.height - 1 and not (pos[0], pos[1] + 1) in temp:
				queue.append((pos[0], pos[1] + 1))
			if pos[1] > 0 and not (pos[0], pos[1] - 1) in temp:
				queue.append((pos[0], pos[1] - 1))
		return self.users[id].castle
	
	def nearestPoint(self, targetX, targetY, x, y):
		return (int(int(x) + Utils.sign(targetX - x)), int(int(y) + Utils.sign(targetY - y)))
	
	def nearestPointTo(self, targetX, targetY, x, y, rng):
		data = {}
		for tX in range(int(targetX - rng), int(targetX + rng)):
			for tY in range(int(targetY - rng), int(targetY + rng)):
				if math.sqrt((tX - targetX) ** 2 + (tY - targetY) ** 2) <= rng:
					data[(tX, tY)] = math.sqrt((tX - x) ** 2 + (tY - y) ** 2)
		return Utils.min_by_val(data)
	
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
					num[pos] = num[Utils.min_by_val(self.near(num, pos))] + 1
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
		while not pos == pos1:
			pos = Utils.min_by_val(self.near(num, pos))
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
			str = str + unit.toJSON() + '\n'
		return str

	def sendFullState(self):
		del self.updates[:]
		socketio.emit('update-full', self.toJSON(), room = self.id)

	def toStr(self):
		s = ''
		for user in self.users.values():
			s = s + '[' + str(user.id) + ']: (' + str(user.castle.hp) + '/' + str(user.castle.maxHP) + ')\n'
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
		global DEBUG
		gID = uuid().int
		while gID in cls.games:
			gID = uuid().int
		if not DEBUG:
			join_room(gID, id1)
			join_room(gID, id2)
		cls.games[gID] = Game(gID, id1, id2)
		cls.players.update(cls.games[gID].users)
		cls.threads[gID] = [eventlet.spawn(Utils.infinite, cls.games[gID].update, UPDATE_SERVER), eventlet.spawn(Utils.infinite, cls.games[gID].sendFullState, UPDATE_FULL), eventlet.spawn(Utils.infinite, cls.games[gID].sendUpdate, UPDATE_DELTA)]
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
		global DEBUG
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
		if len(game.units) < 1 and not bool(random.getrandbits(1)):
			game.users[random.getrandbits(1) + 1].buy('{"type":"' + random.choice(['fist', 'bow', 'sword']) + '"}')
		print('\n' + game.toStr())
		print('\n' + str(game.unitsToString()))
test_thread = eventlet.spawn(Utils.infinite, test_print, 1)
#GameManager.killAll()
while True:
	eventlet.sleep(50)