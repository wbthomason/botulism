import socket
import re
import time

def connect(server, chan, nick, passwd):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((server, 6667))
    print("Connected to {}".format(server))
    connection.send(bytes("USER {0} 8 * :{0}\r\n".format(nick), 'UTF-8'))
    updates = connection.recv(4096).decode('UTF-8')
    print(updates)
    if updates.find("PING") != -1:
        pong = "PONG {}\r\n".format(updates.split()[1])
        print(pong)
        connection.send(bytes("PONG :{}\r\n".format(updates.split()[0]),'UTF-8'))
    connection.send(bytes("NICK {}\r\n" .format(nick), 'UTF-8'))
    updates = connection.recv(4096).decode('UTF-8')
    print(updates)
    if updates.find("PING") != -1:
        pong = "PONG {}\r\n".format(updates.split()[1])
        print(pong)
        connection.send(bytes(pong,'UTF-8'))
    print("Using nick {}".format(nick))
    time.sleep(2)
    connection.send(bytes("PRIVMSG NickServ :identify {}\r\n".format(passwd), 'UTF-8')) 
    connection.send(bytes("JOIN {}\r\n".format(chan), 'UTF-8'))
    return connection

def idle(connection, responder, logfile, pattern):
    while True:
        updates = connection.recv(4096).decode('UTF-8')
        print(updates)
        if updates.find("PING") != -1:
            pong = "PONG {}\r\n".format(updates.split()[1])
            print(pong)
            connection.send(bytes("PONG :{}\r\n".format(updates.split()[0]),'UTF-8'))
        commands = re.search(pattern, updates)
        if commands:
            logfile.write(updates + '\n')
            responder(commands, connection)