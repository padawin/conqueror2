import tornado.ioloop
import tornado.web
import tornado.websocket

import uuid
import json

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("../web/index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self, *args):
		self.id = uuid.uuid4()
		self.stream.set_nodelay(True)
		clients[self.id] = {"id": self.id, "object": self}

	def on_message(self, message):
		try:
			message = json.loads(message)
		except ValueError:
			print('invalid json: %s' % message)
			return

		if message['messageType'] == 'CLIENT_JOINED':
			for key in clients:
				if key is not self.id:
					clients[key]['object'].write_message(u'%s joined' % self.id)
		elif message['messageType'] == 'CLIENT_CLOSED':
			del clients[self.id]
			for key in clients:
				clients[key]['object'].write_message(u'%s left' % self.id)

	def on_close(self):
		if self.id in clients:
			del clients[self.id]

app = tornado.web.Application([
	(r'/', IndexHandler),
	(r'/ws', WebSocketHandler),
])

if __name__ == '__main__':
	parse_command_line()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
