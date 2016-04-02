import sys
import random

from queue import Queue
from threading import Thread

from bot import Bot
from settings import CHANNEL, BOTNAMES, EMOTES

class Main:

    def __init__(self):

        self.bot = Bot()
        self.q = Queue()
        self.rs = self.bot.conn()
        self.bot.start()
        self.raffle = False

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

    def join(self, channel, msg):
        try:
            #s = int(msg.split(" in ")[1].split(" ")[0])
            self.bot.say("!join " + random.choice(EMOTES), channel)
        except Exception as e:
            print(e)

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

                if user in BOTNAMES and "raffle" in msg.lower() and "begun" in msg.lower() and not " -"  in msg.lower():
                    self.raffle = True

                if user in BOTNAMES and "raffle" in msg.lower() and "ends in" in msg.lower() and not " -"  in msg.lower() and self.raffle:
                    Thread(target=self.join, args=((channel, msg))).start()
                    self.raffle = False

            else:
                print(line)


def start():
    main = Main()
    Thread(target=main.listen).start()
    Thread(target=main.read).start()
    main.join_channels()

start()
