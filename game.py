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
UPDATE_FULL = 5000
UPDATE_DELTA = 100
UPDATE_SERVER = 50
ANIM_FIST = [0.25, 0.5, 0.75]
ANIM_BOW = [0.75]
ANIM_SWORD = [0.25, 0.75]
CASTLE_X = 1
PLANE_HEIGHT = 10
PLANE_WIDTH = 10
PRICE_BOW = 35
PRICE_FIST = 20
PRICE_SWORD = 40
PRICE_SINGLE = 100
PRICE_AREA = 140
#PRICE_PSY = 200
RESOURCES_PER_SECOND = 40
STATE_ATTACK = 'ATTACK'
STATE_DIE = 'DIE'
STATE_GO = 'GO'
TOWER_SINGLE = Template('single', 50, 10, 5, 100)
TOWER_AREA = Template('area', 30, 15, 8, 200)
#TOWER_PSY = Template('psy', 20, 15, 9, 150)
UNIT_SPEED = 0.5
UNIT_FIST = Template('fist', 40, 5, 1, 50)
UNIT_BOW = Template('bow', 30, 10, 6, 150)
UNIT_SWORD = Template('sword', 50, 15, 1.5, 100)
USER_HP = 500

class Utils:
	def min(*args):
		

class Template:
	def __init__(self, type, hp, dmg, range, time):
		self.type = template.type
		self.hp = template.hp
		self.dmg = template.dmg
		self.range = template.range
		self.time = time

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
		self.timeout = time
		self.time = time
		#self.state = STATE_GO
		
	def toJSON(self):
		return '{"position":{"x":' + self.x + ',"y":' + self.y + '},"type":"' + self.type + '","hp":{"HP":' + self.hp + ',"maxHP":' + self.maxHP + '}}'
		
	def update(self):
		delta = Timer.time() * 1000 - self.time
		self.time = self.time + delta
		u = self.user.game.findNearestUnit()
		

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
		self.time = time
		self.state = STATE_GO
		
	def toJSON(self):
		return '{"position":{"x":' + self.x + ',"y":' + self.y + '},"type":"' + self.type + '","hp":{"HP":' + self.hp + ',"maxHP":' + self.maxHP + '}}'
		
	def update(self, delta):
		

class User:
	def __init__(self, game, id, castle_x):
		self.game = game
		self.id = id
		self.resources = 0
		self.x = castle_x
		self.y = (PLANE_HEIGHT - 1) / 2
		self.hp = USER_HP
		self.towers = []
		
	def update(self, delta):
		self.resources = self.resources + RESOURCES_PER_SECOND * delta / 1000
		
	def toJSON(self):
		str = '{"id":' + self.id + ',"res":' + self.resources + ',"static":['
		for tower in self.towers:
			str = str + tower.toJSON() + ','
		str = str + '],"dynamic":['
		for unit in self.game.units:
			if unit.id == id:
				str = str + unit.toJSON() + ','
		return str + '],"castle":{"position":{"x":' + self.x + ',"y":' + self.y + '},"type":"castle","hp":{"HP":' + self.hp + ',"maxHP":' + USER_HP + '}}}'
		
class Game:
	def __init__(self, id, id1, id2):
		self.id = id
		self.users = {}
		self.users[id1] = User(self, id1, CASTLE_X)
		self.users[id2] = User(self, id2, PLANE_WIDTH - CASTLE_X - 1)
		self.width = PLANE_WIDTH
		self.height = PLANE_WIDTH
		self.time = Timer.time() * 1000
		self.units = []
		self.updates = []
		self.plane = {}
		
	def other(self, id):
		u = []
		for user in self.users:
			u.append(user)
		if u[0].id == id:
			return u[1].id
		else:
			return u[0].id
	
	def update(self):
		delta = Timer.time() * 1000 - self.time
		self.time = self.time + delta
		for unit in self.units:
			unit.update(delta)
		for user in self.users:
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
	
	def path(self, x1, y1, x2, y2):
		queue = [(x1, y1)]
		temp = []
		num = {queue[0]: 0}
		while queue:
			pos = queue[0]
			queue.remove(pos)
			if pos == (x2, y2):
				break
			elif pos in temp:
				continue
			else:
				temp.append(pos)
				if not pos in num:
					n = None
					if (pos[0] + 1, pos[1]) in temp:
						n = num[(pos[0] + 1, pos[1])]
					if (pos[0], pos[1] + 1) in temp:
						n = 
					if (pos[0] - 1, pos[1]) in temp:
						
					if (pos[0], pos[1] - 1) in temp:
						
				
	
	def winner(self):
		for user in self.users:
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
		for user in self.users:
			socketio.emit('update-delta', json, user.id)
		del self.updates[:]
		eventlet.sleep(UPDATE_DELTA)
	
	def toJSON(self):
		str = '{"players":['
		for user in self.users:
			str = str + user.toJSON() + ','
		return str + ']}'
	
	def sendFullState(self):
		del self.updates[:]
		for user in self.users:
			socketio.emit('update-full', self.toJSON(), user.id)
		eventlet.sleep(UPDATE_FULL)
	
class GameManager:
	games = {}
	threads = {}

	def start(id1, id2):
		gID = uuid().int
		while games[gID]:
			gID = uuid().int
		games[gID] = Game(gID, id1, id2)
		threads[gID] = [eventlet.spawn(games[gID].update), eventlet.spawn(games[gID].sendFullState), eventlet.spawn(games[gID].sendUpdate)]
	
	def stop(gID):
		win = winner(gID)
		lose = games[gID].other(win)
		socketio.emit('win', '{}', win)
		socketio.emit('lose', '{}', lose)
		kill(gID)
	
	def kill(gID):
		for thread in threads[gID]:
			thread.kill()
		del threads[gID]
		del games[gID]