from channels.sessions import channel_session
import time
import os

counter = 0


@channel_session
def ws_connect(msg):
    global counter
    msg.channel_session['id'] = counter
    counter += 1
    print("open connection with client %s" % msg.channel_session['id'])


@channel_session
def ws_receive(msg):
    mid = msg.channel_session['id']
    print("data from client %s: %r" % (mid, msg.__str__(),))
    text_message = "echo reply. You are client %s connected to %s" % (mid, os.getpid())
    reply = {"text": text_message}
    msg.reply_channel.send(reply)
    for i in range(0, 10):
        msg.reply_channel.send({"text": str(i)})
        time.sleep(5)


@channel_session
def ws_disconnect(msg):
    print("connection to client %s closed" % msg.channel_session['id'])
