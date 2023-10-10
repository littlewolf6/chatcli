# CLI chat

Simple CLI chat **server-client** application written in Python.

This approach uses **asyncio** built-in package instead of sockets.

**Multiple clients** can join server and can **use some user commands**.

## Requirements
- **Python 3.10** or higher
- **Click**, python package for arguments
- **aioconsole**, python package for asynchronous console

## Server arguments
- --host, ip address
- --port, port

## Client arguments
- --host, host ip address
- --port, port
- --user, username

## Client commands
- /setname, set new username
- /history, last n chat messages
- /users, list of connected users

