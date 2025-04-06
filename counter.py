#!/usr/bin/env python3

from maelstrom import Node, Body, Request

if __name__ == "__main__":
    node = Node()

    async def write(value: int):
        await node.rpc("seq-kv", {"type": "write", "key": node.node_id, "value": value})

    async def read_value(id) -> int:
        response = await node.rpc("seq-kv", {"type": "read", "key": id})
        await node.log(response)
        return response["value"]

    @node.handler
    async def add(req: Request) -> Body:
        try:
            old_value = await read_value(node.node_id)
        except:
            old_value = 0
        new_value = old_value + req.body["delta"]
        await write(new_value)
        return {"type": "add_ok"}

    @node.handler
    async def read(req: Request) -> Body:
        counter = 0
        for id in node.node_ids:
            counter += await read_value(id)
        return {"type": "read_ok", "value": counter}
    
    node.run()