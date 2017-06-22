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
UPDATE_SERVER = 0.05
ANIM_FIST = [0.25, 0.5, 0.75]
ANIM_BOW = [0.75]
ANIM_SWORD = [0.25, 0.75]
CASTLE_X = 1
MINIMAL_RANGE = 0.1
PLANE_HEIGHT = 10
PLANE_WIDTH = 10
#PRICE_PSY = 200
RESOURCES_PER_SECOND = 20
STATE_ATTACK = 'ATTACK'
STATE_DIE = 'DIE'
STATE_GO = 'GO'
#TOWER_PSY = Template('psy', 20, 15, 9, 150)
UNIT_SPEED = 0.5

DEBUG = True

TEMPLATES = {'single': Template('single', 100, 50, 10, 5, 100), 
			 'area': Template('area', 140, 30, 15, 8, 200), 
			 'fist': Template('fist', 20, 40, 5, 1, 50), 
			 'bow': Template('bow', 35, 30, 10, 6, 150), 
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
	def min_by_val(**kwargs):
		result = None
		for key in kwargs:
			if not result or (kwargs[key]) and (kwargs[result] < kwargs[key]):
				result = key
		return result

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
		return self.id + ':{"position":{"x":' + str(self.x) + ',"y":' + str(self.y) + '},"type":"' + self.type + '","hp":{"HP":' + str(self.hp) + ',"maxHP":' + str(self.maxHP) + '}}'

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
			target = self.user.game.findNearestUnit(self.x, self.y, self.user.game.other(self.user.id))
			if target == None:
				target = self.user.game.findNearestTower(int(self.x), int(self.y), self.user.game.other(self.user.id))
			if math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2) <= range:
				if self.timer <= 0:
					target.hp = target.hp - self.dmg
					self.timer = selt.timeout
			else:
				if not path:
					path = self.user.game.path(self.user.game.nearestPoint(target.x, target.y, self.x, self.y), self.user.game.nearestPointTo(target.x, target.y, self.x, self.y, self.range))
				if math.sqrt((self.x - path[0][0]) ** 2, (self.y - path[0][1]) ** 2) <= MINIMAL_RANGE:
					path.pop(0, None)
				if path:
					self.move(path[0][0] - self.x, path[0][1] - self.y)
	
class Tower:
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
		self.timer = time
		self.time = time
		#self.state = STATE_GO
		id = uuid().int
		while id in self.user.game.usedID:
			id = uuid().int
		self.id = id
		self.user.game.usedID.append(id)
		
	def toJSON(self):
		return self.id + ':{"position":{"x":' + str(self.x) + ',"y":' + str(self.y) + '},"type":"' + str(self.type) + '","hp":{"HP":' + str(self.hp) + ',"maxHP":' + str(self.maxHP) + '}}'
	
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
				if math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2) <= range:
					target.hp = target.hp - self.dmg
				self.timer = self.timeout

class User:
	def __init__(self, game, id, castle_x):
		global TEMPLATES
		self.game = game
		self.id = id
		self.resources = 0
		self.towers = []
		self.time = Timer.time() * 1000
		self.castle = Tower(self, castle_x, (PLANE_HEIGHT - 1) / 2, TEMPLATES['castle'])
		
	def update(self):
		delta = Timer.time() * 1000 - self.time
		self.time = self.time + delta
		self.resources = int(self.resources + RESOURCES_PER_SECOND * delta / 1000)
	
	def buyUnit(self, template):
		if self.resources < template.price:
			return
		self.game.units.append(Unit(self, self.x, self.y, template))
		self.resources = self.resources - template.price
		self.game.addToUpdate('{"type":"add","x":' + str(self.x) + ',"y":' + str(self.y) + ',"type":' + template.type + '}')
	
	def buyTower(self, x, y, template):
		if self.resources < template.price or self.game.plane[(x, y)]:
			return
		self.game.plane[(x, y)] = Tower(self, x, y, template)
		self.towers.append(self.game.plane[(x, y)])
		self.resources = self.resources - template.price
		self.game.addToUpdate('{"type":"add","x":' + str(x) + ',"y":' + str(y) + ',"type":' + template.type + '}')
	
	def buy(self, str):
		global TEMPLATES, DEBUG
		data = json.loads(str)
		if DEBUG:
			print(data)
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
		global USER_HP
		string = '{"id":' + str(self.id) + ',"res":' + str(self.resources) + ',"static":{'
		for tower in self.towers:
			string = string + tower.toJSON() + ','
		string = string + '"castle":{"position":{"x":' + str(self.x) + ',"y":' + str(self.y) + '},"type":"castle","hp":{"HP":' + str(self.hp) + ',"maxHP":' + str(USER_HP) + '}}},"dynamic":{'
		for unit in self.game.units:
			if unit.id == id:
				string = string + unit.toJSON() + ','
		return string + '}}'
	
class Game:
	def __init__(self, id, id1, id2):
		self.id = id
		self.users = {}
		self.users[id1] = User(self, id1, CASTLE_X)
		self.users[id2] = User(self, id2, PLANE_WIDTH - CASTLE_X - 1)
		self.width = PLANE_WIDTH
		self.height = PLANE_WIDTH
		self.time = int(Timer.time() * 1000)
		self.units = []
		self.updates = []
		self.plane = {}
		self.usedID = []
	
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
		eventlet.sleep(UPDATE_SERVER)
		self.update()
	
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
		return users[id].castle
	
	def nearestPoint(self, targetX, targetY, x, y):
		return (int(int(x) + sign(targetX - x)), int(int(y) + sign(targetY - y)))
	
	def nearestPointTo(self, targetX, targetY, x, y, range):
		data = {}
		for tX in range(targetX - range, targetX + range):
			for tY in range(targetY - range, targetY + range):
				if math.sqrt((tX - x) ** 2 + (tY - y) ** 2) <= range:
					data[(tX, tY)] = math.sqrt((tX - x) ** 2 + (tY - y) ** 2)
		return Utils.min_by_val(data)
	
	def path(self, pos1, pos2):
		queue = [pos1]
		temp = []
		num = {queue[0]: 0}
		while queue:
			pos = queue[0]
			queue.remove(pos)
			if pos == pos2:
				break
			elif self.plane[pos]:
				continue
			else:
				temp.append(pos)
				if not pos in num:
					num[pos] = num[Utils.min_by_val({(pos[0] + 1, pos[1]): num[(pos[0] + 1, pos[1])], (pos[0], pos[1] + 1): num[(pos[0], pos[1] + 1)], (pos[0] - 1, pos[1]): num[(pos[0] - 1, pos[1])], (pos[0], pos[1] - 1): num[(pos[0], pos[1] - 1)]})] + 1
				if pos[0] < width - 1 and not (pos[0] + 1, pos[1]) in temp:
					queue.append((pos[0] + 1, pos[1]))
				if pos[0] > 0 and not (pos[0] - 1, pos[1]) in temp:
					queue.append((pos[0] - 1, pos[1]))
				if pos[1] < height - 1 and not (pos[0], pos[1] + 1) in temp:
					queue.append((pos[0], pos[1] + 1))
				if pos[1] > 0 and not (pos[0], pos[1] - 1) in temp:
					queue.append((pos[0], pos[1] - 1))
		data = []
		pos = pos2
		while not pos == pos1:
			pos = Utils.min_by_val({(pos[0] + 1, pos[1]): num[(pos[0] + 1, pos[1])], (pos[0], pos[1] + 1): num[(pos[0], pos[1] + 1)], (pos[0] - 1, pos[1]): num[(pos[0] - 1, pos[1])], (pos[0], pos[1] - 1): num[(pos[0], pos[1] - 1)]})
			data.insert(0, pos)
		data.insert(0, pos1)
		return data
	
	def winner(self):
		for user in self.users.values():
			if user.hp <= 0:
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
		eventlet.sleep(UPDATE_DELTA)
		self.sendUpdate()
	
	def toJSON(self):
		str = '{"players":['
		for user in self.users.values():
			str = str + user.toJSON() + ','
		return str + ']}'
	
	def sendFullState(self):
		del self.updates[:]
		socketio.emit('update-full', self.toJSON(), room = self.id)
		eventlet.sleep(UPDATE_FULL)
		self.sendFullState()
	
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
		cls.threads[gID] = [eventlet.spawn(cls.games[gID].update), eventlet.spawn(cls.games[gID].sendFullState), eventlet.spawn(cls.games[gID].sendUpdate)]
		return gID
	
	@classmethod
	def stop(cls, gID):
		win = cls.games[gID].winner()
		socketio.emit('end', '{"winner"=' + win + '}', room = gID)
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
		del cls.threads[gID]
		del cls.games[gID]
		
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
print(gID)
game = GameManager.games[gID]
def test_print():
	global game
	if not bool(random.getrandbits(1)):
		game.users[random.getrandbits(1) + 1].buy('{"type":"' + random.choice(['fist', 'bow', 'sword']) + '"}')
	print(game.toJSON())
	eventlet.sleep(1)
	test_print()
test_thread = eventlet.spawn(test_print)
#GameManager.killAll()
while True:
	eventlet.sleep(0.5)