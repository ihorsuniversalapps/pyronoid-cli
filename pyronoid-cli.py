#!/usr/bin/python

import curses
import os
import sys
import threading
import time

import Pyro4
from Pyro4.errors import NamingError


class Bat:
    def __init__(self, pos_y, max_x):
        self.x = 0
        self.pos_y = pos_y
        self.speed_x = 2
        self.width = 10
        self.max_x = max_x - self.width - 1

    def move_right(self):
        self.x += self.speed_x
        if self.x > self.max_x:
            self.x = self.max_x

    def move_left(self):
        self.x -= self.speed_x
        if self.x < 0:
            self.x = 0

    def set_post(self, percent):
        self.x = int(percent * self.max_x)
        if self.x > self.max_x:  # todo: move check outside
            self.x = self.max_x

    def draw(self, stdscr):
        stdscr.addstr(self.pos_y, self.x, '@' * self.width, curses.color_pair(1))


class Ball:
    def __init__(self, initial_y=0, initial_x=0, max_y=0, max_x=0):
        self.y = initial_y
        self.x = initial_x
        self.speed_y = 1
        self.speed_x = 1
        self.max_y = max_y
        self.max_x = max_x

    def move(self):
        self.y += self.speed_y
        self.x += self.speed_x

        if self.y < 0:
            self.speed_y = -self.speed_y
            self.y = 0

        if self.y > self.max_y:
            self.speed_y = -self.speed_y
            self.y = self.max_y

        if self.x < 0:
            self.speed_x = -self.speed_x
            self.x = 0

        if self.x > self.max_x:
            self.x = self.max_x
            self.speed_x = -self.speed_x

    def draw(self, stdscr):
        stdscr.addstr(self.y, self.x, 'O', curses.color_pair(1))


class BatMover:
    def __init__(self, bat):
        self.bat = bat

    @Pyro4.expose
    def move(self, pos):
        self.bat.set_post(pos)


class Scene:
    def init_scene(self):
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()
        self.stdscr.nodelay(True)
        self.stdscr.keypad(1)

    def __init__(self):
        self.stdscr = curses.initscr()
        self.init_scene()
        rows, columns = self.stdscr.getmaxyx()

        self.ball = Ball(0, 0, rows - 2, columns - 2)
        self.bat = Bat(rows - 1, columns - 2)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

        self.daemon = Pyro4.Daemon(host="192.168.10.104")  # todo: determine address or get from params
        self.run_pyro_demon()

    def pyro_loop(self):
        self.daemon.requestLoop()
        print "Loop ends"

    def loop(self):
        try:
            while True:
                self.ball.move()

                self.stdscr.clear()
                self.ball.draw(self.stdscr)
                self.bat.draw(self.stdscr)
                self.stdscr.refresh()

                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            self.finish()

    def finish(self):
        self.daemon.close()
        self.restore_terminal_state()

    @staticmethod
    def restore_terminal_state():
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def run_pyro_demon(self):
        ns = Pyro4.locateNS()
        uri = self.daemon.register(BatMover(self.bat))
        ns.register("PYRONAME:local.pyronoid", uri)

        worker = threading.Thread(target=self.pyro_loop)
        worker.setDaemon(True)
        worker.start()


def main():
    if os.isatty(sys.stdin.fileno()):
        print "PYRONOID v0.1"
    else:
        print "You should run application from Terminal."
        exit()

    try:
        scene = Scene()
        scene.loop()
    except NamingError as e:
        Scene.restore_terminal_state()
        print "Name server error: " + e.message


if __name__ == '__main__':
    main()

# todo: remove this shit
# # self.daemon.events(self.daemon.sockets)
# socks = self.daemon.sockets
# ins, outs, exs = select.select(socks, [], [], 0.1)
# for s in socks:
#     if s in ins:
#         # self.daemon.handleRequest(s)
#         self.daemon.events(self.daemon.sockets)
