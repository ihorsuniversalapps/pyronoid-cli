# Real-time network communication between Python and Android

## The goal

Sometime we need to create some kind of fast communication between, for instance, IoT devices at home or control some server by your phone.

Everyone knows about client-server architecture in software developing. The client–server model is a distributed application structure that partitions tasks or workloads between the providers of a resource or service, called servers, and service requesters, called clients. Often clients and servers communicate over a computer network on separate hardware, but both client and server may reside in the same system. A server host runs one or more server programs which share their resources with clients. A client does not share any of its resources, but requests a server's content or service function. Clients therefore initiate communication sessions with servers which await incoming requests.

In this article I want to tell you about one of existence ways for near real-time client-server communication in Python. The most popular example for real-time communication is a chat application. But I will try to explain subject by creating small game like Arkanoid. It's a game where you control bat at the bottom of the screen. During game the ball will flying and beating of walls. The aim of the game is beat the ball by the bat the maximum number of beats as possible.

Application will consist two parts - terminal application which will draw ball and bat in text mode using ncurses library. The second part will be the game controller - application for Android that allows gamer to make swipes by a finger on the screen to control bat on the game server.

For communicating between game server and game controller we will use Pyro.

## What is Pyro

It is a library that enables you to build applications in which objects can talk to each other over the network, with minimal programming effort. You can just use normal Python method calls to call objects on other machines. Pyro is written in 100% pure Python and therefore runs on many platforms and Python versions, including Python 3.x.

Why Pyro? Because Pyro a very simple to use and pretty fast. On a typical networked system you can expect:

* a few hundred new proxy connections per second to one sever
* similarly, a few hundred initial remote calls per second to one server
* a few thousand remote method calls per second on a single proxy
* tens of thousands batched or oneway remote calls per second
* 10-100 Mb/sec data transfer

## What is ncurses

ncurses (new curses) is a programming library providing an application programming interface (API) that allows the programmer to write text-based user interfaces in a terminal-independent manner. It is a toolkit for developing "GUI-like" application software that runs under a terminal emulator. It also optimizes screen changes, in order to reduce the latency experienced when using remote shells.

## Lets begin or some boring theory

Let's begin creating the greatest game ever step-by-step.

First of all we should start game developing with preparing terminal. For working with terminal we would use ncurses, as I mentioned before. Also we should check if the application runs from terminal. For check this we should execute:

```python
if not os.isatty(sys.stdin.fileno()):
    print "You should run application from Terminal."
    exit()
```

Function *os.isatty(fd)* checks if the file descriptor*(fd)* is open and connected to tty(-like) device. *sys.stdin.fileno()* returns the integer “file descriptor” that is used by the underlying implementation to request I/O operations from the operating system.

Next thing that we should do after we sure that we are running on terminal - initializing ncurses library. Run next code:

```python
stdscr = curses.initscr()
curses.noecho()
curses.curs_set(0)
curses.cbreak()
```

Now, stdscr variable will contains the object represents our terminal. For instance, we can get max x and y coordinates of our terminal.

```python
rows, columns = self.stdscr.getmaxyx()
```

The max rows and colums amount will be helpful for us when we will calculate collisions for ball and bat.

Also we need to setup a color scheme for our game. During displaying symbol or string on the screen we should use a color pairs - foreground and background colors. Each color pair has integer identifier, so we can make something like this::

```python
COLOR_BAT = 1
COLOR_BALL = 2
COLOR_INTERFACE = 3

curses.start_color()
curses.init_pair(COLOR_BAT, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(COLOR_BALL, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(COLOR_INTERFACE, curses.COLOR_RED, curses.COLOR_BLACK)
```

And every time when we want to display some text we can call *addstr()* method:

```python
stdscr.addstr(int(self.pos_y), int(self.pos_x), 'O', curses.color_pair(COLOR_BALL))
```

As you know, each game should have a loop. Loop - it's a infinite cycle that runs forever. Each loop the game should move ball, receive and process data from game controller, clean, draw ball, bat and interface on the screen.

## Writing Game Server

## Writing Game Controller

## In the end

## Links

1. [Pyro official documentation](https://pythonhosted.org/Pyro4/)
2. [ncurses Wikipedia](https://en.wikipedia.org/wiki/Ncurses)
