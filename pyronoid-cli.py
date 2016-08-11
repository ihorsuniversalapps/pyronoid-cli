#!/usr/bin/python
import argparse
import curses
import os
import sys
import threading
import time

import Pyro4
from Pyro4.errors import NamingError

GAME_LOOP_TIMEOUT = 0.06  # 60 fps
BAT_WIDTH = 10
BALL_INITIAL_SPEED = 1.0


class Bat:
    def __init__(self, pos_y, max_x):
        self.pos_x = 0.0
        self.pos_y = pos_y
        self.width = BAT_WIDTH
        self.max_x = max_x - self.width - 1.0  # todo: check

    def set_position(self, percent):
        self.pos_x = int(percent * self.max_x)
        if self.pos_x > self.max_x:
            self.pos_x = self.max_x

    def draw(self, stdscr):
        stdscr.addstr(int(self.pos_y), int(self.pos_x), '@' * self.width, curses.color_pair(1))


class Ball:
    def __init__(self, initial_y=0.0, initial_x=0.0, max_y=0.0, max_x=0.0):
        self.pos_y = initial_y
        self.pos_x = initial_x
        self.speed_y = BALL_INITIAL_SPEED
        self.speed_x = BALL_INITIAL_SPEED
        self.max_y = max_y
        self.max_x = max_x

    def move(self):
        self.pos_y += self.speed_y
        self.pos_x += self.speed_x

        # todo: y pos checking should be removed according to
        if self.pos_y < 0.0:
            self.speed_y = -self.speed_y
            self.pos_y = 0.0

        if self.pos_y > self.max_y:
            self.speed_y = -self.speed_y
            self.pos_y = self.max_y

        if self.pos_x < 0.0:
            self.speed_x = -self.speed_x
            self.pos_x = 0.0

        if self.pos_x > self.max_x:
            self.pos_x = self.max_x
            self.speed_x = -self.speed_x

    def draw(self, stdscr):
        stdscr.addstr(int(self.pos_y), int(self.pos_x), 'O', curses.color_pair(2))


class GameController:
    def __init__(self, bat):
        self.bat = bat

    @Pyro4.expose
    def move_bat(self, pos):
        """
        Moves bat.
        :param pos: Percent position, e.g. 50.0% means half of terminal width.
        :return: None
        """
        self.bat.set_position(pos)

    @Pyro4.expose
    def restart_game(self):
        """
        Restarts game if it was game over.
        :return: None
        """
        pass


class Scene:
    @staticmethod
    def init_scene():
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()

    def __init__(self, host):
        print "Running game on {}".format(host)
        self.daemon = Pyro4.Daemon(host=host)

        self.stdscr = curses.initscr()
        self.init_scene()
        rows, columns = self.stdscr.getmaxyx()

        self.ball = Ball(0.0, 0.0, rows - 2.0, columns - 2.0)  # todo: check max width
        self.bat = Bat(rows - 1.0, columns - 2.0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.run_pyro_demon()

    def pyro_loop(self):
        self.daemon.requestLoop()
        print "Pyro loop finished."

    def check_collisions(self):
        # todo: Collision to bat
        # todo: Collision to bottom
        pass

    def draw_score(self):
        # todo: draw score - amount of succeed reflections
        # todo: draw max score
        # todo: draw game time
        pass

    def loop(self):
        try:
            while True:
                self.ball.move()
                self.check_collisions()

                self.stdscr.clear()
                self.ball.draw(self.stdscr)
                self.bat.draw(self.stdscr)
                self.draw_score()
                self.stdscr.refresh()

                time.sleep(GAME_LOOP_TIMEOUT)
        except KeyboardInterrupt:
            pass
        finally:
            self.finish()

    def finish(self):
        self.daemon.shutdown()
        self.restore_terminal_state()
        print "Pyro daemon is closed."

    @staticmethod
    def restore_terminal_state():
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def run_pyro_demon(self):
        ns = Pyro4.locateNS()
        uri = self.daemon.register(GameController(self.bat))
        ns.register("PYRONAME:local.pyronoid", uri)

        worker = threading.Thread(target=self.pyro_loop)
        worker.setDaemon(True)
        worker.start()


def main():
    parser = argparse.ArgumentParser(description='Pyronoid v0.1- Arkanoid clone game')
    parser.add_argument('host', metavar='H', type=str, nargs=1, help='Host name (external machine address)')

    args = parser.parse_args()

    if not os.isatty(sys.stdin.fileno()):
        print "You should run application from Terminal."
        exit()

    try:
        scene = Scene(args.host[0])
        scene.loop()
    except NamingError as e:
        Scene.restore_terminal_state()
        print "Name server error: " + e.message


if __name__ == '__main__':
    main()
