import botulism
import re
import socket
import sys
import smtplib
import time
from email.mime.text import MIMEText

passwd = sys.argv[1]
pattern = re.compile(":(?P<user>[\S\s]+)!(?P<id>[\S\s]+) PRIVMSG [\S\s]+ :!TABot ask (?P<question>[\S\s]+)")
mailserv = smtplib.SMTP('localhost')

def response(commands, connection):
    user = commands.group(1)
    ident = commands.group(2)
    question = commands.group(3)
    connection.send(bytes("PRIVMSG <CHANNEL> : Thanks for asking, {}! I'm sending an \
email with your question and username to the course staff.\r\n".format(user), 'UTF-8'))
    message = MIMEText("Course staff: At {}, {} ({}) on <CHANNEL> asked the following: \
\n\n\t\"{}\"\n\nThanks, your friendly neighborhood IRC bot.".format(time.strftime("%c"), user, ident, question.rstrip()))
    message['Subject'] = "[IRC BOT] A question from {}".format(user)
    message['From'] = <FROM EMAIL>
    message['To'] = <TO EMAIL>
    mailserv.send_message(message)

rustchan = botulism.connect(<SERVER>, <CHANNEL>, <NICK>, passwd)
logfile = open(<LOGFILE>, "w+")
botulism.idle(rustchan, response, logfile, pattern)

