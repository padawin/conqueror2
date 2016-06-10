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

	# functional tests

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
			'{"x":0,"y":4}': [OrderedDict([('x', 1), ('y',1)])]
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
			'{"x":1,"y":1}': [OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 3), ('y', 2)])],
			'{"x":3,"y":2}': [OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 1), ('y', 1)])],
			'{"x":0,"y":4}': [OrderedDict([('x', 1), ('y', 1)]), OrderedDict([('x', 3), ('y', 2)])]
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
			'{"x":1,"y":1}': [OrderedDict([('x', 0), ('y', 4)])],
			'{"x":3,"y":2}': [OrderedDict([('x', 4), ('y', 3)])],
			'{"x":0,"y":4}': [OrderedDict([('x', 1), ('y', 1)])],
			'{"x":4,"y":3}': [OrderedDict([('x', 3), ('y', 2)])]
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
			'{"x":0,"y":4}': [OrderedDict([('x', 1), ('y', 1)]), OrderedDict([('x', 3), ('y', 0)])],
			'{"x":1,"y":1}': [OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 3), ('y', 0)])],
			'{"x":3,"y":0}': [OrderedDict([('x', 0), ('y', 4)]), OrderedDict([('x', 1), ('y', 1)])],
			'{"x":3,"y":2}': [OrderedDict([('x', 4), ('y', 3)])],
			'{"x":4,"y":3}': [OrderedDict([('x', 3), ('y', 2)])]
		}
		self.assertEquals(g.edges, expected)
