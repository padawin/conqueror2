# -*- coding: utf-8 -*-
import unittest

from server import graph
import tests.common


class graphTests(tests.common.common):
	def test_nodes_generation(self):
		g = graph.graph()
		g.generateNodes(5, 5, 5, lambda: {'owned_by': None})

		self.assertEquals(len(g.nodes), 5)
