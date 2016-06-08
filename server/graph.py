import random
import operator
import json
import collections


class graph:
	def __init__(self):
		self.nodes = []
		self.nodesGrid = []
		self.edges = edgeList()

	def getNode(self, x, y):
		return self.nodesGrid[x][y]

	def generateNodes(self, nbNodes, maxWidth, maxHeight, nodeProcedure):
		self.nodesGrid = [
			[None for x in range(maxWidth)] for y in range(maxHeight)
		]
		rows = [i for i in range(maxHeight)]
		cols = [i for i in range(maxWidth)]
		random.shuffle(rows)
		random.shuffle(cols)
		while nbNodes > 0:
			index = nbNodes - 1
			x = cols[index]
			y = rows[index]
			self.nodesGrid[x][y] = nodeProcedure()
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
			self.edges.addEdge(self.nodes[start], self.nodes[start + 1])
			self.edges.addEdge(self.nodes[start + 1], self.nodes[start + 2])
			self.edges.addEdge(self.nodes[start + 2], self.nodes[start])
		else:
			self.edges.addEdge(self.nodes[start], self.nodes[start + 1])

class edgeList(dict):
	def addEdge(self, start, end):
		keyStart = edgeList.getNodeKey(start)
		keyEnd = edgeList.getNodeKey(end)
		if keyStart not in self:
			self[keyStart] = []

		if keyEnd not in self:
			self[keyEnd] = []

		self[keyStart].append(end)
		self[keyEnd].append(start)

		self.orderNodes(keyStart)
		self.orderNodes(keyEnd)

	def getEdgesFromNode(self, node):
		key = edgeList.getNodeKey(node)
		return self[key]

	def orderNodes(self, index):
		self[index] = sorted(self[index], key=operator.itemgetter('x', 'y'))

	@staticmethod
	def getNodeKey(node):
		tmp = collections.OrderedDict()
		tmp['x'] = node['x']
		tmp['y'] = node['y']
		return json.dumps(tmp, separators=(',', ':'))
