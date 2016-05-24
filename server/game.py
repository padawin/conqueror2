import random
import operator
import uuid
import json
import collections

import config

MAX_PLAYER_PER_GAME = 2

class game:
	def __init__(self):
		self.id = uuid.uuid4()
		self.nodes = []
		self.nodesGrid = []
		self.edges = edgeList()
		self.players = {}
		self.playerIds = []

	def addPlayer(self, player):
		if not self.hasFreeSlot():
			raise OverflowError()
		self.players[player.id] = player

	def hasFreeSlot(self):
		return len(self.players) < MAX_PLAYER_PER_GAME

	def deletePlayer(self, player):
		del self.players[player.id]

	def hasPlayers(self):
		return len(self.players) > 0

	def initialisePlayers(self):
		self.playerIds = self.players.keys()

		# Define the start position of each player
		nodes = list(self.nodes)
		random.shuffle(nodes)
		for index, playerId in enumerate(self.playerIds):
			node = nodes.pop(0)
			self.nodesGrid[node['x']][node['y']]['owned_by'] = index

	def definePlayersOrder(self):
		random.shuffle(self.playerIds)
		self.currentPlayer = 0
		return self.playerIds

	def notifyNextPlayerTurn(self):
		self.players[self.playerIds[self.currentPlayer]].write_message(
			{
				'type': 'PLAYER_TURN',
				'message': u'Your turn to start'
			}
		)

	def conquerNode(self, node, playerIndex):
		neighbours = self.edges.getEdgesFromNode(node)
		nbAlliedNeighbours = 0
		nbEnemyNeighbours = 0
		for n in neighbours:
			neighbour = self.nodesGrid[n['x']][n['y']]
			if neighbour['owned_by'] is not None:
				if neighbour['owned_by'] == playerIndex:
					nbAlliedNeighbours += 1
				else:
					nbEnemyNeighbours += 1

		if nbEnemyNeighbours >= nbAlliedNeighbours:
			return False
		else:
			self.nodesGrid[node['x']][node['y']]['owned_by'] = playerIndex
			return True

	def generateNodes(self, nbNodes, maxWidth, maxHeight):
		self.nodesGrid = [
			[None for x in range(maxWidth)] for y in range(maxHeight)
		]
		while nbNodes > 0:
			x = random.randint(0, maxWidth - 1)
			y = random.randint(0, maxHeight - 1)

			self.nodesGrid[x][y] = {'owned_by': None}
			node = collections.OrderedDict()
			node['x'] = x
			node['y'] = y
			self.nodes.append(node)
			nbNodes -= 1;

		self.nodes = sorted(self.nodes, key=operator.itemgetter('x', 'y'))

	def generateEdges(self, start=0, end=None):
		if end is None:
			end = len(self.nodes) - 1

		if end - start >= 3:
			self.generateEdges(start, start + (end - start) / 2)
			self.generateEdges(start + (end - start) / 2 + 1, end)
		elif end - start == 2:
			self.edges.addEdge([self.nodes[start], self.nodes[start + 1]])
			self.edges.addEdge([self.nodes[start + 1], self.nodes[start + 2]])
			self.edges.addEdge([self.nodes[start + 2], self.nodes[start]])
		else:
			self.edges.addEdge([self.nodes[start], self.nodes[start + 1]])

	def notifyPlayers(self, emitter = None, message = None):
		players = self.players
		for playerId in players.keys():
			if emitter is None or players[playerId].id is not emitter.id:
				players[playerId].write_message(message)

class edgeList(dict):
	def addEdge(self, edge):
		keyStart = json.dumps(edge[0], separators=(',', ':'))
		keyEnd = json.dumps(edge[1], separators=(',', ':'))
		if keyStart not in self:
			self[keyStart] = []

		if keyEnd not in self:
			self[keyEnd] = []

		self[keyStart].append(edge[1])
		self[keyEnd].append(edge[0])

	def getEdgesFromNode(self, node):
		tmp = collections.OrderedDict()
		tmp['x'] = node['x']
		tmp['y'] = node['y']
		key = json.dumps(tmp, separators=(',', ':'))
		return self[key]

class collection(dict):
	def __init__(self):
		super(collection, self).__init__()

	def deleteGame(self, gameInstance):
		del self[gameInstance.id]

	def addGame(self, gameInstance):
		self[gameInstance.id] = gameInstance

	def getGame(self, gameId=None):
		# return the first available
		if gameId is None:
			return self[self.keys()[0]]
		else:
			return self[gameId]

	def createGame(self, player):
		gameInstance = game()
		gameInstance.generateNodes(
			config.nbNodes, config.mapWidth, config.mapHeight
		)
		gameInstance.generateEdges()
		gameInstance.addPlayer(player)
		self[gameInstance.id] = gameInstance
		return gameInstance
