import tornado.ioloop
import tornado.web
import tornado.websocket

import uuid
import json
import game
import graph

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
openGames = game.collection()
fullGames = game.collection()


class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self, url):
		if url == '':
			url = 'index.html'
		self.render("../web/%s" % url)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self, *args):
		self.id = uuid.uuid4()
		self.stream.set_nodelay(True)
		clients[self.id] = {"id": self.id, "object": self}

		if len(openGames.keys()) == 0:
			gameInstance = game.createGame(self, graph.graph())
			openGames.addGame(gameInstance)
		else:
			gameInstance = openGames.getGame()
			gameInstance.addPlayer(self)

			if not gameInstance.hasFreeSlot():
				gameInstance.initialisePlayers()
				playersOrder = gameInstance.definePlayersOrder()
				fullGames.addGame(gameInstance)
				openGames.deleteGame(gameInstance)

				for key, playerId in enumerate(playersOrder):
					gameInstance.players[playerId].write_message(
						{
							'type': 'PLAYER_ID',
							'message': key
						}
					)

				gameInstance.notifyPlayers(
					message={
						'type': 'GAME_MAP',
						'map': gameInstance.getSerializedGraph()
					}
				)

				gameInstance.notifyNextPlayerTurn()

		self.game = gameInstance

	def on_message(self, message):
		try:
			message = json.loads(message)
		except ValueError:
			print('invalid json: %s' % message)
			return

		if message['messageType'] == 'CLIENT_JOINED':
			self.game.notifyPlayers(
				self,
				{
					'type': 'PLAYER_JOINED',
					'message': u'%s joined' % self.id
				}
			)
		elif message['messageType'] == 'CAPTURED_NODE':
			isCurrentPlayer = self.game.currentPlayer == message['playerId']
			hasGoodPlayerIndex = self.game.playerIds[message['playerId']] == self.id
			if isCurrentPlayer and hasGoodPlayerIndex and self.game.conquerNode(
				message['node'], message['playerId']
			):
				self.game.notifyPlayers(
					message={
						'type': 'GAME_MAP',
						'map': self.game.getSerializedGraph()
					}
				)
				self.game.endTurn()

	def on_close(self):
		if self.id in clients:
			self.game.notifyPlayers(
				self,
				{
					'type': 'PLAYER_LEFT',
					'message': u'%s left' % self.id
				}
			)

			del clients[self.id]
			self.game.deletePlayer(self)

			# the game still has a player, it is now open
			if self.game.hasPlayers():
				openGames.addGame(self.game)
				fullGames.deleteGame(self.game)
			# Else the game is empty, delete it
			else:
				openGames.deleteGame(self.game)

app = tornado.web.Application([
	(r'/ws', WebSocketHandler),
	(r'/(.*)', IndexHandler)
])

if __name__ == '__main__':
	parse_command_line()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
