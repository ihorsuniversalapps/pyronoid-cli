# Real-time network communication between Python and Android

## The goal

Sometime we need to create some kind of fast communication between, for instance, IoT devices at home or control some server by your phone.

Everyone knows about client-server architecture in software developing. The client–server model is a distributed application structure that partitions tasks or workloads between the providers of a resource or service, called servers, and service requesters, called clients. Often clients and servers communicate over a computer network on separate hardware, but both client and server may reside in the same system. A server host runs one or more server programs which share their resources with clients. A client does not share any of its resources, but requests a server's content or service function. Clients therefore initiate communication sessions with servers which await incoming requests.

In this article I want to tell you about one of ways for near real-time client-server communication in Python. The most popular example for real-time communication is a chat application. But I will try to explain by creating small game like Arkanoid. Application will be consist of two pars - terminal application which will draw ball and bat in text mode using ncurses library. The second part will be game controller - application for Android that allow gamer swipes by finger on the screen to control bat on game server.

For communicating between game server and game controller we will use Pyro.

## What is Pyro

It is a library that enables you to build applications in which objects can talk to each other over the network, with minimal programming effort. You can just use normal Python method calls to call objects on other machines. Pyro is written in 100% pure Python and therefore runs on many platforms and Python versions, including Python 3.x.

## What is ncurses

ncurses (new curses) is a programming library providing an application programming interface (API) that allows the programmer to write text-based user interfaces in a terminal-independent manner. It is a toolkit for developing "GUI-like" application software that runs under a terminal emulator. It also optimizes screen changes, in order to reduce the latency experienced when using remote shells.

## Lets begin or some boring theory

## Writing Game Server

## Writing Game Controller

## In the end

## Links

1. [Pyro official documentation](https://pythonhosted.org/Pyro4/)
2. [ncurses Wikipedia](https://en.wikipedia.org/wiki/Ncurses)
