import os
import sys
import time
from slackclient import SlackClient

from collections import namedtuple


Chat = namedtuple('Contact', 'name id')


class Slack(object):

    def __init__(self):
        token = os.environ.get('SLACK_TOKEN')
        if not token:
            print('Need to define ENV variable "SLACK_TOKEN"')
            sys.exit(-1)

        self.sc = SlackClient(token)
        self.contacts = []
        self.channels = []
        self.active = []
        self.ims = {}

    def setup(self):
        self.set_contacts()
        self.set_channels()
        self.set_ims()
        self.active = self.active_chats()

    def set_contacts(self):
        contacts = self.sc.api_call("users.list")
        self.contacts = [
            Chat(name=c['name'], id=c['id'])
            for c in contacts['members'] if not c['deleted']
        ]

    def set_channels(self):
        channels = self.sc.api_call("channels.list", exclude_archived=1)
        self.channels = [
            Chat(name=c['name'], id=c['id'])
            for c in channels['channels']
        ]

    def active_chats(self):
        """
        returns a list of the chats we want to show
        Only Ims for the moment
        """
        show = []
        for c in self.contacts:
            if c.id in list(self.ims.keys()):
                show.append(c)
                self.ims[c.id]['username'] = c.name
        return show

    def set_ims(self):
        ims = self.sc.api_call("im.list")
        for d in ims['ims']:
            if not d['is_user_deleted']:
                self.ims[d['user']] = {
                    'id': d['id'],
                    'username': ''
                }

    def message_channel(self, id, message):
        # disable for testing
        self.sc.api_call(
            "chat.postMessage",
            channel=id,
            text=message,
            as_user=True)

    def channel_history(self, id, count=3):
        # By default only get the last 3 messages
        hist = self.sc.api_call(
            "channels.history",
            channel=id,
            count=count)
        return hist

    def im_history(self, id, count=3):
        # By default only get the last 3 messages
        hist = self.sc.api_call(
            "im.history",
            channel=id,
            count=count)
        return hist

    def last_messages(self, id):
        """
        This method retrieves the history of the channel
        or IM and maps user id's to usernames
        """
        messages = self.im_history(self.ims[id]['id'])
        history = []
        for m in messages['messages']:
            history.append({
                'user': self.ims[m['user']]['username'],
                'text': m['text']
            })
        return history
