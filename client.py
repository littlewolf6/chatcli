import asyncio
import click
from aioconsole import ainput
import json


class Client:
    def __init__(self, host, port, default_username: str = None):
        self.host = host
        self.port = port
        self.default_username = default_username
        self.reader = None
        self.writer = None

    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def _send(self, message: str):
        self.writer.write(message.encode() + b'\n')
        await self.writer.drain()

    async def _receive(self):
        data = await self.reader.readline()
        if data:
            raw_message = data.decode().strip()
            try:
                return json.loads(raw_message)
            except json.JSONDecodeError:
                return {"raw_message": raw_message} if raw_message else None
        return None

    async def run(self):
        await self._connect()
        if self.default_username:
            await self._process_command("/setname", self.default_username)

        user_input_task = asyncio.create_task(self._user_input_loop())

        await self._server_output_loop()

        user_input_task.cancel()
        self.close()

    async def _server_output_loop(self):
        while True:
            try:
                message = await self._receive()
            except ConnectionError:
                print('Disconnected from server')
                break

            if not message:
                print('Disconnected from server')
                break

            await self._process_server_output(message)

    async def _user_input_loop(self):
        while True:
            _input = await ainput()

            await self._process_input(_input)

    async def _process_server_output(self, message: dict):
        if message.get("type") == "message":
            sender = message.get("data", None)["source"]
            content = message["data"]["message"]
            print(f"{sender}: {content}")
        else:
            print(f'Raw message: {message["raw_message"]}')

    async def _process_input(self, _input: str):
        if _input[0] == '/':
            split_str = _input.split(" ", 1)
            command, rest = split_str if len(split_str) > 1 else (split_str[0], "")
            await self._process_command(command, rest)

        else:
            await self._send(f'{{"type": "message", "data": "{_input}"}}')

    async def _process_command(self, command: str, rest: str):
        match command:
            case "/setname":
                username = rest.strip(" ")
                await self._send(f'{{"type": "set-name", "data": "{username}"}}')
            case "/history":
                await self._send(f'{{"type": "history", "data": ""}}')
            case "/users":
                await self._send(f'{{"type": "users", "data": ""}}')
            case _:
                print("INVALID COMMAND!")

    def close(self):
        if self.writer:
            self.writer.close()


@click.command()
@click.option('--host', "host_address", type=click.STRING, help='Host address', prompt=True)
@click.option('--port', "host_port", type=click.INT, help='Host port', prompt=True)
@click.option('--user', 'username', type=click.STRING, default=None, help="Username", prompt=True)
def main(host_address, host_port, username):
    client = Client(host_address, host_port, default_username=username)
    asyncio.run(client.run())


if __name__ == "__main__":
    main()
