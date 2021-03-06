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
			nbNodes -= 1

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
			(hull, topTangent, bottomTangent) = convexHull.merge(
				hull1, hull2,
				self.nodes[rightHull1],
				self.nodes[leftHull2]
			)

			self.edges.addEdge(topTangent[0], topTangent[1])
			self.edges.addEdge(bottomTangent[0], bottomTangent[1])
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

	@staticmethod
	def merge(hull1, hull2, rightMostHull1, leftMostHull2):
		topTangent = convexHull.findTangent(
			hull1, hull2,
			rightMostHull1, leftMostHull2,
			True
		)
		bottomTangent = convexHull.findTangent(
			hull1, hull2,
			rightMostHull1, leftMostHull2,
			False
		)

		# remove edges contained in the two tangents
		# loop clockwise from topTangent[0] to bottomTangent[0]
		hull1._clean(
			fromNode=topTangent[0],
			toNode=bottomTangent[0],
			clockwise=True
		)
		# loop counter clockwise from topTangent[1] to bottomTangent[1]
		hull2._clean(
			fromNode=topTangent[1],
			toNode=bottomTangent[1],
			clockwise=False
		)

		# merge the two hulls
		hull = convexHull(hull1.copy())
		hull.update(hull2)

		# add topTangent and bottomTangent to hull
		hull._joinNodesClockwise(topTangent[0], topTangent[1])
		hull._joinNodesClockwise(bottomTangent[1], bottomTangent[0])

		# _clean orphan nodes
		hull = convexHull({
			key: hull[key]
			for key in hull
			if len(hull[key]) == 2
		})

		return (hull, topTangent, bottomTangent)

	@staticmethod
	def findTangent(hull1, hull2, rightMostHull1, leftMostHull2, isUpperTangent):
		'''
		find a point p1 in hull1 and a point p2 in hull2 such as [p1, p2] is a
		tangent to hull1 and hull2
		'''
		callbackHull1 = hull1.isUpperTangent if isUpperTangent\
			else hull1.isLowerTangent
		callbackHull2 = hull2.isUpperTangent if isUpperTangent\
			else hull2.isLowerTangent

		# start edge, going from right most of hull1 to left most of hull2
		tangent = [rightMostHull1, leftMostHull2]
		while not callbackHull1(tangent) or not callbackHull2(tangent):
			# the hull is not at the right of the top edge
			while not callbackHull1(tangent):
				# move the left extremity of the edge counter clock wise)
				tangent[0] = hull1.getNextNode(
					tangent[0], clockwise=(not isUpperTangent)
				)

			# the hull is not at the right of the top edge
			while not callbackHull2(tangent):
				# move the left extremity of the edge clock wise
				tangent[1] = hull2.getNextNode(
					tangent[1], clockwise=isUpperTangent
				)

		return tangent

	def getNextNode(self, node, clockwise):
		key = self.getNodeKey(node)
		return self[key][0 if len(self[key]) == 1 or clockwise else 1]

	def _clean(self, fromNode, toNode, clockwise):
		'''
		It breaks a hull by removing the links between two points.
		Makes the Hull unstable and breaks its integrity
		'''
		if len(self.keys()) == 2 and fromNode is not toNode:
			return

		nodesDeleted = False
		nodeKey = convexHull.getNodeKey(fromNode)
		toNodeKey = convexHull.getNodeKey(toNode)
		while not nodesDeleted or nodeKey != toNodeKey:
			if len(self[nodeKey]) == 1:
				index = 0
				backIndex = None
			elif clockwise:
				index = 0
				backIndex = 1
			else:
				index = 1
				backIndex = 0

			nextNode = self[nodeKey][index]
			self[nodeKey][index] = None
			nodeKey = convexHull.getNodeKey(nextNode)
			if backIndex is not None:
				self[nodeKey][backIndex] = None
			nodesDeleted = True

	def _joinNodesClockwise(self, fromNode, toNode):
		fromKey = convexHull.getNodeKey(fromNode)
		toKey = convexHull.getNodeKey(toNode)

		if len(self[fromKey]) == 2:
			if self[fromKey][0] is not None and self[fromKey][0] is not toNode:
				raise exception("This node already has a clockwise neighbour")
			self[fromKey][0] = toNode
		else:
			self[fromKey].insert(0, toNode)

		if len(self[toKey]) == 2:
			if self[toKey][1] is not None and self[toKey][1] is not fromNode:
				raise exception("This node already has a counter clockwise neighbour")
			self[toKey][1] = fromNode
		else:
			self[toKey].append(fromNode)

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
