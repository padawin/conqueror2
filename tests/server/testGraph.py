# -*- coding: utf-8 -*-
import unittest

from server import graph
import tests.common
from collections import OrderedDict


class graphTests(tests.common.common):
	def test_nodes_generation(self):
		graphWidth = 5
		graphHeight = 5
		nodesNumber = 5
		g = graph.graph()
		g.generateNodes(
			nodesNumber,
			graphWidth,
			graphHeight,
			lambda: {'owned_by': None}
		)

		self.assertEquals(len(g.nodes), nodesNumber)
		nbNone = 0
		nbNodes = 0
		for row in g.nodesGrid:
			for node in row:
				if node is None:
					nbNone += 1
				else:
					self.assertEquals(node, {'owned_by': None})
					nbNodes += 1

		self.assertEquals(nbNone, graphWidth * graphHeight - nodesNumber)
		self.assertEquals(nbNodes, nodesNumber)

	def test_getNode(self):
		g = graph.graph()
		g.nodes = [
			OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 1), ('y', 1)]),
			OrderedDict([('x', 2), ('y', 3)]), OrderedDict([('x', 3), ('y', 2)]),
			OrderedDict([('x', 4), ('y', 0)])
		]
		g.nodesGrid = [
			[None, None, None, None, {'owned_by': None}],
			[None, {'owned_by': None}, None, None, None],
			[None, None, None, {'owned_by': None}, None],
			[None, None, {'owned_by': None}, None, None],
			[{'owned_by': None}, None, None, None, None]
		]

		self.assertEquals(g.getNode(2, 3), {'owned_by': None})
		self.assertEquals(g.getNode(0, 0), None)

		with self.assertRaises(IndexError):
			g.getNode(7, 3)

	def test_edgeList_get_node_key(self):
		node = {'x': 1, 'y': 2}
		key = graph.edgeList.getNodeKey(node)
		self.assertEquals(key, '{"x":1,"y":2}')

		node = {'y': 1, 'x': 2}
		key = graph.edgeList.getNodeKey(node)
		self.assertEquals(key, '{"x":2,"y":1}')

		node = {'y': 1, 'foo': 2}
		with self.assertRaises(KeyError):
			graph.edgeList.getNodeKey(node)

		node = {'foo': 1, 'x': 2}
		with self.assertRaises(KeyError):
			graph.edgeList.getNodeKey(node)

	def test_edgeList_addEdge(self):
		el = graph.edgeList()
		node1 = {'x': 0, 'y': 0}
		node2 = {'x': 1, 'y': 0}
		node3 = {'x': 1, 'y': 1}
		node4 = {'x': 0, 'y': 1}

		self.assertEquals(el, {})
		el.addEdge(node1, node2)
		self.assertEquals(el, {
			'{"x":0,"y":0}': [node2],
			'{"x":1,"y":0}': [node1]
		})

		el.addEdge(node2, node3)
		self.assertEquals(el, {
			'{"x":0,"y":0}': [node2],
			'{"x":1,"y":0}': [node1, node3],
			'{"x":1,"y":1}': [node2]
		})
		el.addEdge(node3, node4)
		self.assertEquals(el, {
			'{"x":0,"y":0}': [node2],
			'{"x":1,"y":0}': [node1, node3],
			'{"x":1,"y":1}': [node4, node2],
			'{"x":0,"y":1}': [node3]
		})
		el.addEdge(node4, node1)
		self.assertEquals(el, {
			'{"x":0,"y":0}': [node4, node2],
			'{"x":1,"y":0}': [node1, node3],
			'{"x":1,"y":1}': [node4, node2],
			'{"x":0,"y":1}': [node1, node3]
		})

	def test_edgeList_getEdgesFromNode(self):
		el = graph.edgeList()
		node1 = {'x': 0, 'y': 0}
		node2 = {'x': 1, 'y': 0}
		node3 = {'x': 1, 'y': 1}
		node4 = {'x': 0, 'y': 1}

		el.addEdge(node1, node2)
		el.addEdge(node2, node3)
		el.addEdge(node3, node4)
		el.addEdge(node4, node1)

		edgesNode1 = el.getEdgesFromNode(node1)
		edgesNode2 = el.getEdgesFromNode(node2)
		edgesNode3 = el.getEdgesFromNode(node3)
		edgesNode4 = el.getEdgesFromNode(node4)

		self.assertEquals(edgesNode1, [node4, node2])
		self.assertEquals(edgesNode2, [node1, node3])
		self.assertEquals(edgesNode3, [node4, node2])
		self.assertEquals(edgesNode4, [node1, node3])

	def test_getSideOfNodeFromEdge_left(self):
		edge = [
			{'x': 0, 'y': 1},
			{'x': 1, 'y': 0}
		]
		node = {'x': 0, 'y': 0}
		side = graph.convexHull.getSideOfNodeFromEdge(edge, node)
		self.assertGreater(side, 0)

	def test_getSideOfNodeFromEdge_right(self):
		edge = [
			{'x': 0, 'y': 1},
			{'x': 1, 'y': 0}
		]
		node = {'x': 1, 'y': 1}
		side = graph.convexHull.getSideOfNodeFromEdge(edge, node)
		self.assertLess(side, 0)

	def test_getSideOfNodeFromEdge_aligned_after(self):
		edge = [
			{'x': 0, 'y': 0},
			{'x': 1, 'y': 0}
		]
		node = {'x': 2, 'y': 0}
		side = graph.convexHull.getSideOfNodeFromEdge(edge, node)
		self.assertEquals(side, 0)

	def test_getSideOfNodeFromEdge_aligned_before(self):
		edge = [
			{'x': 0, 'y': 0},
			{'x': 1, 'y': 0}
		]
		node = {'x': -1, 'y': 0}
		side = graph.convexHull.getSideOfNodeFromEdge(edge, node)
		self.assertEquals(side, 0)

	def test_getNodeKey_hull_node_ok(self):
		node = {'x': 1, 'y': 2}
		self.assertEquals('1-2', graph.convexHull.getNodeKey(node))

	def test_getNodeKey_hull_node_ko(self):
		node = {'foo': 1}
		with self.assertRaises(KeyError):
			graph.convexHull.getNodeKey(node)

	def test_hull_getNextNode_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]

		h['0-4'] = [nodes[1], nodes[2]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['2-3'] = [nodes[0], nodes[1]]

		self.assertEquals(
			h.getNextNode(nodes[0], clockwise=True),
			nodes[1]
		)
		self.assertEquals(
			h.getNextNode(nodes[1], clockwise=True),
			nodes[2]
		)
		self.assertEquals(
			h.getNextNode(nodes[2], clockwise=True),
			nodes[0]
		)

	def test_hull_getNextNode_counter_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]

		h['0-4'] = [nodes[1], nodes[2]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['2-3'] = [nodes[0], nodes[1]]

		self.assertEquals(
			h.getNextNode(nodes[0], clockwise=False),
			nodes[2]
		)
		self.assertEquals(
			h.getNextNode(nodes[1], clockwise=False),
			nodes[0]
		)
		self.assertEquals(
			h.getNextNode(nodes[2], clockwise=False),
			nodes[1]
		)

	def test_flat_hull_is_tangent(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1}
		]

		h['0-4'] = [nodes[1]]
		h['1-1'] = [nodes[0]]

		edge1 = [nodes[0], nodes[1]]
		# 1 == tangent and hull parallel of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [{'x': -1, 'y': 7}, nodes[0]]
		# 1 == tangent and hull parallel of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [nodes[1], {'x': 2, 'y': -2}]
		# 1 == tangent and hull parallel of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [nodes[0], {'x': 2, 'y': 3}]
		# 1 == tangent and hull at the left of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [nodes[1], {'x': 1, 'y': 0}]
		# 1 == tangent and hull at the left of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [{'x': 1, 'y': 3}, nodes[1]]
		# 1 == tangent and hull at the left of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [nodes[1], {'x': 3, 'y': 2}]
		# -1 == tangent and hull at the right of the edge
		self.assertEquals(h.isTangent(edge1), -1)

		edge1 = [nodes[0], {'x': 0, 'y': 0}]
		# -1 == tangent and hull at the right of the edge
		self.assertEquals(h.isTangent(edge1), -1)

	def test_hull_is_tangent(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]

		h['0-4'] = [nodes[1], nodes[2]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['2-3'] = [nodes[0], nodes[1]]

		edge1 = [{'x': 2, 'y': 3}, {'x': 4, 'y': 0}]
		# 1 == tangent and hull at the left of the edge
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [{'x': 0, 'y': 2}, {'x': 1, 'y': 1}]
		# -1 == tangent and hull at the right of the edge
		self.assertEquals(h.isTangent(edge1), -1)

		edge1 = [{'x': 1, 'y': 4}, {'x': 7, 'y': 2}]
		# None == none of the nodes of the edge belong to the hull
		self.assertEquals(h.isTangent(edge1), None)

		edge1 = [{'x': 1, 'y': 1}, {'x': 1, 'y': 4}]
		# 0 == not tangent
		self.assertEquals(h.isTangent(edge1), 0)

		edge1 = [nodes[1], nodes[2]]
		# -1 == hull at the right of the edge, edge cotangent with a side of the hull
		self.assertEquals(h.isTangent(edge1), -1)

		edge1 = [{'x': 0, 'y': -1}, nodes[2]]
		# -1 == hull at the right of the edge, edge cotangent with a side of the hull
		self.assertEquals(h.isTangent(edge1), -1)

		edge1 = [nodes[1], {'x': 3, 'y': 5}]
		# -1 == hull at the right of the edge, edge cotangent with a side of the hull
		self.assertEquals(h.isTangent(edge1), -1)

		edge1 = [nodes[0], nodes[2]]
		# -1 == hull at the right of the edge, edge cotangent with a side of the hull
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [{'x': -2, 'y': 5}, nodes[2]]
		# -1 == hull at the right of the edge, edge cotangent with a side of the hull
		self.assertEquals(h.isTangent(edge1), 1)

		edge1 = [nodes[0], {'x': 2, 'y': 4}]
		# -1 == hull at the right of the edge, edge cotangent with a side of the hull
		self.assertEquals(h.isTangent(edge1), 1)

	def test_hull_isLowerTangent(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]

		h['0-4'] = [nodes[1], nodes[2]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['2-3'] = [nodes[0], nodes[1]]

		edge1 = [{'x': 2, 'y': 3}, {'x': 4, 'y': 0}]
		# 1 == tangent and hull at the left of the edge
		self.assertEquals(h.isLowerTangent(edge1), True)
		edge1 = [{'x': 0, 'y': 2}, {'x': 1, 'y': 1}]
		# -1 == tangent and hull at the right of the edge
		self.assertEquals(h.isLowerTangent(edge1), False)

	def test_hull_isUpperTangent(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]

		h['0-4'] = [nodes[1], nodes[2]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['2-3'] = [nodes[0], nodes[1]]

		edge1 = [{'x': 0, 'y': 2}, {'x': 1, 'y': 1}]
		# -1 == tangent and hull at the right of the edge
		self.assertEquals(h.isUpperTangent(edge1), True)
		edge1 = [{'x': 2, 'y': 3}, {'x': 4, 'y': 0}]
		# 1 == tangent and hull at the left of the edge
		self.assertEquals(h.isUpperTangent(edge1), False)

	def test_find_upper_tangent_between_hulls(self):
		h1 = graph.convexHull()
		h2 = graph.convexHull()
		nodes1 = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]
		h1['0-4'] = [nodes1[1], nodes1[2]]
		h1['1-1'] = [nodes1[2], nodes1[0]]
		h1['2-3'] = [nodes1[0], nodes1[1]]

		nodes2 = [
			{'x': 4, 'y': 2},
			{'x': 6, 'y': 1},
			{'x': 6, 'y': 4}
		]
		h2['4-2'] = [nodes2[1], nodes2[2]]
		h2['6-1'] = [nodes2[2], nodes2[0]]
		h2['6-4'] = [nodes2[0], nodes2[1]]

		upperTangent = graph.convexHull.findTangent(
			h1, h2,
			nodes1[2], nodes2[0],
			isUpperTangent=True
		)
		self.assertEquals(upperTangent, [nodes1[1], nodes2[1]])

	def test_find_lower_tangent_between_hulls(self):
		h1 = graph.convexHull()
		h2 = graph.convexHull()
		nodes1 = [
			{'x': 0, 'y': 4},
			{'x': 1, 'y': 1},
			{'x': 2, 'y': 3}
		]
		h1['0-4'] = [nodes1[1], nodes1[2]]
		h1['1-1'] = [nodes1[2], nodes1[0]]
		h1['2-3'] = [nodes1[0], nodes1[1]]

		nodes2 = [
			{'x': 4, 'y': 2},
			{'x': 6, 'y': 1},
			{'x': 6, 'y': 4}
		]
		h2['4-2'] = [nodes2[1], nodes2[2]]
		h2['6-1'] = [nodes2[2], nodes2[0]]
		h2['6-4'] = [nodes2[0], nodes2[1]]

		upperTangent = graph.convexHull.findTangent(
			h1, h2,
			nodes1[2], nodes2[0],
			isUpperTangent=False
		)
		self.assertEquals(upperTangent, [nodes1[0], nodes2[2]])

	def test_clean_line_hull_one_node_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1}
		]
		h['0-2'] = [nodes[1]]
		h['1-1'] = [nodes[0]]

		h._clean(nodes[1], nodes[1], True)

		expected = graph.convexHull()
		expected['1-1'] = [None]
		expected['0-2'] = [None]
		self.assertEquals(h, expected)

	def test_clean_line_hull_one_node_counter_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1}
		]
		h['0-2'] = [nodes[1]]
		h['1-1'] = [nodes[0]]

		h._clean(nodes[1], nodes[1], False)

		expected = graph.convexHull()
		expected['1-1'] = [None]
		expected['0-2'] = [None]
		self.assertEquals(h, expected)

	def test_clean_line_hull_one_node_to_from_different_counter_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1}
		]
		h['0-2'] = [nodes[1]]
		h['1-1'] = [nodes[0]]

		expected = graph.convexHull()
		expected['0-2'] = [nodes[1]]
		expected['1-1'] = [nodes[0]]

		h._clean(nodes[1], nodes[0], False)
		self.assertEquals(h, expected)
		h._clean(nodes[1], nodes[0], True)
		self.assertEquals(h, expected)
		h._clean(nodes[0], nodes[1], False)
		self.assertEquals(h, expected)
		h._clean(nodes[0], nodes[1], True)
		self.assertEquals(h, expected)

	def test_clean_hull_one_node_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]
		#  012345
		# 0...2..
		# 1.1....
		# 20...3.
		# 3......
		# 46..4..
		# 5..5...
		h['0-2'] = [nodes[1], nodes[6]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['3-0'] = [nodes[3], nodes[1]]
		h['4-2'] = [nodes[4], nodes[2]]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [nodes[6], nodes[4]]
		h['0-4'] = [nodes[0], nodes[5]]

		h._clean(nodes[3], nodes[4], True)
		expected = graph.convexHull()
		expected['0-2'] = [nodes[1], nodes[6]]
		expected['1-1'] = [nodes[2], nodes[0]]
		expected['3-0'] = [nodes[3], nodes[1]]
		expected['4-2'] = [None, nodes[2]]
		expected['3-4'] = [nodes[5], None]
		expected['2-5'] = [nodes[6], nodes[4]]
		expected['0-4'] = [nodes[0], nodes[5]]
		self.assertEquals(h, expected)

	def test_clean_hull_one_node_counter_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]
		h['0-2'] = [nodes[1], nodes[6]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['3-0'] = [nodes[3], nodes[1]]
		h['4-2'] = [nodes[4], nodes[2]]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [nodes[6], nodes[4]]
		h['0-4'] = [nodes[0], nodes[5]]

		h._clean(nodes[4], nodes[3], False)
		expected = graph.convexHull()
		expected['0-2'] = [nodes[1], nodes[6]]
		expected['1-1'] = [nodes[2], nodes[0]]
		expected['3-0'] = [nodes[3], nodes[1]]
		expected['4-2'] = [None, nodes[2]]
		expected['3-4'] = [nodes[5], None]
		expected['2-5'] = [nodes[6], nodes[4]]
		expected['0-4'] = [nodes[0], nodes[5]]
		self.assertEquals(h, expected)

	def test_fail_joinNodesClockwise_from_on_full_node(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]

		h['0-2'] = [nodes[1], nodes[6]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['3-0'] = [nodes[3], nodes[1]]
		h['4-2'] = [nodes[4], nodes[2]]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [nodes[6], nodes[4]]
		h['0-4'] = [nodes[0], nodes[5]]

		with self.assertRaises(graph.exception):
			h._joinNodesClockwise(nodes[3], nodes[5])

	def test_fail_joinNodesClockwise_to_on_full_node(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]

		h['0-2'] = [nodes[1], nodes[6]]
		h['1-1'] = [nodes[2], nodes[0]]
		h['3-0'] = [None, nodes[1]]
		h['4-2'] = [nodes[4], None]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [nodes[6], nodes[4]]
		h['0-4'] = [nodes[0], nodes[5]]

		with self.assertRaises(graph.exception):
			h._joinNodesClockwise(nodes[2], nodes[4])

	def test_joinNodesClockwise_from_on_two_nodes_hull(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]
		#  012345
		# 0...2..
		# 1.1....
		# 20...3.
		# 3......
		# 46..4..
		# 5..5...

		# The 2nodes hull is the [0, 6]
		# [1, 2, 3, 4, 5] is the second hull
		h['0-2'] = [nodes[6]]
		h['1-1'] = [nodes[2], None]
		h['3-0'] = [nodes[3], nodes[1]]
		h['4-2'] = [nodes[4], nodes[2]]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [None, nodes[4]]
		h['0-4'] = [nodes[0]]

		h._joinNodesClockwise(nodes[0], nodes[1])
		expected = graph.convexHull()
		expected['0-2'] = [nodes[1], nodes[6]]
		expected['1-1'] = [nodes[2], nodes[0]]
		expected['3-0'] = [nodes[3], nodes[1]]
		expected['4-2'] = [nodes[4], nodes[2]]
		expected['3-4'] = [nodes[5], nodes[3]]
		expected['2-5'] = [None, nodes[4]]
		expected['0-4'] = [nodes[0]]
		self.assertEquals(h, expected)

	def test_joinNodesClockwise_to_on_two_nodes_hull(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]
		#  012345
		# 0...2..
		# 1.1....
		# 20...3.
		# 3......
		# 46..4..
		# 5..5...

		# The 2nodes hull is the [0, 6]
		# [1, 2, 3, 4, 5] is the second hull
		h['0-2'] = [nodes[6]]
		h['1-1'] = [nodes[2], None]
		h['3-0'] = [nodes[3], nodes[1]]
		h['4-2'] = [nodes[4], nodes[2]]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [None, nodes[4]]
		h['0-4'] = [nodes[0]]

		h._joinNodesClockwise(nodes[5], nodes[6])
		expected = graph.convexHull()
		expected['0-2'] = [nodes[6]]
		expected['1-1'] = [nodes[2], None]
		expected['3-0'] = [nodes[3], nodes[1]]
		expected['4-2'] = [nodes[4], nodes[2]]
		expected['3-4'] = [nodes[5], nodes[3]]
		expected['2-5'] = [nodes[6], nodes[4]]
		expected['0-4'] = [nodes[0], nodes[5]]
		self.assertEquals(h, expected)

	def test_joinNodesClockwise_join_hulls(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 2},
			{'x': 1, 'y': 1},
			{'x': 3, 'y': 0},
			{'x': 4, 'y': 2},
			{'x': 3, 'y': 4},
			{'x': 2, 'y': 5},
			{'x': 0, 'y': 4}
		]
		#  012345
		# 0...2..
		# 1.1....
		# 20...3.
		# 3......
		# 46..4..
		# 5..5...

		# The 2nodes hull is the [0, 6]
		# [1, 2, 3, 4, 5] is the second hull
		h['0-2'] = [nodes[1], nodes[6]]
		h['1-1'] = [None, nodes[0]]
		h['3-0'] = [nodes[3], None]
		h['4-2'] = [nodes[4], nodes[2]]
		h['3-4'] = [nodes[5], nodes[3]]
		h['2-5'] = [None, nodes[4]]
		h['0-4'] = [nodes[0], None]

		h._joinNodesClockwise(nodes[5], nodes[6])
		expected = graph.convexHull()
		expected['0-2'] = [nodes[1], nodes[6]]
		expected['1-1'] = [None, nodes[0]]
		expected['3-0'] = [nodes[3], None]
		expected['4-2'] = [nodes[4], nodes[2]]
		expected['3-4'] = [nodes[5], nodes[3]]
		expected['2-5'] = [nodes[6], nodes[4]]
		expected['0-4'] = [nodes[0], nodes[5]]
		self.assertEquals(h, expected)

	# functional tests

	def test_merge_hulls_4_nodes_with_one_inside(self):
		h1 = graph.convexHull()
		h2 = graph.convexHull()
		nodes1 = [
			{'x': 0, 'y': 4},
			{'x': 2, 'y': 0}
		]
		nodes2 = [
			{'x': 2, 'y': 2},
			{'x': 3, 'y': 3}
		]
		h1['0-4'] = [nodes1[1]]
		h1['2-0'] = [nodes1[0]]
		h2['2-2'] = [nodes2[1]]
		h2['3-3'] = [nodes2[0]]

		(hull, upperTangent, lowerTangent) = graph.convexHull.merge(
			h1, h2, nodes1[1], nodes2[0]
		)
		expected = graph.convexHull()
		expected['0-4'] = [nodes1[1], nodes2[1]]
		expected['2-0'] = [nodes2[1], nodes1[0]]
		expected['3-3'] = [nodes1[0], nodes1[1]]

		self.assertEquals(hull, expected)
		self.assertEquals(upperTangent, [nodes1[1], nodes2[1]])
		self.assertEquals(lowerTangent, [nodes1[0], nodes2[1]])

	def test_generate_hull_2_nodes(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 0},
			{'x': 0, 'y': 1}
		]

		h.generate(nodes[0], nodes[1])

		expected = {
			'0-0': [nodes[1]],
			'0-1': [nodes[0]]
		}
		self.assertEquals(dict(h), expected)

	def test_generate_hull_3_nodes_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 1},
			{'x': 1, 'y': 0},
			{'x': 1, 'y': 1}
		]

		h.generate(nodes[0], nodes[1], nodes[2])

		expected = {
			'0-1': [nodes[1], nodes[2]],
			'1-0': [nodes[2], nodes[0]],
			'1-1': [nodes[0], nodes[1]]
		}
		self.assertEquals(dict(h), expected)

	def test_generate_hull_3_nodes_counter_clockwise(self):
		h = graph.convexHull()
		nodes = [
			{'x': 0, 'y': 1},
			{'x': 1, 'y': 0},
			{'x': 0, 'y': 0}
		]

		h.generate(nodes[0], nodes[1], nodes[2])

		expected = {
			'0-0': [nodes[1], nodes[0]],
			'0-1': [nodes[2], nodes[1]],
			'1-0': [nodes[0], nodes[2]]
		}
		self.assertEquals(dict(h), expected)

	def test_generate_edges_2_nodes(self):
		g = graph.graph()
		g.nodes = [
			OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 1), ('y', 1)])
		]
		g.nodesGrid = [
			[None, None, None, None, None],
			[None, {'owned_by': None}, None, None, None],
			[None, None, None, None, None],
			[None, None, None, None, None],
			[{'owned_by': None}, None, None, None, None]
		]

		g.generateEdges()
		expected = {
			'{"x":1,"y":1}': [OrderedDict([('x', 0), ('y', 4)])],
			'{"x":0,"y":4}': [OrderedDict([('x', 1), ('y', 1)])]
		}
		self.assertEquals(g.edges, expected)

	def test_generate_edges_3_nodes(self):
		g = graph.graph()
		g.nodes = [
			OrderedDict([('x', 0), ('y', 4)]),
			OrderedDict([('x', 1), ('y', 1)]),
			OrderedDict([('x', 3), ('y', 2)])
		]
		g.nodesGrid = [
			[None, None, None, None, None],
			[None, {'owned_by': None}, None, None, None],
			[None, None, None, {'owned_by': None}, None],
			[None, None, None, None, None],
			[{'owned_by': None}, None, None, None, None]
		]

		g.generateEdges()
		expected = {
			'{"x":1,"y":1}': [
				OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 3), ('y', 2)])
			],
			'{"x":3,"y":2}': [
				OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 1), ('y', 1)])
			],
			'{"x":0,"y":4}': [
				OrderedDict([('x', 1), ('y', 1)]), OrderedDict([('x', 3), ('y', 2)])
			]
		}
		self.assertEquals(g.edges, expected)

	def test_generate_edges_4_nodes(self):
		g = graph.graph()
		g.nodes = [
			OrderedDict([('x', 0), ('y', 4)]),
			OrderedDict([('x', 1), ('y', 1)]),
			OrderedDict([('x', 3), ('y', 2)]),
			OrderedDict([('x', 4), ('y', 3)])
		]
		g.nodesGrid = [
			[None, None, None, None, None],
			[None, {'owned_by': None}, None, None, None],
			[None, None, None, {'owned_by': None}, None],
			[None, None, None, None, {'owned_by': None}],
			[{'owned_by': None}, None, None, None, None]
		]

		g.generateEdges()
		expected = {
			'{"x":0,"y":4}': [g.nodes[1], g.nodes[3]],
			'{"x":1,"y":1}': [g.nodes[0], g.nodes[2]],
			'{"x":3,"y":2}': [g.nodes[1], g.nodes[3]],
			'{"x":4,"y":3}': [g.nodes[0], g.nodes[2]]
		}
		self.assertEquals(g.edges, expected)

	def test_generate_edges_5_nodes(self):
		g = graph.graph()
		g.nodes = [
			OrderedDict([('x', 0), ('y', 4)]),
			OrderedDict([('x', 1), ('y', 1)]),
			OrderedDict([('x', 3), ('y', 0)]),
			OrderedDict([('x', 3), ('y', 2)]),
			OrderedDict([('x', 4), ('y', 3)])
		]
		g.nodesGrid = [
			[None, None, None, {'owned_by': None}, None],
			[None, {'owned_by': None}, None, None, None],
			[None, None, None, {'owned_by': None}, None],
			[None, None, None, None, {'owned_by': None}],
			[{'owned_by': None}, None, None, None, None]
		]

		g.generateEdges()
		expected = {
			'{"x":0,"y":4}': [g.nodes[1], g.nodes[2], g.nodes[4]],
			'{"x":1,"y":1}': [g.nodes[0], g.nodes[2]],
			'{"x":3,"y":0}': [g.nodes[0], g.nodes[1], g.nodes[4]],
			'{"x":3,"y":2}': [g.nodes[4]],
			'{"x":4,"y":3}': [g.nodes[0], g.nodes[2], g.nodes[3]]
		}
		self.assertEquals(g.edges, expected)
