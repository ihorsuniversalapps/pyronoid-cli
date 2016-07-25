import curses
import os
import sys
import time


class Bat:
    def __init__(self, pos_y):
        self.x = 0
        self.pos_y = pos_y
        self.speed_x = 1
        self.width = 5

    def move_right(self):
        self.x += self.speed_x
        if self.x > 100:
            self.x = 100

    def move_left(self):
        self.x -= self.speed_x
        if self.x < 0:
            self.x = 0

    def draw(self, stdscr):
        stdscr.addstr(self.pos_y, self.x, 'T' * self.width, curses.color_pair(1))


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


class Scene:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        curses.cbreak()
        self.stdscr.nodelay(True)
        self.stdscr.keypad(1)

        rows, columns = self.stdscr.getmaxyx()

        self.ball = Ball(0, 0, rows - 2, columns - 2)
        self.bat = Bat(rows - 1)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    def loop(self):
        try:
            while True:
                try:
                    key = self.stdscr.getkey()
                    print key
                except Exception as e:  # in no delay mode getkey raise and exeption if no key is press
                    key = None

                if key == curses.KEY_LEFT:  # of we got a space then break
                    print 'left'
                    self.bat.move_left()
                if key == curses.KEY_RIGHT:  # of we got a space then break
                    print 'right'
                    self.bat.move_right()

                self.ball.move()
                self.ball.draw(self.stdscr)

                self.bat.draw(self.stdscr)

                self.stdscr.refresh()
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            curses.echo()
            curses.endwin()


def main():
    if os.isatty(sys.stdin.fileno()):
        print "PYRONOID v0.1"
    else:
        print "You should run application from Terminal."
        exit()

    scene = Scene()
    scene.loop()


if __name__ == '__main__':
    main()
