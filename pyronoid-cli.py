import curses
import time
import random

import sys, os
if os.isatty(sys.stdin.fileno()):
    print "PYRONOID v0.1"
    pass
else:
    print "You should run application from Terminal."
    exit()


stdscr = curses.initscr()
curses.noecho()
curses.curs_set(0)
curses.cbreak()

rows, columns = stdscr.getmaxyx()

curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

try:
    while True:
        y = random.choice(range(1, int(rows)))
        x = random.choice(range(1, int(columns)))
        stdscr.addstr(y - 1, x - 1, random.choice(['*', '+', '@']), curses.color_pair(1))
        stdscr.refresh()
        time.sleep(0.01)
except KeyboardInterrupt:
    pass

curses.nocbreak()
curses.echo()
curses.endwin()
