import botulism
import re
from time import sleep

logfile = 'demo.log'
server = 'irc.freenode.net'
channel = '#stupidbottestroom'
credentials = {'nick': 'foobardemobot', 'password': 'SomePasswordOrSomething'}
pattern = re.compile(':(?P<user>[\S]+)!(?P<id>[\S]+) PRIVMSG [\S]+ :@foobardemobot (?P<command>[\S]+)[ ]*(?P<body>[\S\s]*)')


def responder(re_match, conn):
    conn.send(
        bytes(
            "PRIVMSG #stupidbottestroom : Hello {}! I'm a stupid demo bot!\r\n".format(re_match.group(1)),
            'UTF-8'))

demo_connection = botulism.connect(name='demo_connection')

demo_connection.addCommand('greeter', pattern, responder)

sleep(360)
