import random
import time
import sys

from threading import Thread

from bot import Bot
from settings import BOTNAMES, EMOTES

class Main:

    def __init__(self):

        self.bot = Bot()
        self.q = self.bot.q
        self.raffle = {}
        self.bot.raffle = self.raffle
        self.bot.conn()
        Thread(target=self.read).start()

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
            if s > 6:
                time.sleep(s / 4 - 1)
            self.raffle[channel] = True
            time.sleep(2)
            self.raffle[channel] = False
        except:
            self.raffle[channel] = False

    def checkForRaffle(self, msg, channel):
        try:
            tempmsg = msg.split(" ")
            for i in range(len(tempmsg)):
                if "points" in tempmsg[i]:
                    points = tempmsg[i - 1]

            if "-" not in points:
                self.raffle[channel] = True
                Thread(target=self.reset_raffle, args=((msg, channel))).start()
                print("joining")
            else:
                print("negative raffle")
        except:
            print("invalid raffle")




    def read(self):

        while True:
            line = self.q.get()

            if "PRIVMSG" in line:
                user = self.getUser(line)
                msg = self.getMessage(line)
                channel = self.getChannel(line)

                try:
                    if user in BOTNAMES:
                        print("%s # %s : %s" % (channel, user, msg))
                        sys.stdout.flush()


                    if "aff" in msg.lower() and " begun " in msg.lower():
                        self.checkForRaffle(msg, channel)

                    if "aff" in msg.lower() and " ends in " in msg.lower() and self.raffle[channel]:
                        self.bot.say("!join " + random.choice(EMOTES), channel)
                        self.raffle[channel] = False

                except:
                    pass

                if user == "twitchnotify" and " to " not in msg:
                    self.bot.say("!join " + random.choice(EMOTES), channel)

            else:
                print(line)

Main()

