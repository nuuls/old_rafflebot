import socket
import time
from queue import Queue

from threading import Thread

from settings import HOST, PORT, IDENT, PASS, CHANNEL


class Bot():

    def __init__(self):
        self.last_msg_sent = time.time()
        self.q = Queue()

    def conn(self):
        s = socket.socket()
        s.connect((HOST, PORT))
        s.send(("PASS " + PASS + "\r\n").encode("utf-8"))
        s.send(("NICK " + IDENT + "\r\n").encode("utf-8"))
        print("connected")
        self.s = s
        Thread(target=self.listen).start()
        Thread(target=self.join_channels).start()
        Thread(target=self.ping).start()


    def join(self, channel):
        self.send_raw("JOIN #" + channel)
        print("joined " + channel)

    def join_channels(self):
        for channel in CHANNEL:
            self.join(channel)
            self.raffle[channel] = False
        time.sleep(5)

    def send_raw(self, msg):
        self.s.send((msg + "\r\n").encode("utf-8"))
        print("sent: " + msg)

    def say(self, msg, channel):
        if self.last_msg_sent + 1.7 < time.time():

            if msg.startswith("."):
                space = ""
            else:
                space = ". "

            msgTemp = "PRIVMSG #" + channel + " :" + space + msg
            self.send_raw(msgTemp)
            try:
                print("sent: " + msg)
            except:
                print("message sent but could not print")
            self.last_msg_sent = time.time()

    def ping(self):
        while True:
            try:
                while True:
                    time.sleep(60)
                    self.send_raw("PING")
            except:
                print("reconnecting in 30 seconds...")
                time.sleep(30)
                self.conn()


    def listen(self):
        while True:
            try:
                readbuffer = ""
                while True:

                    readbuffer = readbuffer + (self.s.recv(4096)).decode("utf-8", errors="ignore")
                    temp = readbuffer.split("\r\n")
                    readbuffer = temp.pop()

                    for line in temp:
                        if line.startswith("PING"):
                            print(line)
                            self.send_raw(line.replace("PING", "PONG"))
                        else:
                            self.q.put(line)
            except:
                print("reconnecting in 30 seconds...")
                time.sleep(30)
                self.conn()
