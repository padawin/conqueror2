# -*- coding: utf-8 -*-
import unittest

from server import graph
import tests.common


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
			'{"x":1,"y":1}': [node2, node4],
			'{"x":0,"y":1}': [node3]
		})
		el.addEdge(node4, node1)
		self.assertEquals(el, {
			'{"x":0,"y":0}': [node2, node4],
			'{"x":1,"y":0}': [node1, node3],
			'{"x":1,"y":1}': [node2, node4],
			'{"x":0,"y":1}': [node3, node1]
		})
