import asyncio
import aiohttp
import json
import os
from discord.ext import ipc
from typing import Any, AsyncGenerator, Callable, Optional, Union, Dict


class StellaClient(ipc.Client):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.bot_id = kwargs.pop("bot_id", None)
        self._listeners = {}
        self.events = {}
        self.connect = None

    def __call__(self, bot_id: int) -> None:
        self.bot_id = bot_id

    def exception_catching_callback(self, task):
        if task.exception():
            task.print_stack()

    async def check_init(self) -> None:
        if not self.session:
            await self.init_sock()
        if not self.connect:
            self.connect = asyncio.create_task(self.connection())
            self.connect.add_done_callback(self.exception_catching_callback)

    def listen(self) -> Callable[[], Callable]:
        def inner(coro) -> Callable[..., None]:
            name = coro.__name__
            listeners = self.events.setdefault(name, [])
            listeners.append(coro)
        return inner

    def wait_for(self, event: str, request_id: str, timeout: Optional[int] = None) -> Any:
        future = asyncio.get_event_loop().create_future()
        listeners = self._listeners.setdefault("on_" + event, {})
        listeners.update({request_id: future})
        return asyncio.wait_for(future, timeout)

    async def do_request(self, endpoint: str, **data: Dict[str, Any]):
        await self.check_init()
        request_id = os.urandom(32).hex()
        payload = self.create_payload(endpoint, data)
        payload.update({"request_id": request_id})
        if self.websocket is None:
            raise Exception("Server is not connected")
        await self.websocket.send_json(payload)
        return await self.wait_for(endpoint, request_id)

    def create_payload(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Union[int, str, Dict[str, Any]]]:
        return {
            "endpoint": endpoint,
            "data": data,
            "headers": {"Authorization": self.secret_key, "Bot_id": self.bot_id}
        }

    async def request(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        return await self.do_request(endpoint, **kwargs)

    async def subscribe(self) -> Dict[str, Any]:
        data = await self.do_request("start_connection")
        if data.get("error") is not None:
            self.connect.cancel()
            raise Exception(f"Unable to get event from server: {data['error']}")
        return data

    async def get_response(self) -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            recv = await self.websocket.receive()
            if recv.type == aiohttp.WSMsgType.PING:
                await self.websocket.ping()
                continue
            elif recv.type == aiohttp.WSMsgType.PONG:
                continue
            elif recv.type == aiohttp.WSMsgType.CLOSED:
                await self.session.close()
                await asyncio.sleep(5)
                await self.init_sock()
                continue
            else:
                yield recv

    async def connection(self) -> None:
        async for data in self.get_response():
            try:
                respond = json.loads(data.data)
                event = "on_" + respond.pop("endpoint")
                value = respond.pop("response")
                if listeners := self._listeners.get(event):
                    if request_id := respond.get("request_id"):
                        if future := listeners.pop(request_id):
                            future.set_result(value)

                if events := self.events.get(event):
                    for coro in events:
                        await coro(value)
            except Exception as e:
                print("Ignoring error in gateway:", e)
