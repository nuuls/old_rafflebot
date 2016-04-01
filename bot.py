import socket
import time

from threading import Thread

from settings import HOST, PORT, IDENT, PASS, WHISPERPORT, WHISPERHOST


class Bot():
    s = socket.socket()
    ws = socket.socket()

    def __init__(self):
        self.last_msg_sent = time.time()
        self.uptime = time.time()
        self.on = True
        self.msgs_sent = 0

    def conn(self, s=socket.socket(), HOST=HOST, PORT=PORT):
        s.connect((HOST, PORT))
        s.send(("PASS " + PASS + "\r\n").encode("utf-8"))
        s.send(("NICK " + IDENT + "\r\n").encode("utf-8"))
        print("connected")
        return s

    def join(self, s, channel):
        time.sleep(2)
        s.send(("JOIN #" + channel + "\r\n").encode("utf-8"))
        print("joined " + channel)

    def send_raw(self, s, msg):
        s.send((msg + "\r\n").encode("utf-8"))
        print("sent: " + msg)

    def say(self, msg, channel):
        if self.on:
            if self.last_msg_sent + 1.7 < time.time():

                if msg.startswith("."):
                    space = ""
                else:
                    space = ". "

                msgTemp = "PRIVMSG #" + channel + " :" + space + msg
                self.s.send((msgTemp + "\r\n").encode("utf-8"))
                self.msgs_sent += 1
                try:
                    print("sent: " + msg)
                except:
                    print("message sent but could not print")
                self.last_msg_sent = time.time()


    def whisper(self, user, msg):
        msgTemp = "PRIVMSG #jtv :/w " + user + " " + msg
        self.send_raw(self.ws, msgTemp)

    def pong(self, s):
        need_to_pong = True
        readbuffer = ""
        while need_to_pong:

            try:
                readbuffer = readbuffer + (s.recv(1024)).decode("utf-8")
                temp = readbuffer.split("\r\n")
                readbuffer = temp.pop()

                for line in temp:
                    if line.startswith("PING"):
                        print(line)
                        self.send_raw(s, line.replace("PING", "PONG"))
            except:
                print("no longer ponging")
                need_to_pong = False

    def start(self):
        self.s = self.conn(self.s)
        self.ws = self.conn(self.ws, HOST=WHISPERHOST, PORT=WHISPERPORT)

        Thread(target=self.pong, args=(self.s,)).start()
        Thread(target=self.pong, args=(self.ws,)).start()







