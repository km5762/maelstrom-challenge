#!/usr/bin/env python3

from maelstrom import Body, Node, Request

if __name__ == "__main__":
    node = Node()
    messages = set()
    neighbors: list[str] = []

    @node.handler
    async def broadcast(req: Request) -> Body:
        messages.add(req.body["message"])
        for neighbor in neighbors:
            await node.rpc(neighbor, {"type": "broadcast", "message": req.body["message"]})
        return {"type": "broadcast_ok"}

    @node.handler
    async def read(req: Request) -> Body:
        return {"type": "read_ok", "messages": list(messages)}

    @node.handler
    async def topology(req: Request) -> Body:
        global neighbors
        neighbors = req.body["topology"].get(node.node_id, [])
        return {"type": "topology_ok"}
    
    node.run()
