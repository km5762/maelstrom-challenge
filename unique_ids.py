#!/usr/bin/env python3

from maelstrom import Body, Node, Request

if __name__ == "__main__":
    node = Node()
    i = 0

    @node.handler
    async def generate(req: Request) -> Body:
        global i
        i += 1
        return {"type": "generate_ok", "id": f"{node.node_id},{i}"}

    node.run()