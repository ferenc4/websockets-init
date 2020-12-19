from time import sleep

from websockets import WebSocketServerProtocol


async def home_page_api(websocket, path: str):
    await websocket.send("This is the home page API. It ain't much, but its honest work.")


async def one_to_one_api(websocket: WebSocketServerProtocol, path: str):
    print(f"path={path}")
    name = await websocket.recv()
    print(f"< {name}")
    await greet(websocket, name, 1, 1)
    await websocket.close()


async def one_to_n_api(websocket: WebSocketServerProtocol, path: str):
    print(f"path={path}")
    name = await websocket.recv()
    idx = 1
    await greet(websocket, name, idx, 3)
    sleep(1)
    idx += 1
    await greet(websocket, name, idx, 3)
    sleep(1)
    idx += 1
    await greet(websocket, name, idx, 3)
    await websocket.close()


async def greet(websocket, name, msg_index, msg_count):
    print(f"< {name}")
    greeting = f"Hello {name}! {msg_index}/{msg_count}"
    print(f"> {greeting}")
    await websocket.send(greeting)

__ROUTES = {
    "/": home_page_api,
    "/one_to_one": one_to_one_api,
    "/one_to_n": one_to_n_api
}


async def handle_routes(websocket: WebSocketServerProtocol, path: str):
    api_method = __ROUTES.get(path)
    if api_method is None:
        print(f"The method for path <{path}> does not exist.")
        websocket.fail_connection(1011, f"The method for path <{path}> does not exist.")
    else:
        await api_method(websocket=websocket, path=path)
