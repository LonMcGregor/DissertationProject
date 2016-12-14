import tornado.ioloop
import tornado.web
import echosockjs as ejs


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application(
        ejs.EchoSockjsRouter('/notify') + [
            (r"/", MainHandler),
        ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()