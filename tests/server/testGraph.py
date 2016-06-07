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
