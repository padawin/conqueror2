import random
import operator
import uuid

import config

MAX_PLAYER_PER_GAME = 2

class game:
	def __init__(self):
		self.id = uuid.uuid4()
		self.nodes = []
		self.edges = []
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

	def defineFirstPlayer(self):
		self.playerIds = self.players.keys()
		random.shuffle(self.playerIds)
		self.currentPlayer = 0
		return self.players[self.playerIds[self.currentPlayer]]

	def generateNodes (self, nbNodes, maxWidth, maxHeight):
		while nbNodes > 0:
			self.nodes.append({
				'x': random.randint(0, maxWidth - 1),
				'y': random.randint(0, maxHeight - 1)
			})
			nbNodes -= 1;

		self.nodes = sorted(self.nodes, key=operator.itemgetter('x', 'y'))

	def generateEdges(self, start=0, end=None):
		if end is None:
			end = len(self.nodes) - 1

		if end - start >= 3:
			edges = self.generateEdges(start, start + (end - start) / 2)
			edges.extend(self.generateEdges(start + (end - start) / 2 + 1, end))
			return edges
		elif end - start == 2:
			return [
				[self.nodes[start], self.nodes[start + 1]],
				[self.nodes[start + 1], self.nodes[start + 2]],
				[self.nodes[start + 2], self.nodes[start]]
			]
		else:
			return [[self.nodes[start], self.nodes[start + 1]]]

	def notifyPlayers(self, emitter, message):
		players = self.players
		for playerId in players.keys():
			if players[playerId].id is not emitter.id:
				players[playerId].write_message(message)


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
