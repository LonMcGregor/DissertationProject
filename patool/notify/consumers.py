import os
import time

from channels.sessions import channel_session
from django.db import transaction

counter = 0
active_connections = {}


class Connection:
    connection_id = -1
    reply_channel = 1


@channel_session
def ws_connect(msg):
    """Accept an incoming websocket connection with data in @msg"""
    global counter, active_connections
    msg.channel_session['id'] = counter
    active_connections[counter] = msg
    counter += 1
    print("open connection with client %s" % msg.channel_session['id'])


@channel_session
def ws_receive(msg):
    """Handle an incoming websocket @msg and set up for reply"""
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
    """A given websocket connection detailed in @msg has been closed by the client"""
    global active_connections
    del active_connections[msg.channel_session['id']]
    print("connection to client %s closed" % msg.channel_session['id'])


def add_notification(info):
    """We want to add a notification with @info for a given user"""
    add_notification_to_database(info)
    notify_user(info)


@transaction.atomic
def add_notification_to_database(info):
    """Create and add a notification with @info to the db"""
    pass


def notify_user(info):
    """If the user in @info us currently connected, tell them about it"""
    if not is_connected(info.user):
        return
    pass


def is_connected(user):
    """Identify if a user is currently connected"""
    return False