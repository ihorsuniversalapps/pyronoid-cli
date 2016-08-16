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
MESSAGE_AWAITING_CONNECTION = "Awaiting connection from game controller..."
MESSAGE_GAME_OVER = "GAME OVER"


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

        if self.pos_y < 0.0:
            self.speed_y = -self.speed_y
            self.pos_y = 0.0

        if self.pos_x < 0.0:
            self.speed_x = -self.speed_x
            self.pos_x = 0.0

        if self.pos_x > self.max_x:
            self.pos_x = self.max_x
            self.speed_x = -self.speed_x

    def draw(self, stdscr):
        stdscr.addstr(int(self.pos_y), int(self.pos_x), 'O', curses.color_pair(2))

    def beat(self):
        self.speed_y = -self.speed_y


class GameController:
    def __init__(self, bat, f):
        self.bat = bat
        self.f = f

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
        self.f()


class Scene:
    GAME_STATE_AWAITING_GAMEPAD = 0
    GAME_STATE_RUNNING = 1
    GAME_STATE_GAME_OVER = 2

    @staticmethod
    def init_scene():
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()

    def restart_game(self):
        self.ball.pos_y = 0.0
        self.ball.pos_x = 0.0
        self.bat.pos_x = 0.0
        self.max_score = max(self.score, self.max_score)
        self.score = 0
        self.game_state = self.GAME_STATE_RUNNING

    def __init__(self, host):
        self.game_state = self.GAME_STATE_AWAITING_GAMEPAD
        self.score = 0
        self.max_score = 0

        print "Running game on {}".format(host)
        self.daemon = Pyro4.Daemon(host=host)

        self.stdscr = curses.initscr()
        self.init_scene()
        self.rows, self.columns = self.stdscr.getmaxyx()

        self.ball = Ball(0.0, 0.0, self.rows - 1.0, self.columns - 2.0)  # todo: check max width
        self.bat = Bat(self.rows - 1.0, self.columns - 2.0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        self.run_pyro_demon()

    def pyro_loop(self):
        self.daemon.requestLoop()
        print "Pyro loop finished."

    def check_collisions(self):
        ball_x = int(self.ball.pos_x)
        ball_y = int(self.ball.pos_y)
        bat_x = int(self.bat.pos_x)
        bat_x_max = int(self.bat.pos_x + self.bat.width)
        bat_y = int(self.bat.pos_y)

        if ball_y == bat_y:
            if bat_x <= ball_x <= bat_x_max:
                self.ball.beat()
                self.score += 1
                return

        if ball_y >= self.ball.max_y:
            self.game_state = self.GAME_STATE_GAME_OVER

    def draw_score(self):
        self.stdscr.addstr(1, 10, 'Score: {} Max Score: {}'.format(self.score, self.max_score), curses.color_pair(3))

    def draw_message(self, message):
        self.stdscr.addstr(int(self.rows / 2.0),
                           int(self.columns / 2.0 - len(message) / 2.0),
                           message,
                           curses.color_pair(3))

    def loop(self):
        try:
            while True:
                if self.game_state == self.GAME_STATE_AWAITING_GAMEPAD:
                    self.draw_message(MESSAGE_AWAITING_CONNECTION)
                elif self.game_state == self.GAME_STATE_RUNNING:
                    self.ball.move()
                    self.check_collisions()

                    self.stdscr.clear()
                    self.ball.draw(self.stdscr)
                    self.bat.draw(self.stdscr)
                else:
                    self.draw_message(MESSAGE_GAME_OVER)

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
        uri = self.daemon.register(GameController(self.bat, self.restart_game))
        ns.register("PYRONAME:local.pyronoid", uri)

        worker = threading.Thread(target=self.pyro_loop)
        worker.setDaemon(False)
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
