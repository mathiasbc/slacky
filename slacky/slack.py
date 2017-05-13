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

    def setup(self):
        self.set_contacts()
        self.set_channels()
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
        returns a list of the chats we want to show, should read
        this from a file perhaps ?
        """
        # for dev, only show 10 contacts
        show = self.contacts[-10:]
        show.extend(self.channels[:10])
        return show

    # TODO: we need to build a hash, keyed by ['user'] from im
    def get_ims(self):
        self.ims = self.sc.api_call("im.list")
        return self.ims['ims']

    def message_channel(self, id, message):
        pass
        # disable for testing
        # self.sc.api_call(
        #     "chat.postMessage",
        #     channel=id,
        #     text=message,
        #     as_user=True)

    def channel_history(self, id, count=10):
        """
        By default only get the last 10 messages
        """
        hist = self.sc.api_call(
            "channels.history",
            channel=id,
            count=count)
        return hist

    def im_history(self, id):
        hist = self.sc.api_call(
            "im.history",
            channel=id)
        return hist


def main():
    client = Slack()
    client.setup()

    # for c in client.active:
        # print(c.name, c.id)

    # print(client.get_ims())
    his = client.im_history('D02VBAP3C')
    print(his)


    # connect to the real time API
    # for feeding incoming messages
    # if client.sc.rtm_connect():
        # while True:
            # print(client.sc.rtm_read())
            # time.sleep(5)


if __name__ == "__main__":
    main()
