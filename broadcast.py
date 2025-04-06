#!/usr/bin/env python3

from maelstrom import Body, Node, Request
import asyncio
from collections import defaultdict

if __name__ == "__main__":
    node = Node()
    messages = set()
    neighbors: dict[str, list[str]] = {}
    backlog: dict[str, list[str]] = defaultdict(list)


    async def send_propogation_request(message, neighbor):
        backlog[neighbor].append(message)
        response = await node.rpc(neighbor, {"type": "propogate", "messages": backlog[neighbor]})
        if response.get("type") != "error":
            backlog[neighbor] = []


        
    @node.handler
    async def propogate(req: Request) -> Body:
        req_messages = req.body["messages"]

        for message in req_messages:
            if message in messages:
                  continue
            messages.add(message)
            await asyncio.gather(
            *[
                send_propogation_request(message, neighbor)
                for neighbor in neighbors.get(node.node_id, []) if neighbor != req.src
            ]
            )
        return {"type": "propogate_ok"}


    @node.handler
    async def broadcast(req: Request) -> Body:
        message = req.body["message"]
        if message not in messages:
            messages.add(message)
            await asyncio.gather(
            *[
                send_propogation_request(message, neighbor)
                for neighbor in neighbors.get(node.node_id, []) if neighbor != req.src
            ]
            )
        return {"type": "broadcast_ok"}

    @node.handler
    async def read(req: Request) -> Body:
        return {"type": "read_ok", "messages": list(messages)}

    @node.handler
    async def topology(req: Request) -> Body:
        global neighbors
        neighbors = req.body["topology"]
        return {"type": "topology_ok"}
    
    node.run()
