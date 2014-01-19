import botulism
import re
import socket
import sys
import smtplib
import time
from email.mime.text import MIMEText

passwd = sys.argv[1]
to_email = sys.argv[2]

pattern = re.compile(":(?P<user>[\S]+)!(?P<id>[\S]+) PRIVMSG [\S]+ :!TABot (?P<command>[\S]+)[ ]*(?P<body>[\S\s]*)")
mailserv = smtplib.SMTP('localhost')

def do_ask(user, ident, body, command, connection):
    connection.send(bytes("PRIVMSG #cs4414 : Thanks for asking, {}! I'm sending an \
email with your question and username to the course staff.\r\n".format(user), 'UTF-8'))
    message = MIMEText("Course staff: At {}, {} ({}) on #cs4414 asked the following: \
\n\n\t\"{}\"\n\nThanks, your friendly neighborhood IRC bot.".format(time.strftime("%c"), user, ident, body.rstrip()))
    message['Subject'] = "[IRC BOT] A question from {}".format(user)
    message['From'] = "cs4414-bot@virginia.edu"
    message['To'] = to_email
    mailserv.send_message(message)

def do_help(user, ident, body, command, connection):
    connection.send(bytes("PRIVMSG #cs4414 : Hi, {}! I'm TABot-4414! Here's a listing of my currently available commands:\r\n".format(user),'UTF-8'))
    connection.send(bytes("PRIVMSG #cs4414 : {}: (1) ask     - The ask command will send the TA's and professor an email with your information and question.\r\n".format(user),'UTF-8'))
    connection.send(bytes("PRIVMSG #cs4414 : {}: (2) help    - The help command prints this output.\r\n".format(user), 'UTF-8'))
    connection.send(bytes("PRIVMSG #cs4414 : {}: We might have more coming soon, depending on what seems helpful. Invoke any of these by sending '!TABot <command> <data>.\r\n".format(user), 'UTF-8'))

def unknown_command(user, ident, body, command, connection):
    connection.send(bytes("PRIVMSG #cs4414 : {}: I'm sorry, I don't know what {} means. Try !TABot help if you aren't sure what command you want.\r\n".format(user, command),'UTF-8'))

known_commands = {'ask': do_ask, 'help': do_help}

def response(commands, connection):
    user = commands.group(1)
    ident = commands.group(2)
    command = commands.group(3)
    body = commands.group(4)
    known_commands.get(command, unknown_command)(user, ident, body, command, connection)

rustchan = botulism.connect("irc.mozilla.org", "#cs4414", "TABot-4414", passwd)
logfile = open("botlogs.txt", "w+")
botulism.idle(rustchan, response, logfile, pattern)