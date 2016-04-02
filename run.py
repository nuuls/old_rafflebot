import sys
import random
import time

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
        self.raffle = {}

    def join_channels(self):

        for channel in CHANNEL:
            self.bot.join(self.rs, channel)
            self.raffle[channel] = False

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

    def reset_raffle(self, msg, channel):
        try:
            s = int(msg.split(" in ")[1].split(" ")[0])
            time.sleep(s / 4 + 3)
            self.raffle[channel] = False
        except:
            self.raffle[channel] = False


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
                    self.raffle[channel] = True
                    Thread(target=self.reset_raffle, args=((msg, channel))).start()

                if user in BOTNAMES and "raffle" in msg.lower() and "ends in" in msg.lower() and not " -"  in msg.lower() and self.raffle[channel]:
                    self.bot.say("!join " + random.choice(EMOTES), channel)
                    self.raffle[channel] = False

            else:
                print(line)


def start():
    main = Main()
    Thread(target=main.listen).start()
    Thread(target=main.read).start()
    main.join_channels()

start()
