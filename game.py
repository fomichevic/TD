from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit
from collections import defaultdict
from uuid import uuid4 as uuid
import time as Timer
import eventlet
import json

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
UPDATE_FULL = 5000
UPDATE_DELTA = 100
UPDATE_SERVER = 50
ANIM_FIST = [0.25, 0.5, 0.75]
ANIM_BOW = [0.75]
ANIM_SWORD = [0.25, 0.75]
CASTLE_X = 1
MINIMAL_RANGE = 0.1
PLANE_HEIGHT = 10
PLANE_WIDTH = 10
#PRICE_PSY = 200
RESOURCES_PER_SECOND = 40
STATE_ATTACK = 'ATTACK'
STATE_DIE = 'DIE'
STATE_GO = 'GO'
#TOWER_PSY = Template('psy', 20, 15, 9, 150)
UNIT_SPEED = 0.5
USER_HP = 500

TEMPLATES = {'single': Template('single', 100, 50, 10, 5, 100), 
			 'area': Template('area', 140, 30, 15, 8, 200), 
			 'fist': Template('fist', 20, 40, 5, 1, 50), 
			 'bow': Template('bow', 35, 30, 10, 6, 150), 
			 'sword': Template('sword', 40, 50, 15, 1.5, 100)}

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
    return render_template('chat.html', async_mode=socketio.async_mode)


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
		self.HP = template.hp
		self.maxHP = self.HP
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
		return self.id + ':{"position":{"x":' + self.x + ',"y":' + self.y + '},"type":"' + self.type + '","hp":{"HP":' + self.hp + ',"maxHP":' + self.maxHP + '}}'

	def move(self, dX, dY):
		global UNIT_SPEED
		self.x = self.x + (dX / math.sqrt(dX ** 2 + dY ** 2)) * UNIT_SPEED
		self.y = self.y + (dY / math.sqrt(dX ** 2 + dY ** 2)) * UNIT_SPEED
	
	def update(self):
		global MINIMAL_RANGE
		if self.hp <= 0:
			self.user.units.remove(self)
			self.user.game.addToUpdate('{"type":"remove","id":' + self.id + '}')
			del self
		else:
			delta = int(Timer.time() * 1000) - self.time
			self.time = self.time + delta
			self.timer = self.timer - delta
			target = self.user.game.findNearestUnit(self.x, self.y, self.user.game.other(self.user.id))
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
		return self.id + ':{"position":{"x":' + self.x + ',"y":' + self.y + '},"type":"' + self.type + '","hp":{"HP":' + self.hp + ',"maxHP":' + self.maxHP + '}}'
	
	def update(self):
		if self.hp <= 0:
			del self.game.plane[(self.x, self.y)]
			self.user.game.addToUpdate('{"type":"remove","id":' + self.id + '}')
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
		self.game = game
		self.id = id
		self.resources = 0
		self.x = castle_x
		self.y = (PLANE_HEIGHT - 1) / 2
		self.hp = USER_HP
		self.towers = []
		
	def update(self):
		self.resources = self.resources + RESOURCES_PER_SECOND * delta / 1000
	
	def buyUnit(self, template):
		if self.resources < template.price:
			return
		self.game.units.append(Unit(self, self.x, self.y, template))
		self.resources = self.resources - template.price
		self.game.addToUpdate('{"type":"add","x":' + self.x + ',"y":' + self.y + ',"type":' + template.type + '}')
	
	def buyTower(self, x, y, template):
		if self.resources < template.price or self.game.plane[(x, y)]:
			return
		self.game.plane[(x, y)] = Tower(self, x, y, template)
		self.towers.append(self.game.plane[(x, y)])
		self.resources = self.resources - template.price
		self.game.addToUpdate('{"type":"add","x":' + x + ',"y":' + y + ',"type":' + template.type + '}')
	
	def buy(self, str):
		global TEMPLATES
		data = json.loads(str)
		if data and data.type:
			if data.type in ['fist', 'bow', 'sword']:
				self.buyUnit(TEMPLATES[data.type])
			elif data.type in ['single', 'area']:
				self.buyTower(data.x, data.y, TEMPLATES[data.type])
	
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
		self.game.addToUpdate('{"type":"remove","id":' + self.id + '}')
	
	def toJSON(self):
		str = '{"id":' + self.id + ',"res":' + self.resources + ',"static":{'
		for tower in self.towers:
			str = str + tower.toJSON() + ','
		str = str + '"castle":{"position":{"x":' + self.x + ',"y":' + self.y + '},"type":"castle","hp":{"HP":' + self.hp + ',"maxHP":' + USER_HP + '}}},"dynamic":{'
		for unit in self.game.units:
			if unit.id == id:
				str = str + unit.toJSON() + ','
		return str + '}}'
	
class Game:
	usedID = []
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
	
	def other(self, id):
		u = []
		for user in self.users.values():
			u.append(user)
		if u[0].id == id:
			return u[1].id
		else:
			return u[0].id
	
	def update(self):
		delta = int(Timer.time() * 1000) - self.time
		self.time = self.time + delta
		for unit in self.units:
			unit.update(delta)
		for user in self.users.values():
			for tower in user.towers:
				tower.update(delta)
		if winner():
			GameManager.stop(self.id)
		eventlet.sleep(UPDATE_SERVER)
	
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
			tower = self.plane[pos]
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
		json = self.deltasToJSON()
		socketio.emit('update-delta', json, room = gID)
		del self.updates[:]
		eventlet.sleep(UPDATE_DELTA)
	
	def toJSON(self):
		str = '{"players":['
		for user in self.users.values():
			str = str + user.toJSON() + ','
		return str + ']}'
	
	def sendFullState(self):
		del self.updates[:]
		socketio.emit('update-full', self.toJSON(), room = gID)
		eventlet.sleep(UPDATE_FULL)
	
class GameManager:
	games = {}
	threads = {}
	players = {}
	waiting = None
	
	def killAll(): # Do not use!
		for key in games.keys():
			kill(key)
	
	def start(id1, id2):
		gID = uuid().int
		while games[gID]:
			gID = uuid().int
		join_room(gID, id1)
		join_room(gID, id2)
		games[gID] = Game(gID, id1, id2)
		players.update(games[gID].users)
		threads[gID] = [eventlet.spawn(games[gID].update), eventlet.spawn(games[gID].sendFullState), eventlet.spawn(games[gID].sendUpdate)]
	
	def stop(gID):
		win = games[gID].winner()
		socketio.emit('end', '{"winner"=' + win + '}', room = gID)
		kill(gID)
	
	def kill(gID):
		for id in games[gID].users.keys():
			leave_room(gID, sid = id)
			players.pop(id, None)
		close_room(gID)
		for thread in threads[gID]:
			thread.kill()
		del threads[gID]
		del games[gID]
		
	def join(id):
		if waiting == None:
			waiting = id
		else:
			start(waiting, id)
			waiting = None
	
	def leave(id):
		socketio.emit('end', '{"winner"=' + games[players[id].game.id].other(id) + '}', room = players[id].game.id)
		kill(players[id].game.id)
		
	