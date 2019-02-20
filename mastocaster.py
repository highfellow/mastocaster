#!/usr/bin/python3
from mastodon import Mastodon, StreamListener
from bs4 import BeautifulSoup
import sys, yaml, datetime, pprint, re
pp = pprint.PrettyPrinter(depth=4)

# Function defs

# print out a notification
def notif_print(notif):
    print ("Notification:")
    print ("  type: %s" % notif.type)
    print ("  created: %s" % notif.created_at)
    print ("  account: %s" % notif.account.username)
    if notif.type in ['mention', 'reblog', 'favourite']:
        status_print(notif.status)
        pp.pprint(notif.status)

# print out a status
def status_print(status):
    print ("Status:")
    print ("  account: %s" % status.account.username)
    print ("  created: %s" % status.created_at)
    print ("  visibility: %s" % status.visibility)
    if status.spoiler_text:
        print ("  spoiler: %s" % status.spoiler_text)
    print ("  content: %s" % status.content)


with open(sys.argv[1]) as f:
    config = yaml.load(f.read())
print("Read config file: %s" % sys.argv[1])

# Class defs
class NotifListener(StreamListener):

    def on_notification(self, notif):
        if notif.type == "mention":
            status_relay(notif)

def status_relay(notif):
    print("parsing status:")
    sender=notif.account.acct
    print("sender: %s" % sender)
    soup=BeautifulSoup(notif.status.content,'html.parser')
    print("incoming status:")
    print(soup.prettify())
    for hcard in soup.find_all(attrs={'class': 'h-card'}):
        if hcard.a['href'] == config['Account URL']:
            hcard.extract()
    outgoing='[@' + sender + '] ' + soup.string
    print("outgoing status: %s" % outgoing)
    mastodon.status_post(outgoing, visibility=config['Post Visibility'])


# Log in - either every time, or use persisted
mastodon = Mastodon(
    api_base_url = config['Instance URL'],
    client_id = config['Client ID'],
    client_secret = config['Client Secret'],
    access_token = config['Access Token'],
    ratelimit_method = 'pace',
    ratelimit_pacefactor = 0.1
)
print("Logged in")
notifListener=NotifListener()
print ("Listening for notifications")
mastodon.stream_user(notifListener)

