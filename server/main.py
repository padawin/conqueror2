import tornado.ioloop
import tornado.web
import tornado.websocket

import uuid
import json
import game

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
openGames = dict()
fullGames = dict()

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("../web/index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self, *args):
		self.id = uuid.uuid4()
		self.stream.set_nodelay(True)
		clients[self.id] = {"id": self.id, "object": self}

		if len(openGames.keys()) > 0:
			gameInstance = openGames[openGames.keys()[0]]
			gameInstance.addPlayer(self)
			fullGames[gameInstance.id] = gameInstance
			del openGames[gameInstance.id]

		else:
			gameInstance = game.game()
			gameInstance.addPlayer(self)
			openGames[gameInstance.id] = gameInstance

		self.game = gameInstance

	def on_message(self, message):
		try:
			message = json.loads(message)
		except ValueError:
			print('invalid json: %s' % message)
			return

		if message['messageType'] == 'CLIENT_JOINED':
			players = self.game.players
			for playerId in players.keys():
				if players[playerId].id is not self.id:
					players[playerId].write_message(
						u'%s joined' % self.id
					)

	def on_close(self):
		if self.id in clients:
			players = self.game.players
			for playerId in players.keys():
				if players[playerId].id is not self.id:
					players[playerId].write_message(u'%s left' % self.id)

			del clients[self.id]
			del self.game.players[self.id]

			# the game still has a player, it is now open
			if len(self.game.players.keys()) == 1:
				openGames[self.game.id] = self.game
				del fullGames[self.game.id]
			# Else the game is empty, delete it
			else:
				del openGames[self.game.id]

app = tornado.web.Application([
	(r'/', IndexHandler),
	(r'/ws', WebSocketHandler),
])

if __name__ == '__main__':
	parse_command_line()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
