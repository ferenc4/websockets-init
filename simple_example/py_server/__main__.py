#!/usr/bin/env python

# WS server example

import asyncio
import websockets
from py_server.routes import handle_routes


def main():
    start_server = websockets.serve(handle_routes, host="localhost", port=8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
