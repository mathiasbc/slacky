import time
from slackclient import SlackClient


# get all users info, could store this meta somewhere
# print(sc.api_call("users.list"))
# if sc.rtm_connect():
#     print(sc.api_call(
#         "chat.postMessage",
#         channel='D02VA032R', # channel ID only for IM
#         text='!karma',
#         as_user=True
#     ))
#     while True:
#         print(sc.rtm_read())
#         time.sleep(5)
# else:
#     print("Connection Failed, invalid token?")



class Slack(object):

    def __init__(self):
        # TODO: move token to file not versioned
        token = "xoxp-2151890299-2997363102-36830412037-01d0d5d3a7"
        self.sc = SlackClient(token)
        # print(self.sc.api_call("api.test"))

    def get_contacts_names(self):
        self.contacts = self.sc.api_call("users.list")
        return [m['name'] for m in self.contacts['members']][-10:]

    def get_channels(self):
        self.channels = self.sc.api_call("channels.list")
        return [{c['name']: c['id']} for c in self.channels['channels']]

    def get_ims(self):
        self.ims = self.sc.api_call("im.list")
        return self.ims['ims']
