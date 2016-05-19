import random
import operator


class game:
	def __init__(self):
		self.nodes = []
		self.edges = []
		self.players = {}

	def addPlayer(self, player):
		self.players[player.id] = player

	def hasFreeSlot(self):
		return len(self.players) < 2

	def generateNodes (self, nbNodes, maxWidth, maxHeight):
		while nbNodes > 0:
			self.nodes.append({
				'x': random.randint(0, maxWidth - 1),
				'y': random.randint(0, maxHeight - 1)
			})
			nbNodes -= 1;

		self.nodes = sorted(self.nodes, key=operator.itemgetter('x', 'y'))

	def generateEdges(self, start=0, end=None):
		if end is None:
			end = len(self.nodes) - 1

		if end - start >= 3:
			edges = self.generateEdges(start, start + (end - start) / 2)
			edges.extend(self.generateEdges(start + (end - start) / 2 + 1, end))
			return edges
		elif end - start == 2:
			return [
				[self.nodes[start], self.nodes[start + 1]],
				[self.nodes[start + 1], self.nodes[start + 2]],
				[self.nodes[start + 2], self.nodes[start]]
			]
		else:
			return [[self.nodes[start], self.nodes[start + 1]]]
