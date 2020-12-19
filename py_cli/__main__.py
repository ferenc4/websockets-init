#!/usr/bin/env python

# WS client example

import asyncio
from uuid import uuid4

import websockets
from websockets.protocol import State


async def one_to_one(uri: str):
    async with websockets.connect(uri) as websocket:
        request = f"Client {uuid4()}"
        print(f"> {request}")
        await websocket.send(request)

        response = await websocket.recv()
        print(f"< {response}")


async def one_to_n(uri: str):
    async with websockets.connect(uri) as websocket:
        request = f"client-{uuid4()}"
        print(f"> {request}")
        await websocket.send(request)

        async for response in websocket:
            print(f"< {response}")


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(one_to_one("ws://localhost:8765/"))
    loop.run_until_complete(one_to_one("ws://localhost:8765/one_to_one"))
    loop.run_until_complete(one_to_n("ws://localhost:8765/one_to_n"))
    try:
        loop.run_until_complete(one_to_one("ws://localhost:8765/doesntexist"))
    except websockets.exceptions.ConnectionClosedError:
        print("As expected, no connection was made to missing API.")


if __name__ == "__main__":
    main()
