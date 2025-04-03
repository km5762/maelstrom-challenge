#!/usr/bin/env python3

from maelstrom import Node, Body, Request

if __name__ == "__main__":
    node = Node()

    @node.handler
    async def echo(req: Request) -> Body:
        return {"type": "echo_ok", "echo": req.body["echo"]}

    node.run()