#!/usr/bin/env python3

from maelstrom import Body, Node, Request
import asyncio
from collections import defaultdict

if __name__ == "__main__":
    node = Node()
    logs: dict[str, list[int]] = defaultdict(list)
    committed_offsets: dict[str, int] = defaultdict(int)

    @node.handler
    async def send(req: Request) -> Body:
        key = req.body["key"]
        msg = req.body["msg"]
        offset = len(logs[key])
        logs[key].append(msg)
        return {"type": "send_ok", "offset": offset}

    @node.handler
    async def poll(req: Request) -> Body:
        offsets = req.body["offsets"]
        msgs = {}

        for key, offset in offsets.items():
            if key not in msgs:
                msgs[key] = []
            existing_msgs = logs[key]
            for i in range(offset, len(existing_msgs)):
                msgs[key].append([i, existing_msgs[i]])

        return {"type": "poll_ok", "msgs": msgs}

    @node.handler
    async def commit_offsets(req: Request) -> Body:
        offsets = req.body["offsets"]
        for key, offset in offsets.items():
            committed_offsets[key] = offset

        return {"type": "commit_offsets_ok"}

    @node.handler
    async def list_committed_offsets(req: Request) -> Body:
        keys = req.body["keys"]
        offsets = {}

        for key in keys:
            offsets[key] = committed_offsets[key]

        return {"type": "list_committed_offsets_ok", "offsets": offsets}

    node.run()
