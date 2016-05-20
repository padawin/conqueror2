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
openGames = game.collection()
fullGames = game.collection()

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
			gameInstance = openGames.getGame()
			gameInstance.addPlayer(self)

			if not gameInstance.hasFreeSlot():
				firstPlayer = gameInstance.defineFirstPlayer()
				fullGames.addGame(gameInstance)
				openGames.deleteGame(gameInstance)

				firstPlayer.write_message(u'Your turn to start')
		else:
			gameInstance = openGames.createGame(self)

		self.game = gameInstance

	def on_message(self, message):
		try:
			message = json.loads(message)
		except ValueError:
			print('invalid json: %s' % message)
			return

		if message['messageType'] == 'CLIENT_JOINED':
			self.game.notifyPlayers(self, u'%s joined' % self.id)

	def on_close(self):
		if self.id in clients:
			self.game.notifyPlayers(self, u'%s left' % self.id)

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
	(r'/', IndexHandler),
	(r'/ws', WebSocketHandler),
])

if __name__ == '__main__':
	parse_command_line()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
