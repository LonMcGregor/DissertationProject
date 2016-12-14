from sockjs.tornado import SockJSRouter, SockJSConnection
import time

counter = 0


class EchoWebSocket(SockJSConnection):
    def on_open(self, request):
        global counter
        self.id = counter
        counter += 1
        print("sockjs: open connection with client %s" % self.id)

    def on_message(self, data):
        print("data from client %s: %r" % (self.id, data,))
        self.send("echo reply. You are client %s" % self.id)
        for i in range(0,10):
            self.send(i)
            time.sleep(5)

    def on_comment(self, data):
        print("data comment from client %s: %r" % (self.id, data,))
        self.send(data)

    def on_close(self):
        print("sockjs: connection to client %s closed" % self.id)


def EchoSockjsRouter(prefix):
    return SockJSRouter(EchoWebSocket, prefix).urls