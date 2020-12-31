import asyncio
import json
import logging
import sys
from threading import Thread
from typing import Union

from websockets import serve

logger = logging.getLogger(__name__)
TIMER_INCREMENT_SECONDS = 5


class GenericServer:
    def start(self, host, port: int):
        raise NotImplementedError()


class Game:
    def __init__(self, users: []):
        self.users = users


class WsServer(GenericServer):
    def __init__(self):
        self.online_users = set()
        self.online_connections = set()
        self.connections_by_user = dict()
        self.users_by_connection = dict()
        self.games = []
        self.games_by_user = dict()
        self.queued_up_users = set()

    def start(self, host: str, port: int):
        start_server = serve(lambda websocket, path: self.on_connection(websocket, path), host, port)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()

    async def on_connection(self, websocket, path):
        await self.register(websocket)
        message_idx = 0
        last_message = None
        try:
            async for message in websocket:
                last_message = message
                print(f"{websocket.__hash__()} #{message_idx + 1} Received < {message} >")
                data = json.loads(message)
                if message_idx == 0:
                    await self.register_user(websocket, data)
                else:
                    print(f"unsupported event: < {data} >")
                message_idx += 1
        except:
            logging.exception(f"An exception occurred while processing message < {last_message} >.",
                              exc_info=sys.exc_info())
            self.fail_connection(websocket)
        finally:
            print("unregistering")
            await self.unregister(websocket)

    def fail_connection(self, websocket):
        websocket.fail_connection(1011, f"An error occurred, ending connection.")

    async def notify_game_start(self, game):
        # asyncio.wait doesn't accept an empty list
        task_futures = []
        subscribers = []
        for user in game.users:
            websocket = self.connections_by_user[user]
            subscribers.append(websocket)
            to_send = json.dumps({"type": "queue_lobby", "state": "success"})
            print(f"Sending to user < {user} > the message < {to_send} >")
            task_futures.append(websocket.send(to_send))
        await asyncio.wait(task_futures)
        await TurnTimer(game, self, subscribers, 60).run()

    async def register(self, websocket):
        self.online_connections.add(websocket)

    async def register_user(self, websocket, first_message):
        user = first_message["user"]
        assert user
        if user in self.online_users:
            raise Exception(f"User <{user}> is already online.")

        self.online_users.add(user)
        self.connections_by_user[user] = websocket
        self.users_by_connection[websocket] = user
        if len(self.queued_up_users) > 0:
            p1 = self.queued_up_users.pop()
            p2 = user
            new_game = Game([p1, p2])
            self.games.append(new_game)
            self.games_by_user[p1] = new_game
            self.games_by_user[p2] = new_game
            await self.notify_game_start(new_game)
        else:
            self.queued_up_users.add(user)

    async def unregister(self, websocket):
        self.online_connections.discard(websocket)
        if websocket in self.users_by_connection:
            user: Union[str, None] = self.users_by_connection.pop(websocket)
            self.online_users.discard(user)
            self.connections_by_user.pop(user)
            self.queued_up_users.discard(user)
            affected_game: Game = self.games_by_user.pop(user)
            is_no_one_playing = True
            for user_in_game in affected_game.users:
                if user_in_game in self.online_users:
                    is_no_one_playing = False
            if is_no_one_playing:
                self.games.remove(affected_game)


class TurnTimer(Thread):
    def __init__(self, game, ws_server, websockets: [], total_seconds):
        super().__init__()
        self.game = game
        self.ws_server = ws_server
        self.websockets: [] = websockets
        self.total_seconds = total_seconds

    async def run(self):
        for i in range(0, self.total_seconds, TIMER_INCREMENT_SECONDS):
            ticker_msg = json.dumps({
                "type": "time",
                "ticker": self.total_seconds - i
            })
            all_to_remove = []
            for websocket in self.websockets:
                try:
                    print(f"Sending to user < {self.ws_server.users_by_connection[websocket]} > "
                          f"the message < {ticker_msg} >")
                    await websocket.send(ticker_msg)
                except:
                    all_to_remove.append(websocket)
                    self.ws_server.fail_connection(websocket)
                    await self.ws_server.unregister(websocket)
            for to_remove in all_to_remove:
                self.websockets.remove(to_remove)
            if not self.websockets:
                break
            await asyncio.sleep(TIMER_INCREMENT_SECONDS)
