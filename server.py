import asyncio
import click
import json
from dataclasses import dataclass
from collections import deque


@dataclass
class ClientConnectionContext:
    client_name: str
    writer: asyncio.StreamWriter


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_contexts: list[ClientConnectionContext] = []
        self.output_history: deque[str] = deque(maxlen=20)

    async def _send(self, writer: asyncio.StreamWriter, message: str, cache_history=True):
        writer.write(message.encode() + b'\n')
        await writer.drain()

        if cache_history:
            self.output_history.append(message)

    async def _receive(self, reader: asyncio.StreamReader):
        data = await reader.readline()
        raw_message = data.decode().strip()
        try:
            return json.loads(raw_message)
        except json.JSONDecodeError:
            return {"raw_message": raw_message} if raw_message else None

    async def run(self):
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        print(f'Server listening on {self.host}:{self.port}')

        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer_name = writer.get_extra_info("peername")
        context = ClientConnectionContext(f"{peer_name[0]}:{peer_name[1]}", writer)
        self.client_contexts.append(context)

        print(f"Client connected: {context.client_name}")
        await self._broadcast_message(
            self.to_server_output_format(f"\"{context.client_name}\" has entered the chat")
        )

        try:
            while True:
                message = await self._receive(reader)

                if not message:
                    break

                await self._process_client_output(message, context)

        except ConnectionError:
            pass

        await self._remove_client(context)

        writer.close()

    async def _process_client_output(self, message: dict, context: ClientConnectionContext):
        match message.get("type"):
            case "message":
                print(f"{context.client_name}: {message['data']}")
                await self._broadcast_message(
                    self.to_server_output_format(message["data"], context),
                    to_ignore=context,
                )

            case "set-name":
                await self._rename_client(context, message["data"])

            case "history":
                await self._send_history(context)

            case "users":
                await self._send_client_list(context)

            case _:
                print(f'({context.client_name}): {message}')

    @staticmethod
    def to_server_output_format(message: str, context: ClientConnectionContext = None) -> str:
        return json.dumps({"type": "message",
                           "data":
                               {"source": context.client_name if context else "[Server]",
                                "message": message
                                }
                           })

    async def _rename_client(self, context: ClientConnectionContext, new_name: str):
        server_message = f"\"{context.client_name}\" renamed to {new_name}"
        context.client_name = new_name
        print(server_message)
        await self._broadcast_message(
            self.to_server_output_format(server_message)
        )

    async def _send_history(self, context: ClientConnectionContext):
        for message in self.output_history:
            await self._send(context.writer, message, cache_history=False)

    async def _send_client_list(self, context: ClientConnectionContext):
        await self._send(context.writer,
                         self.to_server_output_format(
                             f"List of users\n\t{[_context.client_name for _context in self.client_contexts]}"),
                         cache_history=False)

    async def _broadcast_message(self, message: str,
                                 to_ignore: ClientConnectionContext = None,
                                 cache_history=True):
        if cache_history:
            self.output_history.append(message)

        for context in self.client_contexts:
            if to_ignore and (context == to_ignore):
                continue

            try:
                await self._send(context.writer, message, cache_history=False)
            except ConnectionError:
                await self._remove_client(context)

    async def _remove_client(self, context: ClientConnectionContext):
        self.client_contexts.remove(context)
        context.writer.close()
        await self._broadcast_message(
            self.to_server_output_format(f"\"{context.client_name}\" disconnected")
        )


@click.command()
@click.option('--host', "host_address", type=click.STRING, default="localhost", help='Host address', prompt=True)
@click.option('--port', "host_port", type=click.INT, default=5555, help='Host port', prompt=True)
def main(host_address: str, host_port: int):
    server = Server(host_address, host_port)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
