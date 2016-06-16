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
			rightHull1 = start + int((end - start) / 2)
			leftHull2 = start + int((end - start) / 2) + 1
			hull1 = self.generateEdges(start, rightHull1)
			hull2 = self.generateEdges(leftHull2, end)
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
			side = convexHull.getSideOfNodeFromEdge([node1, node2], node3)
			# left
			if side > 0:
				self[node1Key].insert(0, node3)
				self[node2Key].append(node3)
				self[node3Key] = [node2, node1]
			# right or aligned
			else:
				self[node1Key].append(node3)
				self[node2Key].insert(0, node3)
				self[node3Key] = [node1, node2]

	@staticmethod
	def getSideOfNodeFromEdge(edge, node):
		'''
		The edge is oriented (goes from edge[0] to edge[1])
		if the result is < 0, the node is at the right of the edge
		if the result is = 0, the node and the edge are aligned
		if the result is > 0, the node is at the left of the edge
		'''
		# canvas's y starts at the top, we then need to multiply the y
		# to -1 to invert it
		xEdge = edge[1]['x'] - edge[0]['x']
		yEdge = -1 * (edge[1]['y'] - edge[0]['y'])
		xDistFromEdge = node['x'] - edge[0]['x']
		yDistFromEdge = -1 * (node['y'] - edge[0]['y'])
		return xEdge * yDistFromEdge - xDistFromEdge * yEdge

	@staticmethod
	def getNodeKey(node):
		return '{}-{}'.format(node['x'], node['y'])

	def getNextNode(self, node, clockwise):
		key = self.getNodeKey(node)
		return self[key][0 if len(self[key]) == 1 or clockwise else 1]

	def isLowerTangent(self, edge):
		'''
		Means the hull is at the left of the edge
		'''
		tangent = self.isTangent(edge)
		return tangent is not None and tangent == 1

	def isUpperTangent(self, edge):
		'''
		Means the hull is at the right of the edge
		'''
		tangent = self.isTangent(edge)
		return tangent is not None and tangent == -1

	def isTangent(self, edge):
		'''
		Returns None if none of the edge's extremities belong to the hull
		Returns 0 if the edge is not a tangent to the hull
		Returns -1 if the edge is a tangent and the hull is at the right of the edge
		Returns 1 if the edge is a tangent and the hull is at the left of the edge
		'''

		node1Key = self.getNodeKey(edge[0])
		node2Key = self.getNodeKey(edge[1])
		# figure out which node of the edge is in the hull
		# left most edge is in hull
		if node1Key in self:
			nodeKey = node1Key
		# right most edge is in hull
		elif node2Key in self:
			nodeKey = node2Key
		else:
			return None

		# test the 2 neighbours
		sideNeighbourCW = convexHull.getSideOfNodeFromEdge(edge, self[nodeKey][0])
		# get the sign of the value
		sideNeighbourCW = (sideNeighbourCW > 0) - (sideNeighbourCW < 0)

		sideNeighbourCCW = None
		if len(self[nodeKey]) == 2:
			sideNeighbourCCW = convexHull.getSideOfNodeFromEdge(
				edge, self[nodeKey][1]
			)
			sideNeighbourCCW = (sideNeighbourCCW > 0) - (sideNeighbourCCW < 0)

		# edge aligned with the clockwork edge of the node
		if sideNeighbourCW == 0:
			if sideNeighbourCCW is None:
				# the hull has one edge, and the side is 0 -> the hull's edge
				# and the tested edge are parallel. Return an arbitrary tangent
				# value
				return 1
			else:
				# The edge is aligned with the node's clockwise edge. Rely on
				# the node's counter clock wise edge
				return sideNeighbourCCW
		# one-edge hull not aligned with the edge, or hull with both edges at
		# the same side of the edge, or edge aligned with the counter clockwise
		# neighbour edge of the node
		elif not sideNeighbourCCW or sideNeighbourCCW == sideNeighbourCW:
			return sideNeighbourCW
		# neighbour edges on each sides of the edge
		else:
			return 0


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
