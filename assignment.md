# Assignment
Your task is to implement a network chat program based on TCP/IP communication.
There will be two individual programs with a command-line interface - a server and a client.

The server will wait for connections from clients and facilitace communication between them.
Once a client connects, it will start a new thread that will handle that client - send their messages
to all other clients, allow them to change their name etc. Once the client disconnects, the server
will clean up after them and let the other connected clients know.

The client will connect to a server with some address and port, and then it will receive messages
from other chat participants. It will also be able to send messages, of course.

You should implement the client first, and debug it using the provided test server (see Kelvin
for more information).

## Client
Create a chat client with CLI parameters `server` and `port`.
1) Connect to a TCP server at `<server>:<port>`.
2) Create a thread that will read lines from the standard input (terminal) and send them to the server.
3) Read chat messages from the server and print them to standard output (terminal).
4) If the server disconnects, print "Server disconnected" and exit the program.

1. Connect to a TCP server at `<server>:<port>`.
2. Create a thread that will read lines from the standard input (terminal) and send them to the server.
3. Read chat messages from the server and print them to standard output (terminal).
4. If the server disconnects, print "Server disconnected" and exit the program.

### Protocol
The clients will communicate with the server via TCP/IP. They will exchange messages.
Each message is a JSON-encoded dictionary terminated with a newline ("\n").
Each message must have two keys - "type" and "data".
"type" specifies what kind of message it is, "data" contains message-specific data.

You must implement several types of messages.
The user of the chat client decides what type of message will be sent by using various commands.

Client -> server messages:
1) Chat message: `{"type": "message", "data": <content of chat message>}`
   Sends a new message to the chat.
   Send this message if the user writes a line that does not begin with a slash ("/").
2) Change name message: `{"type": "set-name", "data": <username>}`
   Sets the username of the current user on the server.
   Send this message if the user writes "/setname <username>".
3) Display server history message: `{"type": "history", "data": ""}`
   Asks the server to send you the message history.
   Send this message if the user writes "/history".
4) Display connected users message: `{"type": "users", "data": ""}`
   Asks the server to send you a list of currently connected users.
   Send this message if the user writes "/users".

Server -> client messages:
1) New chat message: `{"type": "message", "data": {"source": <username of sender>, "message": <content of chat message>}}`
   The server will send you this message if `data["source"]` sent a chat message containing `data["message"]`.

Remember that TCP is a stream-oriented protocol, you must handle splitting of the stream
into messages terminated by newlines yourself.

**Your solution MUST work even if you use `socket.recv(1)` to read data. But it should also work
for socket.recv(256), socket.recv(512), etc.**

Use e.g. the `click` or `typer` library to create a command line interface.
You can use e.g. the `colorama` library for colored output.

Example:
```
$ python3 client.py 127.0.0.1 5555
[Server]: 127.0.0.1:57354 has entered the chat
hello
127.0.0.1:57354: hello
/setname Kobzol
[Server]: 127.0.0.1:57354 renamed to Kobzol
hello
Kobzol: hello
```

## Server
Create a chat server that will implement the messages described above.
You can also use the test server for inspiration how should it react to the individual messages
(but it should be obvious and there are no strict rules for the behaviour, you can implement it
however you like).

Make sure to handle all errors gracefully and also to limit the number of chat messages and
connected users to avoid running out of memory.

Example:
$ python3 server.py --port 5555
[Server]: 127.0.0.1:57354 has entered the chat
hello
127.0.0.1:57354: hello
/setname Kobzol
[Server]: 127.0.0.1:57354 renamed to Kobzol
hello
Kobzol: hello

Use e.g. the `click` or `typer` library to create a command line interface.
You can use e.g. the `colorama` library for colored output.

## Bonus
- Start a Flask server inside the chat server process. The server will display users connected
to the chat and their messages.
- Implement client and server using `async` coroutines
