import uuid
import random
import config

MAX_PLAYER_PER_GAME = 2


def createGame(player, graph):
	gameInstance = game(graph)
	gameInstance.graph.generateNodes(
		config.nbNodes, config.mapWidth, config.mapHeight,
		lambda: {'owned_by': None}
	)
	gameInstance.graph.generateEdges()
	gameInstance.addPlayer(player)
	return gameInstance


class game:
	def __init__(self, graph):
		self.id = uuid.uuid4()
		self.graph = graph
		self.players = {}
		self.playerIds = []

	def getSerializedGraph(self):
		return {
			'nodes': self.graph.nodes,
			'nodesGrid': self.graph.nodesGrid,
			'edges': self.graph.edges
		}

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
		nodes = list(self.graph.nodes)
		random.shuffle(nodes)
		for index, playerId in enumerate(self.playerIds):
			node = nodes.pop(0)
			self.graph.getNode(node['x'], node['y'])['owned_by'] = index

	def definePlayersOrder(self):
		random.shuffle(self.playerIds)
		self.currentPlayer = 0
		return self.playerIds

	def endTurn(self):
		self.notifyPlayerEndTurn()
		self.currentPlayer = (self.currentPlayer + 1) % len(self.playerIds)
		self.notifyNextPlayerTurn()

	def notifyPlayerEndTurn(self):
		self.players[self.playerIds[self.currentPlayer]].write_message(
			{
				'type': 'PLAYER_TURN_FINISHED',
				'message': u'Turn finished'
			}
		)

	def notifyNextPlayerTurn(self):
		self.players[self.playerIds[self.currentPlayer]].write_message(
			{
				'type': 'PLAYER_TURN',
				'message': u'Your turn to start'
			}
		)

	def conquerNode(self, node, playerIndex):
		neighbours = self.graph.edges.getEdgesFromNode(node)
		nbAlliedNeighbours = 0
		nbEnemyNeighbours = 0
		for n in neighbours:
			neighbour = self.graph.nodesGrid[n['x']][n['y']]
			if neighbour['owned_by'] is not None:
				if neighbour['owned_by'] == playerIndex:
					nbAlliedNeighbours += 1
				else:
					nbEnemyNeighbours += 1

		if nbEnemyNeighbours >= nbAlliedNeighbours:
			return False
		else:
			self.graph.getNode(node['x'], node['y'])['owned_by'] = playerIndex
			return True

	def notifyPlayers(self, emitter=None, message=None):
		players = self.players
		for playerId in players.keys():
			if emitter is None or players[playerId].id is not emitter.id:
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
