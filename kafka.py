#!/usr/bin/env python3

from maelstrom import Body, Node, Request
import asyncio
from collections import defaultdict

if __name__ == "__main__":
    node = Node()

    async def write(key, value):
        await node.rpc("lin-kv", {"type": "write", "key": key, "value": value})

    async def read(key):
        response = await node.rpc("lin-kv", {"type": "read", "key": key})
        return response.get("value")

    async def cas(key, old, new):
        response = await node.rpc("lin-kv", {"type":"cas", "key":key, "from":old, "to":new})
        return response.get("type") == "cas_ok" or ((response.get("type") == "error") and (response.get("code") == 20))


    @node.handler
    async def send(req: Request) -> Body:
        key = req.body["key"]
        msg = req.body["msg"]

        tail_key = f"{key}-tail"
        tail = None

        while(True):
            tail = await read(tail_key)
            if tail is None:
                tail = 0
                await write(tail_key, tail)
            if (await cas(tail_key, tail, tail + 1)):
                break

        await write(f"{key}-{tail}", msg)
        return {"type": "send_ok", "offset": tail}
        
    @node.handler
    async def poll(req: Request) -> Body:
        offsets = req.body["offsets"]

        msgs = {}
        for key, offset in offsets.items():
            value = await read(f"{key}-{offset}")
            if value is not None:
                msgs[key] = [[offset, value]]
            else:
                msgs[key] = []

        return {"type": "poll_ok", "msgs": msgs}

    @node.handler
    async def commit_offsets(req: Request) -> Body:
        offsets = req.body["offsets"]
        for key, offset in offsets.items():
            await write(key + "-offset", offset)

        return {"type": "commit_offsets_ok"}

    @node.handler
    async def list_committed_offsets(req: Request) -> Body:
        keys = req.body["keys"]
        results = await asyncio.gather(*(read(key + "-offset") for key in keys))
        return {
            "type": "list_committed_offsets_ok",
            "offsets": {key: res or 0 for key, res in zip(keys, results)}
        }

    node.run()
