import time
import sys
import socket
import random

from queue import Queue
from threading import Thread

from bot import Bot
from settings import ADMINS, CHANNEL, WHISPERHOST, WHISPERPORT, BOTNAMES

class Main:

    def __init__(self):

        self.bot = Bot()
        self.q = Queue()
        self.wq = Queue()
        self.rs = self.bot.conn()
        self.bot.start()
        self.wr = socket.socket()
        self.wr = self.bot.conn(s=self.wr, HOST=WHISPERHOST, PORT=WHISPERPORT)
        self.emotes = ["FeelsGoodMan", "PepeSquare", "PepeCopter", "nymnSmug", "pajaHappy", "FeelsGreatMan"]

    def join_channels(self):

        for channel in CHANNEL:
            self.bot.join(self.rs, channel)

    def listen(self):

        readbuffer = ""

        while True:
            readbuffer = readbuffer + (self.rs.recv(4096)).decode("utf-8", errors="ignore")
            temp = readbuffer.split("\r\n")
            readbuffer = temp.pop()

            for line in temp:
                self.q.put(line)

    def listen_whisper(self):

        readbuffer = ""
        self.bot.send_raw(self.wr, "CAP REQ :twitch.tv/commands")

        while True:
            readbuffer = readbuffer + (self.wr.recv(4096)).decode("utf-8", errors="ignore")
            temp = readbuffer.split("\r\n")
            readbuffer = temp.pop()

            for line in temp:
                self.wq.put(line)

    def getUser(self, line):
        seperate = line.split(":", 2)
        user = seperate[1].split("!", 1)[0]
        return user

    def getMessage(self, line):
        separate = line.split(":", 2)
        message = separate[2]
        return message

    def getChannel(self, line):
        seperate = line.split("#", 1)
        channel = seperate[1].split(" ")[0]
        return channel

    def read(self):

        while True:
            line = self.q.get()

            if line.startswith("PING"):
                self.rs.send((line.replace("PING", "PONG") + "\r\n").encode("utf-8"))
                print(line)
                print("ponged rs")

            elif "PRIVMSG" in line:
                user = self.getUser(line)
                msg = self.getMessage(line)
                channel = self.getChannel(line)

                try:
                    print((channel + "#" + user + ": " + msg).encode(sys.stdout.encoding, errors="ignore"))
                except:
                    pass

                if user in BOTNAMES and "raffle" in msg.lower() and "begun" in msg.lower() and " -" not in msg.lower():
                    time.sleep(3)
                    self.bot.say("!join " + random.choice(self.emotes), channel)


            else:
                print(line)

    def read_whisper(self):
        print("read whisper")
        while True:
            line = self.wq.get()

            if line.startswith("PING"):
                self.wr.send((line.replace("PING", "PONG") + "\r\n").encode("utf-8"))
                print(line)
                print("ponged ws")

            elif "WHISPER" in line:
                user = self.getUser(line)
                msg = self.getMessage(line)

                try:
                    print((user + ": " + msg).encode(sys.stdout.encoding, errors="ignore"))
                except:
                    pass

                if user in ADMINS:
                    self.checkCom(user, msg)
            else:
                print(line)


def start():
    main = Main()
    Thread(target=main.listen).start()
    Thread(target=main.read).start()
    Thread(target=main.listen_whisper).start()
    Thread(target=main.read_whisper).start()
    main.join_channels()
    #Thread(target=main.type).start()

start()
