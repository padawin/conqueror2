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

		hull = None

		if end - start >= 3:
			hull1 = self.generateEdges(start, start + int((end - start) / 2))
			hull2 = self.generateEdges(start + int((end - start) / 2) + 1, end)
			# @TODO merge the 2 hulls
			hull = dict()
		elif end - start == 2:
			node1 = self.nodes[start]
			node2 = self.nodes[start + 1]
			node3 = self.nodes[start + 2]
			self.edges.addEdge(node1, node2)
			self.edges.addEdge(node2, node3)
			self.edges.addEdge(node3, node1)
			hull = self.generateHull(node1, node2, node3)
		elif end - start == 1:
			node1 = self.nodes[start]
			node2 = self.nodes[start + 1]
			self.edges.addEdge(node1, node2)
			hull = self.generateHull(node1, node2)

		return hull

	# the nodes are expected to be ordered on theiy x, then y
	def generateHull(self, node1, node2, node3=None):
		hull = convexHull()
		hull.generate(node1, node2, node3)
		return hull


class convexHull(dict):
	def generate(self, node1, node2, node3=None):
		# given a node of the hull, we can get 2 other nodes, its neighbours
		# the first neighbour is the clockwise neighbour and the second one is
		# the counter clockwise neighbour
		node1Key = convexHull.getNodeKey(node1)
		node2Key = convexHull.getNodeKey(node2)
		self[node1Key] = [node2]
		self[node2Key] = [node1]

		if node3 is not None:
			node3Key = convexHull.getNodeKey(node3)
			side = self.getSideOfNodeFromEdge([node1, node2], node3)
			# left
			if side > 0:
				self[node1Key].insert(0, node3)
				self[node2Key].append(node3)
			# right or aligned
			else:
				self[node1Key].append(node3)
				self[node2Key].insert(0, node3)

	def getSideOfNodeFromEdge(self, edge, node):
		'''
		The edge is oriented (goes from edge[0] to edge[1])
		if the result is < 0, the node is at the right of the edge
		if the result is = 0, the node and the edge are aligned
		if the result is > 0, the node is at the left of the edge
		'''
		xEdge = edge[1]['x'] - edge[0]['x']
		yEdge = edge[1]['y'] - edge[0]['y']
		xDistFromEdge = node['x'] - edge[0]['x']
		yDistFromEdge = node['y'] - edge[0]['y']
		return xEdge * yDistFromEdge - xDistFromEdge * yEdge

	@staticmethod
	def getNodeKey(node):
		return '{}-{}'.format(node['x'], node['y'])


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


class exception(BaseException):
	pass
