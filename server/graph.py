import random
import operator
import json
import collections


class graph:
	def __init__(self):
		self.nodes = []
		self.nodesGrid = []
		self.edges = edgeList()

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
